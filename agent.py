from tavily import TavilyClient
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import Annotated
import asyncio
from datetime import datetime
from dataclasses import dataclass, field
from langchain_community.document_loaders import WebBaseLoader
import re
from pydantic_graph import Graph, BaseNode, GraphRunContext, End
from agent_tools import get_source_url, web_scraper, python_execution_tool, generate_and_save_image, generate_powerpoint_slides, graph_generator, get_column_list, get_column_description, extract_pptx_structure
import os
from io import StringIO
from contextlib import redirect_stdout
import logfire


load_dotenv()

logfire.configure(token=os.getenv('LOGFIRE_TOKEN'), scrubbing=False)
model_planner = OpenAIModel('gpt-4.1', provider=OpenAIProvider(api_key=os.getenv('OPENAI_API_KEY')))
model_content = OpenAIModel('gpt-4.1', provider=OpenAIProvider(api_key=os.getenv('OPENAI_API_KEY')))
model_editor = OpenAIModel('gpt-4.1', provider=OpenAIProvider(api_key=os.getenv('OPENAI_API_KEY')))



# slide format
class SlideFormat(BaseModel):
    title: str = Field(default="", description="The title of the slide")
    text_content: str = Field(default="", description="The text content of the slide")
    bullets: list[str] = Field(default_factory=list, description="The bullets of the slide")
    image_path: str = Field(default="", description="The path of the image to be displayed on the slide, empty if no image is required, if image is required, use the generate_and_save_image tool to generate the image and save it to the current directory")
    graph_path: str = Field(default="", description="The path of the graph to be displayed on the slide, empty if no graph is required, if graph is required, use the graph_generator tool to generate the graph and save it to the current directory")
    table_data: dict[str, list[float]] = Field(default_factory=dict, description="The table data of the slide, empty if no table is required")

@dataclass
class State:
    user_query: str = field(default_factory=str)
    context: str = field(default_factory=str)
    current_date: str = field(default_factory=str)
    sections: list[str] = field(default_factory=list)
    instructions: list[str] = field(default_factory=list)
    presentation_slides: list[SlideFormat] = field(default_factory=list)
    complete_presentation_path: str = field(default="")
    presentation_content: list[SlideFormat] = field(default_factory=list)
    csv_path: str = field(default="")
    instruction: str = field(default="")
    slide_name_with_number: list[str] = field(default_factory=list)
    



# Building intro Agent

class PlannerAgentOutput(BaseModel):
    sections: list[str] = Field(description="The sections planned for the presentation")
    instructions: list[str] = Field(description="The instructions for the next agent for each section")


planner_agent = Agent(
    model=model_planner,
    deps_type=State,
    output_type=PlannerAgentOutput,
    tools=[Tool(get_column_list, takes_ctx=False), Tool(get_column_description, takes_ctx=False)],
    instrument=True
)

@planner_agent.system_prompt
async def get_planner_agent_system_prompt(ctx: RunContext[State]):
    prompt = f"""
    You are a helpful assistant who is a presentation writer and planner.
    Your goal is to plan the slides of the presentation and provide the instructions for the next agent for each slide.

    **Instructions:**
    - Analyse the user query and the context provided by the user.
    - Decide the title of the presentation.
    - Plan the slides of the presentation such as Introduction, <slide_name>, <slide_name>, ..., Conclusion etc. in a maximum of 5 to 7 slides depending on the complexity of the topic.
    - Provide the instructions for the next agent for each slide like search <slide_name> for more information and write introduction for the slide in tone ...., write the content of the slide in tone ...., write the conclusion for the slide in tone ...., etc.

    **Input Data:**
    - User Query: {ctx.deps.user_query}\n
    - Current Date: {ctx.deps.current_date}\n
    - External Context: {ctx.deps.context}\n
    
    Optional csv file path: {ctx.deps.csv_path}\n , no csv file available if not provided by the user.

    **Instructions for the next agent:**
    - Use the get_column_list tool to get the column list from the csv file if provided.
    - Use the get_column_description tool to get the description of the column if provided.
    - Plan the slides and give instructions to the next agent for each slide. The instruction may include stpes like "generate image for the slide", "generate graph for the slide", "generate table for the slide", "perform research from internet" etc.
    - The instructions should be specific and detailed.
    
    Think step by step.
    
    """
    return prompt

# Slide Agent

class SlideAgentOutput(BaseModel):
    slide: SlideFormat = Field(description="The content of the slide")
    summary: str = Field(description="The summary of the slide and instruction for the next slide, like what has been done and what to do next")
    references: list[str] = Field(description="The references of the slide")
    slide_name_with_number: str = Field(description="The name of the slide with the number of the slide saved as <slide_name>_<slide_number>.pptx")

slide_agent = Agent(
    model=model_content,
    tools=[Tool(get_source_url, takes_ctx=False), 
           Tool(web_scraper, takes_ctx=False), 
           Tool(python_execution_tool, takes_ctx=False), 
           Tool(generate_and_save_image, takes_ctx=False),
           Tool(graph_generator, takes_ctx=False), 
           Tool(get_column_list, takes_ctx=False), 
           Tool(get_column_description, takes_ctx=False),
           Tool(extract_pptx_structure, takes_ctx=False),
           Tool(generate_powerpoint_slides, takes_ctx=False)],
    deps_type=State,
    output_type=SlideAgentOutput,
    instrument=True
)

