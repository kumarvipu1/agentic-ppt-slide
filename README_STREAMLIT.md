# 📊 AI Presentation Generator - Streamlit UI

A modern, minimal web interface for generating professional presentations using AI.

## 🚀 Features

- **Modern UI**: Clean and intuitive interface built with Streamlit
- **Real-time Progress**: Live status updates and progress bars during generation
- **Async Operations**: Efficient handling of long-running AI operations
- **CSV Upload**: Optional data file upload for data-driven presentations
- **Instant Download**: Download generated presentations directly from the browser
- **Customizable**: Add context and specific requirements for better results

## 📋 Prerequisites

- Python 3.10 or higher
- Required API keys:
  - OpenAI API key
  - Google Gemini API key
  - Tavily API key
  - Logfire token

## 🛠️ Installation

1. **Clone the repository** (if not already done):
```bash
git clone <your-repo-url>
cd slide-generator
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:

Create a `.env` file in the root directory with the following:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_GENAI_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LOGFIRE_TOKEN=your_logfire_token_here
```

## 🎯 Usage

### Running the Streamlit App

Start the application with:

```bash
streamlit run app.py
```

The app will open automatically in your default browser at `http://localhost:8501`

### Using the Interface

1. **Enter your topic**: Describe the presentation you want to generate
2. **Add context** (optional): Provide additional details or requirements
3. **Upload CSV** (optional): Include data for charts and tables
4. **Click Generate**: Wait for the AI to create your presentation
5. **Download**: Get your PowerPoint file when complete

### Example Queries

- "Generate a presentation on climate change impacts and solutions"
- "Create a business pitch deck for a SaaS startup"
- "Develop educational slides on quantum computing basics"
- "Build a marketing presentation for a new product launch"

## 📊 Features Breakdown

### Progress Tracking
- **Step 1**: Planning presentation structure
- **Step 2**: Generating slide content with AI
- **Step 3**: Creating PowerPoint file

### Advanced Options
- **Debug Mode**: See detailed error information
- **User ID**: Track different users or sessions
- **Auto Download**: Automatically download when complete

### Data Upload
- Upload CSV files to include charts, graphs, and tables
- Preview data before generating
- Automatic data visualization

## 🎨 UI Customization

The app uses custom CSS for a modern look. You can customize colors and styles by editing the `st.markdown()` section in `app.py`.

## 📁 Output

Generated presentations are saved with timestamps:
- Format: `presentation_YYYYMMDD_HHMMSS.pptx`
- Location: Current directory (temporary)
- Auto-cleaned after download

## ⚙️ Configuration

### Streamlit Settings

Edit `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8F9FA"
textColor = "#2C3E50"
font = "sans serif"

[server]
port = 8501
maxUploadSize = 200
```

## 🐛 Troubleshooting

### Common Issues

**"Module not found" error**:
```bash
pip install -r requirements.txt --upgrade
```

**API key errors**:
- Check your `.env` file exists
- Verify all API keys are valid
- Ensure no extra spaces in the `.env` file

**Streamlit not starting**:
```bash
streamlit run app.py --server.port 8502
```

**Async errors**:
- Make sure you're using Python 3.10+
- Check that asyncio is properly installed

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit Cloud dashboard
5. Deploy!

### Deploy Locally with Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 📝 Notes

- First generation may take 2-5 minutes depending on complexity
- Larger presentations (7+ slides) take longer
- CSV files should be well-formatted with headers
- Internet connection required for AI APIs

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

MIT License - feel free to use and modify as needed.

## 💡 Tips for Best Results

1. Be specific in your topic description
2. Include key points you want covered
3. Add context about your audience
4. Use CSV data for data-driven slides
5. Review and customize downloaded presentations

---

