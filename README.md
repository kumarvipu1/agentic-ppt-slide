# 📊 AI Presentation Generator

> Transform your ideas into professional PowerPoint presentations using AI-powered agents

An intelligent presentation generation system that uses multiple AI agents to plan, research, and create comprehensive slide decks automatically. Built with cutting-edge AI models and a modern Streamlit interface.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)

---

## 🌟 Features

### 🤖 Multi-Agent Architecture
- **Planner Agent**: Analyzes your topic and creates a structured outline
- **Slide Agent**: Generates detailed content for each slide with research
- **Presentation Agent**: Compiles everything into a polished PowerPoint

### 🎨 Rich Content Generation
- 📝 Text content with bullet points
- 🖼️ AI-generated images using Google Gemini
- 📊 Data visualizations and graphs
- 📈 Tables from CSV data
- 🔍 Web research integration
- 📚 Source citation

### 💻 Modern Web Interface
- Clean, minimal Streamlit UI
- Real-time progress tracking
- Async operation handling
- CSV data upload
- Instant download
- Debug mode for development

### 🔧 Powerful Tools
- **Web Search**: Tavily-powered research
- **Web Scraping**: Content extraction from URLs
- **Python Execution**: Dynamic data analysis
- **Image Generation**: AI-powered visuals
- **Graph Generation**: Matplotlib charts
- **CSV Processing**: Data-driven insights

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- API Keys:
  - [OpenAI API](https://platform.openai.com/api-keys)
  - [Google Gemini](https://makersuite.google.com/app/apikey)
  - [Tavily Search](https://tavily.com/)
  - [Logfire](https://logfire.pydantic.dev/)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/slide-generator.git
cd slide-generator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_GENAI_KEY=your_google_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LOGFIRE_TOKEN=your_logfire_token_here
```

> 💡 **Tip**: Copy `config.example.env` to `.env` and fill in your keys

4. **Launch the application**

```bash
streamlit run app.py
```

5. **Open your browser** to `http://localhost:8501`

---

## 📖 Usage

### Basic Workflow

1. **Enter Your Topic**
   ```
   Example: "Generate a presentation on renewable energy solutions"
   ```

2. **Add Context (Optional)**
   ```
   Example: "Focus on solar and wind power, include recent statistics"
   ```

3. **Upload CSV Data (Optional)**
   - Upload data files for charts and tables
   - System will automatically visualize the data

4. **Click Generate**
   - Wait 2-5 minutes for AI to work its magic
   - Watch the progress bar for real-time updates

5. **Download Your Presentation**
   - Get a professional PowerPoint file
   - Ready to present or customize further

### Example Queries

```
✅ "Create a business pitch deck for a SaaS startup"
✅ "Generate educational slides on quantum computing"
✅ "Build a marketing presentation for eco-friendly products"
✅ "Develop a technical overview of machine learning algorithms"
✅ "Make a sales presentation for our Q4 results"
```

---

## 🏗️ Project Structure

```
slide-generator/
├── app.py                    # Streamlit web interface
├── agent.py                  # Multi-agent orchestration
├── agent_tools.py            # Tool implementations
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── config.example.env        # Example environment config
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── README.md                # This file
├── README_STREAMLIT.md      # Detailed UI documentation
└── QUICKSTART.md            # Quick setup guide
```

### Key Components

**`agent.py`** - Core Agent System
- `SlideFormat`: Pydantic model for slide structure
- `State`: Dataclass managing agent state
- `PlannerAgentNode`: Plans presentation structure
- `SlideAgentNode`: Generates individual slides
- `PresentationAgentNode`: Creates final PowerPoint

**`agent_tools.py`** - Tool Library
- `get_source_url()`: Web search for research
- `web_scraper()`: Extract content from URLs
- `python_execution_tool()`: Run Python code
- `generate_and_save_image()`: AI image generation
- `graph_generator()`: Create charts and graphs
- `generate_powerpoint_slides()`: Build PowerPoint files
- `get_column_list()`: CSV data processing
- `get_column_description()`: Data analysis

**`app.py`** - Web Interface
- Modern Streamlit UI
- Async operation handling
- Progress tracking
- File upload/download
- Session management

---

## ⚙️ Configuration

### Model Configuration

Edit `agent.py` to customize AI models:

```python
model_planner = OpenAIModel('gpt-4.1', provider=OpenAIProvider(...))
model_content = OpenAIModel('gpt-4.1', provider=OpenAIProvider(...))
model_editor = OpenAIModel('gpt-4.1', provider=OpenAIProvider(...))
```

### Streamlit Theme

Customize in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
textColor = "#2C3E50"
```

### Agent Behavior

Modify system prompts in `agent.py` to change:
- Tone and style
- Slide structure preferences
- Content depth
- Visual preferences

---

## 🎯 Advanced Usage

### Programmatic Access

Use the agents directly in your Python code:

```python
from agent import run_full_agent_async
import asyncio

async def generate_presentation():
    result = await run_full_agent_async(
        user_query="Generate a presentation on AI ethics",
        user_id="user123",
        context="Include real-world examples",
        csv_path="data.csv"  # optional
    )
    
    print(f"Presentation saved: {result.complete_presentation_path}")
    print(f"Total slides: {len(result.presentation_slides)}")

asyncio.run(generate_presentation())
```

### Custom Tools

Add custom tools in `agent_tools.py`:

```python
def my_custom_tool(param: str) -> str:
    """Description for the AI agent"""
    # Your implementation
    return result

# Register in agent.py
slide_agent = Agent(
    tools=[..., Tool(my_custom_tool, takes_ctx=False)],
    ...
)
```

### CSV Data Integration

Upload CSV files to automatically:
- Generate charts and graphs
- Create data tables
- Extract insights
- Visualize trends

---

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

**API Key Errors**
- Verify `.env` file exists in project root
- Check for typos in API keys
- Ensure no extra spaces or quotes
- Test keys individually

**Streamlit Won't Start**
```bash
# Try different port
streamlit run app.py --server.port 8502

# Clear cache
streamlit cache clear
```

**Generation Fails**
- Check internet connection
- Verify all API keys are valid
- Enable debug mode in UI
- Check terminal for error details

**Slow Performance**
- First run takes longer (model loading)
- Complex topics need more time
- Consider using faster models
- Check API rate limits

### Debug Mode

Enable in the Streamlit sidebar:
1. Click "Advanced Options"
2. Check "Show debug information"
3. Generate presentation
4. View detailed error messages

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 minutes
- **[README_STREAMLIT.md](README_STREAMLIT.md)** - Detailed UI guide
- **API Docs** - Coming soon

---

## 🛣️ Roadmap

- [ ] Multi-language support
- [ ] Custom templates
- [ ] Collaborative editing
- [ ] Export to PDF/Google Slides
- [ ] Voice narration generation
- [ ] Animation presets
- [ ] Theme customization
- [ ] API endpoints
- [ ] Docker deployment
- [ ] Cloud storage integration

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Commit with clear messages**
   ```bash
   git commit -m "Add amazing feature"
   ```
5. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Lint
flake8 .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** - GPT models for content generation
- **Google** - Gemini for image generation
- **Tavily** - Web search capabilities
- **Streamlit** - Beautiful web interface
- **pydantic-ai** - Agent framework
- **python-pptx** - PowerPoint generation

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kumarvipu1/agentic-ppt-slide/issues)
- **Email**: [Email](kumar.vkumar.vipul5@gmail.com)

---

## 💡 Tips for Best Results

1. **Be Specific**: Clear topics yield better presentations
2. **Add Context**: Help the AI understand your needs
3. **Use Data**: CSV files enhance credibility
4. **Review Output**: Always customize for your audience
5. **Iterate**: Try different phrasings if needed

---

## 🌟 Star History

If you find this project helpful, please consider giving it a star ⭐

---

<div align="center">

**[Documentation](README_STREAMLIT.md)** • **[Quick Start](QUICKSTART.md)** • **[Report Bug](https://github.com/kumarvipu1/agentic-ppt-slide/issues)** • **[Request Feature](https://github.com/kumarvipu1/agentic-ppt-slide/issues)**


</div>