@slide_agent.system_prompt
async def get_slide_agent_system_prompt(ctx: RunContext[State]):
    
    prompt = f"""
    You are an expert business analyst who is proficient in generating slide decks based on given instructions and context.
    Your goal is to generate the content and the powerpoint slide itself using pyhton pptx library and python code using the tools provided and keep track of the content and the slide generated for the deck.

    Here are the instructions provided by the previous agent:
    - User Query (IMPORTANT):\n {ctx.deps.user_query}
    - External Context:\n {ctx.deps.context} \n
    - Instructions:\n {ctx.deps.instructions} \n
    - Optional csv file path: {ctx.deps.csv_path}\n , no csv file available if not provided by the user.
    
    
    Tools available:
    - get_column_list: to get the column list from the csv file if provided.
    - get_column_description: to get the description of the column if provided.
    - get_source_url: to get the source urls for the query for research and data gathering.
    - web_scraper: to get the content of the urls for research and data gathering.
    - python_execution_tool: to execute the python code for analysis, generating metrics, tables etc.
    - generate_and_save_image: to generate the image and save it to the current directory if required. Use this tool only if the slide requires an image. IMPORTANT: Use this tool only once per slide and always store png images.
    - graph_generator: to generate the graph and save it to the current directory if required. Use this tool only if the slide requires a graph.
    - generate_powerpoint_slides: to generate the powerpoint slides and save it to the current directory. IMPORTANT: import the necessary libraries such as stringio, redirect_stdout, in the code.
    - extract_pptx_structure: to extract the structure of the powerpoint slides and use template to replace the placeholders with the data in the slides.
    
    
    Instructions for content generation:
    - Follow the instructions provided by the previous agent strictly.
    - Use the relevant tools to generate the slide content based on the instructions and context provided by the previous agent.
    - Keep the record of the path of images and graphs generated using the generate_and_save_image and graph_generator tools.
    - Generate the slide content based on the instructions and context provided by the previous agent and return the output in json format as per the SlideFormat schema.
    - Do not forget to include the reference to the image path and graph path in the slide content so that the presentation agent can include it in the presentation.
    - Keep the content of the slide concise and to the point so that it fits easily in a single slide.
    
   
    Steps to follow for execution:
    - Use the extract_pptx_structure tool to study the template.pptx file.
    - Pick the rellevant slide number for the slide for example if slide content is introduction then pick the slide with introduction from the template.pptx.
    - Write the pyhton code using pyhton pptx library to copy the relevant slides from the template.pptx and replace the placeholders with the data in the slides. Use the generate_powerpoint_slides tool to generate the powerpoint slides and save it to the current directory. IMPORTANT: import the necessary libraries such as stringio, redirect_stdout, in the code.
    - Save the generated powerpoint slides to the current directory as <presentation_name>.pptx and print the path of the generated powerpoint slides.
    - Keep the record of the path of the generated powerpoint slides.
    
    Extra instructions:
    - Study the presentation content format
    - Plan out the slide and content layout:
        Slide layout:
        - Header: The title of the slide
        - Left Content: The text content of the slide or bullet points
        - Right Content: The image or graph or table of the slide generated by the generate_and_save_image and graph_generator tools
        - Layout: Landscape
    - Important step: The template is stored as template.pptx, use extract_pptx_structure tool to extract the structure of the powerpoint slides and use template to replace the placeholders with the data in the slides.
    - Pick the relevant slides from the template to insert the data in the slides using the generate_powerpoint_slides tool. Use the generate_powerpoint_slides tool to generate the powerpoint slides and save it to the current directory. IMPORTANT: import the necessary libraries such as stringio, redirect_stdout, in the code.
    - Important: Do not forget to include the images on the slides generated by the generate_and_save_image and graph_generator tools.
    - Note: Use font size 24 for the title, 16 for the text content and 14 for the bullet points.
    
    Note: Keep the content of the slide concise and to the point so that it fits easily in a single slide.
    
    Think step by step.
    
    """
    return prompt



# Editor Agent

@dataclass
class PresentationAgentOutput(BaseModel):
    complete_presentation_path: str = Field(default_factory=str, description="path where presentation is saved")
    summary: str = Field(description="The summary of the presentation")

presentation_agent = Agent(
    model=model_editor,
    deps_type=State,
    output_type=PresentationAgentOutput,
    tools=[Tool(generate_powerpoint_slides, takes_ctx=False)],
    instrument=True
)
    # Format blog content sections
