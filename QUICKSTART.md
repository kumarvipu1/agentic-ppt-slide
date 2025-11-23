# 🚀 Quick Start Guide

## Get Started in 3 Minutes!

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
GOOGLE_GENAI_KEY=...
TAVILY_API_KEY=...
LOGFIRE_TOKEN=...
```

### 3. Run the App

**Windows:**
```bash
run_app.bat
```

**Mac/Linux:**
```bash
chmod +x run_app.sh
./run_app.sh
```

**Or manually:**
```bash
streamlit run app.py
```

### 4. Use the Interface

1. Open browser at `http://localhost:8501`
2. Enter your presentation topic
3. Click "Generate Presentation"
4. Wait 2-5 minutes
5. Download your PowerPoint!

---

## Example Topics

Try these sample queries:

- "Generate a presentation on artificial intelligence and its applications"
- "Create a business pitch for a new mobile app"
- "Develop educational slides on photosynthesis"
- "Build a marketing deck for a sustainable fashion brand"

---

## Need Help?

- **Check logs**: Streamlit shows errors in the terminal
- **API issues**: Verify your keys in `.env`
- **Slow generation**: First run takes longer (AI warmup)
- **Can't install**: Make sure Python 3.10+ is installed

---

## What's Happening Behind the Scenes?

1. **Planning Agent**: Analyzes your topic and plans slide structure
2. **Slide Agent**: Generates content for each slide
3. **Presentation Agent**: Creates the PowerPoint file

All powered by AI! 🤖✨

---

Enjoy creating amazing presentations! 🎉

