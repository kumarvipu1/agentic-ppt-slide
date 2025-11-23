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
from google import genai
from google.genai import types
from PIL import Image
from dataclasses import dataclass, field
from langchain_community.document_loaders import WebBaseLoader
import re
from io import StringIO
from contextlib import redirect_stdout
from pydantic_graph import Graph, BaseNode, GraphRunContext, End
import os


load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_GENAI_KEY"))


# Tools

# to get the source urls for the final blog
def get_source_url(query: Annotated[str, "The query to search for"]) -> str:
    """Use this tool to get source urls for the query. Later you can use the web_scraper tool to get the content of the urls."""

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    results = client.search(query=query, max_results=4, search_depth="advanced")
    scores = [result['score'] for result in results['results']]
    urls = [result['url'] for result in results['results']]
    images = results['images'][:len(urls)]
    
    return f"Urls:\n{str(urls)}"

# to get the content of the urls
def web_scraper(urls: Annotated[list, "The urls to scrape for more information and data for writing the blog."],
                length: Annotated[int, "The length of the content to scrape"] = 3000) -> str:
    """Pass one url as a string to get more information and data for writing the blog."""
    
    words_per_url = length // len(urls)  # Distribute words evenly across URLs
    text_data = ""
    
    for url in urls:
        try:
            loader = WebBaseLoader(url)
            data = loader.load()
            
            for doc in data:
                # Remove HTML/XML tags first
                content = re.sub(r'<[^>]+>', '', doc.page_content)
                
                # Split into paragraphs
                paragraphs = content.split('\n')
                clean_paragraphs = []
                
                for p in paragraphs:
                    # Remove special characters and normalize spaces
                    cleaned = re.sub(r'[^\w\s]', '', p)  # Keep only alphanumeric and spaces
                    cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normalize to single spaces
                    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned)  # Remove non-English characters
                    
                    # Only keep paragraphs relevant to the query
                    if len(cleaned.split()) > 10 and cleaned:
                        clean_paragraphs.append(cleaned)
                
                filtered_content = ' '.join(clean_paragraphs)  # Join all paragraphs into single text
                final_content = ' '.join(filtered_content.split()[:words_per_url])  # Take exact number of words needed
                    
                title = doc.metadata.get("title", "")
                text_data += f'{title}\n{final_content}\n\n'
        except:
            return f"Error scraping {url}."
    
    return f"Data from the urls:\n{str(urls)}\n\n{text_data}"



# to generate the images for the blog

def generate_and_save_image(prompt: Annotated[str, "The prompt to generate the image"], 
                            filename: Annotated[str, "The filename to save the image"],
                            aspect_ratio: Annotated[str, "The aspect ratio of the image"] = '1:1', 
                            image_size: Annotated[str, "The size of the image"] = '1K'):
    """
    Generate an image using Gemini API and save it as PNG. Use 1:1 aspect ratio and 1K size for the image as default
    
    Args:
        prompt: Text description of the image to generate
        filename: Output filename (default: "generated_image.png")
        aspect_ratio: Image aspect ratio - "1:1", "2:3", "3:2", "4:3", "16:9" (default: '1:1' for model default)
        image_size: Image size - "1K", "2K", "4K" (default: '1K' for model default)
    
    """
    import io
    
    # Build config if size/aspect ratio specified
    config = None
    if aspect_ratio or image_size:
        try:
            config = types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio or "1:1",
                    image_size=image_size or "1K"
                )
            )
        except AttributeError:
            print("⚠ ImageConfig not available. Run: pip install --upgrade google-genai")
            print("  Generating with default settings...")
    
    # Generate image
    if config:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview", 
            contents=[prompt],
            config=config
        )
    else:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image", 
            contents=[prompt]
        )
    
    # Extract and save image
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            image_data = part.inline_data.data
            
            # Save as PNG
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            # Load and return image
            img = Image.open(io.BytesIO(image_data))
            print(f"Saved with filename: {filename} ({len(image_data):,} bytes, {img.size[0]}x{img.size[1]})")
            return f"The image is saved with filename: {filename} ({len(image_data):,} bytes, {img.size[0]}x{img.size[1]}, aspect ratio: {aspect_ratio})"
    
    raise ValueError("No image data found in response")


# Generating the graph
def graph_generator(
    code: Annotated[str, "The python code to execute to generate visualizations"]
) -> str:
    """
    Use this tool to generate graphs and visualizations using python code.

    Print the graph path in html and png format in the following format:
    'The graph path in html format is <graph_path_html> and the graph path in png format is <graph_path_png>'.

    """

    
    catcher = StringIO()

    try:
        with redirect_stdout(catcher):
            # The compile step can catch syntax errors early
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code, globals(), globals())

            return (
                f"The graph path is \n\n{catcher.getvalue()}\n"
                f"Proceed to the next step"
            )

    except Exception as e:
        return f"Failed to run code. Error: {repr(e)}, try a different approach"

    

# Executing the python code
def python_execution_tool(
    code: Annotated[str, "The python code to execute for calculations and data processing"]
) -> str:
    """
    Use this tool to run python code for calculations, data processing, and metric computation.

    Always use print statement to print the result in format:
    'The calculated value for <variable_name> is <calculated_value>'.

    """
    
    catcher = StringIO()

    try:
        with redirect_stdout(catcher):
            # The compile step can catch syntax errors early
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code, globals(), globals())

            return (
                f"The calculated value is \n\n{catcher.getvalue()}\n"
                f"Make sure to include this value in the report\n"
            )

    except Exception as e:
        return f"Failed to run code. Error: {repr(e)}, try a different approach"
    
    

# Executing the python code for generating powerpoint slides
def generate_powerpoint_slides(
    code: Annotated[str, "The python code to execute for generating powerpoint slides using py-pptx library"],
    filename: Annotated[str, "The filename to save the powerpoint slides in format <filename>.pptx"]
) -> str:
    """
    Use this tool to run python code for generating powerpoint slides using py-pptx library.

    Always use print statement to print the result in format:
    'The powerpoint slides are generated and saved as <filename>.pptx'. Make sure to include the filename in the print statement.
    
    Remember to import the necessary libraries such as stringio, redirect_stdout, etc.

    """
    
    catcher = StringIO()

    try:
        with redirect_stdout(catcher):
            # The compile step can catch syntax errors early
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code, globals(), globals())

            return (
                f"The powerpoint slides are generated and saved as {filename}\n"
            )

    except Exception as e:
        return f"Failed to run code. Error: {repr(e)}, try a different approach"
    
    
def get_column_list(
    file_name: Annotated[str, "The name of the csv file that has the data"]
):
    """
    Use this tool to get the column list from the CSV file.
    
    Parameters:
    - file_name: The name of the CSV file that has the data
    """
    df = pd.read_csv(file_name)
    columns = df.columns.tolist()
    return str(columns)

# Getting the description of the column
def get_column_description(
    column_dict: Annotated[dict, "The dictionary of the column name and the description of the column"]
):
    """
    Use this tool to get the description of the column.
    """
    
    return str(column_dict)