@presentation_agent.system_prompt
async def get_presentation_agent_system_prompt(ctx: RunContext[State]):
    presentation_content_formatted = ""
    for i, slide in enumerate(ctx.deps.presentation_slides):
        presentation_content_formatted += f"\nSlide {i+1}:\n"
        presentation_content_formatted += f"Title: {slide.title}\n"
        presentation_content_formatted += f"Text Content: {slide.text_content}\n"
        if slide.bullets:
            presentation_content_formatted += f"Bullets: {', '.join(slide.bullets)}\n"
        if slide.image_path:
            presentation_content_formatted += f"Image Path: {slide.image_path}\n"
        if slide.graph_path:
            presentation_content_formatted += f"Graph Path: {slide.graph_path}\n"
        if slide.table_data:
            presentation_content_formatted += f"Table Data: {slide.table_data}\n"
        presentation_content_formatted += "\n"

    prompt = f"""
    You are a presentation editor who edits the presentation based on the instructions and all the slides of the presentation provided by the previous agent.
    
    you will be provided with the slide name and number, write python code to merge the slides into a single powerpoint presentation. If needed add some complementary slides.

    Here are the instructions, keypoints, title, slides and conclusion provided by the previous agent:
    - User Query:\n {ctx.deps.user_query}
    - ExternalContext:\n {ctx.deps.context}
    - Presentation Content:\n {presentation_content_formatted}
    - Slide Name with Number:\n {str(ctx.deps.slide_name_with_number)}
    \n\n
    
    Tools available:
    - generate_powerpoint_slides: to generate the powerpoint slides and save it to the current directory. IMPORTANT: import the necessary libraries such as stringio, redirect_stdout, in the code.
    
    Steps to follow:
    - write python code to merge the slides into a single powerpoint presentation. If needed add some complementary slides.
    
    return the final powerpoint slide name with the path.
    
   Think step by step.

   """
    return prompt

# Graph Orchestration

@dataclass
class PlannerAgentNode(BaseNode[State]):
    """
    Planning the slides of the presentation
    """
    async def run(self, ctx: GraphRunContext[State]) -> "SlideAgentNode":
        user_query = ctx.state.user_query
        context = ctx.state.context
        current_date = datetime.now().strftime("%Y-%m-%d")
        ctx.state.current_date = current_date
        response = await planner_agent.run(user_query, deps=ctx.state)
        response_data = response.output
        ctx.state.sections = response_data.sections
        ctx.state.instructions = response_data.instructions
        # for debugging
        print(f'\n\n Sections: {ctx.state.sections}\n\n')
        print(f'\n\n Instructions: {ctx.state.instructions}\n\n')
        return SlideAgentNode()
    

@dataclass
class SlideAgentNode(BaseNode[State]):
    """
    Generating slides for the presentation
    """
    async def run(self, ctx: GraphRunContext[State]) -> "PresentationAgentNode":
        i = 1
        for section, instruction in zip(ctx.state.sections, ctx.state.instructions):
            ctx.state.instruction = instruction
            query = f"For user query: {ctx.state.user_query}, generate the slide content for the section: {section} with the instructions: {instruction}"
            response = await slide_agent.run(query, deps=ctx.state)
            response_data = response.output
            
            # Add the slide to the presentation
            ctx.state.presentation_slides.append(response_data.slide)
            ctx.state.slide_name_with_number.append(f"slide for section {section}, slide number {i} saved as {response_data.slide_name_with_number}.pptx")
            i += 1
            
            # for debugging
            print(f'\n\n Slide {len(ctx.state.presentation_slides)}: {response_data.slide.title}\n\n')
            print(f'\n\n Summary: {response_data.summary}\n\n')

        return PresentationAgentNode()
    

@dataclass
class PresentationAgentNode(BaseNode[State]):
    """
    Generating the final presentation
    """
    async def run(self, ctx: GraphRunContext[State]) -> "End":
        user_query = ctx.state.user_query
        response = await presentation_agent.run(user_query, deps=ctx.state)
        response_data = response.output
        ctx.state.complete_presentation_path = response_data.complete_presentation_path

        # for debugging
        print(f'\n\n Complete Presentation Path: {ctx.state.complete_presentation_path}\n\n')
        return End(ctx.state)


def run_full_agent(user_query: str, user_id: str = "123", context: str = "", csv_path: str = ""):
    """Synchronous version to run the full presentation generation agent"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    state = State(user_query=user_query, current_date=current_date, context=context, csv_path=csv_path)
    graph = Graph(nodes=[PlannerAgentNode, SlideAgentNode, PresentationAgentNode])
    result = graph.run_sync(PlannerAgentNode(), state=state)
    result = result.output
    
    return result

async def run_full_agent_async(user_query: str, user_id: str = "123", context: str = "", csv_path: str = ""):
    """Async version of run_full_agent that properly handles async operations"""
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    state = State(user_query=user_query, current_date=current_date, context=context, csv_path=csv_path)
    graph = Graph(nodes=[PlannerAgentNode, SlideAgentNode, PresentationAgentNode])
    result = await graph.run(PlannerAgentNode(), state=state)
    result = result.output
    
    return result

async def main():
    user_prompt = "Generate a presentation on special theory of relativity"
    result = await run_full_agent_async(user_prompt)
    print('\n\n\n')
    print(f'Presentation Path: {result.complete_presentation_path}')
    print(f'Total Slides: {len(result.presentation_slides)}')
    print('\n\n\n')

if __name__ == "__main__":
    asyncio.run(main())
