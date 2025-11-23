import streamlit as st
import asyncio
from datetime import datetime
import os
from pathlib import Path
import time
from agent import run_full_agent_async, State
from io import StringIO
import sys

# Configure Streamlit page
st.set_page_config(
    page_title="Slide Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern minimal design
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .upload-section {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }
    h2, h3 {
        color: #34495e;
        font-weight: 600;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'presentation_path' not in st.session_state:
    st.session_state.presentation_path = None
if 'slides_count' not in st.session_state:
    st.session_state.slides_count = 0

# Header
st.title("📊 AI Presentation Generator")
st.markdown("### Generate professional presentations powered by AI")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # User ID (optional)
    user_id = st.text_input(
        "User ID",
        value="default_user",
        help="Optional identifier for tracking"
    )
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        show_debug = st.checkbox("Show debug information", value=False)
        auto_download = st.checkbox("Auto-download when complete", value=True)
    
    st.markdown("---")
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. Enter your presentation topic
    2. Add context (optional)
    3. Upload CSV data (optional)
    4. Click Generate
    5. Download your presentation
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Be specific with your query
    - Add relevant context for better results
    - CSV files enhance data-driven slides
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Presentation Details")
    
    # User query input
    user_query = st.text_area(
        "What presentation would you like to generate?",
        placeholder="Example: Generate a presentation on climate change impacts and solutions",
        height=120,
        help="Describe the topic and key points you want in your presentation"
    )
    
    # Context input
    context = st.text_area(
        "Additional Context (Optional)",
        placeholder="Add any specific context, requirements, or background information...",
        height=100,
        help="Provide additional details to guide the AI in generating more relevant content"
    )

with col2:
    st.subheader("📁 Data Upload")
    
    # CSV file upload
    uploaded_file = st.file_uploader(
        "Upload CSV (Optional)",
        type=['csv'],
        help="Upload a CSV file to include data visualizations in your presentation"
    )
    
    csv_path = ""
    if uploaded_file is not None:
        # Save uploaded file temporarily
        csv_path = f"temp_{uploaded_file.name}"
        with open(csv_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        # Show preview
        if st.checkbox("Show data preview"):
            import pandas as pd
            df = pd.read_csv(csv_path)
            st.dataframe(df.head(), use_container_width=True)

st.markdown("---")

# Generate button
generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])

with generate_col2:
    generate_button = st.button("🚀 Generate Presentation", type="primary")

# Generation process
if generate_button:
    if not user_query.strip():
        st.error("❌ Please enter a presentation topic before generating!")
    else:
        st.session_state.generated = False
        
        # Create status container
        status_container = st.container()
        
        with status_container:
            # Main status display
            with st.status("🎨 Generating your presentation...", expanded=True) as status:
                try:
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Step 1: Planning
                    status_text.markdown("**Step 1/3:** 🧠 Planning presentation structure...")
                    progress_bar.progress(10)
                    time.sleep(0.5)
                    
                    # Capture output for debugging
                    output_buffer = StringIO()
                    
                    # Run the async function
                    async def generate_with_progress():
                        # Start generation
                        progress_bar.progress(20)
                        status_text.markdown("**Step 1/3:** 🧠 Analyzing topic and planning slides...")
                        
                        # Run the agent
                        result = await run_full_agent_async(
                            user_query=user_query,
                            user_id=user_id,
                            context=context,
                            csv_path=csv_path
                        )
                        
                        return result
                    
                    # Execute async function
                    progress_bar.progress(30)
                    status_text.markdown("**Step 2/3:** ✍️ Generating slide content...")
                    
                    # Run the agent (this will take time)
                    result = asyncio.run(generate_with_progress())
                    
                    progress_bar.progress(70)
                    status_text.markdown("**Step 3/3:** 🎨 Creating PowerPoint presentation...")
                    time.sleep(1)
                    
                    progress_bar.progress(100)
                    status_text.markdown("**✅ Complete!** Presentation generated successfully!")
                    
                    # Store results
                    st.session_state.presentation_path = result.complete_presentation_path
                    st.session_state.slides_count = len(result.presentation_slides)
                    st.session_state.generated = True
                    
                    status.update(label="✅ Presentation generated successfully!", state="complete")
                    
                except Exception as e:
                    progress_bar.progress(100)
                    status.update(label="❌ Generation failed!", state="error")
                    st.error(f"An error occurred: {str(e)}")
                    if show_debug:
                        st.exception(e)
                    st.session_state.generated = False
                
                finally:
                    # Clean up temporary CSV file
                    if csv_path and os.path.exists(csv_path):
                        try:
                            os.remove(csv_path)
                        except:
                            pass

# Display results
if st.session_state.generated and st.session_state.presentation_path:
    st.markdown("---")
    st.markdown("## 🎉 Presentation Ready!")
    
    result_col1, result_col2, result_col3 = st.columns(3)
    
    with result_col1:
        st.metric(
            label="📄 Total Slides",
            value=st.session_state.slides_count
        )
    
    with result_col2:
        st.metric(
            label="📂 File Format",
            value="PowerPoint (.pptx)"
        )
    
    with result_col3:
        if os.path.exists(st.session_state.presentation_path):
            file_size = os.path.getsize(st.session_state.presentation_path) / 1024  # KB
            st.metric(
                label="💾 File Size",
                value=f"{file_size:.1f} KB"
            )
    
    st.markdown("---")
    
    # Download section
    download_col1, download_col2, download_col3 = st.columns([1, 2, 1])
    
    with download_col2:
        if os.path.exists(st.session_state.presentation_path):
            with open(st.session_state.presentation_path, "rb") as file:
                file_data = file.read()
                
                st.download_button(
                    label="📥 Download Presentation",
                    data=file_data,
                    file_name=f"presentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )
        
        if st.button("🔄 Generate New Presentation", use_container_width=True):
            st.session_state.generated = False
            st.session_state.presentation_path = None
            st.session_state.slides_count = 0
            st.rerun()
    
    # Success message
    st.success("✅ Your presentation has been generated successfully! Click the download button above to get your file.")
    
    # Show file path in debug mode
    if show_debug:
        st.info(f"**File saved at:** `{st.session_state.presentation_path}`")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d; padding: 2rem 0;'>"
    "AI Powered Presentation Generator"
    "</div>",
    unsafe_allow_html=True
)

