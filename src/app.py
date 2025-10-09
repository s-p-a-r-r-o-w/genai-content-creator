import streamlit as st
import os
import sys
from dotenv import load_dotenv
import time
import json
from datetime import datetime

# Add src to path for imports
sys.path.append('src')
from workflow import ContentWorkflow
from logger import setup_logger

# Load environment variables
load_dotenv()
logger = setup_logger("streamlit_app")

st.set_page_config(
    page_title="GenAI Content Workflow",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Content Generator")
st.markdown("Transform any topic into engaging LinkedIn content with professional visuals")

# Get API key from environment
openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

# Initialize session state
if "workflow_stats" not in st.session_state:
    st.session_state.workflow_stats = {
        "total_runs": 0,
        "avg_execution_time": 0,
        "style_distribution": {"post": {}, "visual": {}}
    }

# Main interface
st.markdown("---")

# Topic input
topic = st.text_input(
    "📝 Enter your topic:",
    placeholder="e.g., Remote work productivity tips",
    help="Enter any topic you want to create LinkedIn content about"
)

# Sample topics in columns
st.markdown("**💡 Or try these sample topics:**")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤖 AI in Healthcare"):
        topic = "AI in healthcare transformation"
        st.rerun()
    if st.button("🌱 Sustainability"):
        topic = "Sustainable business practices"
        st.rerun()

with col2:
    if st.button("🏠 Remote Work"):
        topic = "Remote work productivity strategies"
        st.rerun()
    if st.button("🚀 Leadership"):
        topic = "Leadership in digital age"
        st.rerun()

with col3:
    if st.button("📊 Digital Transform"):
        topic = "Digital transformation strategies"
        st.rerun()
    if st.button("⚖️ Work-Life Balance"):
        topic = "Work-life balance tips"
        st.rerun()

st.markdown("---")

# Generate button
generate_btn = st.button(
    "🎯 Generate LinkedIn Content",
    type="primary",
    disabled=not (topic and openrouter_key),
    use_container_width=True
)

if not openrouter_key:
    st.error("⚠️ OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file.")

# Output section
if topic:
    st.markdown(f"### 📤 Generated Content for: *{topic}*")
else:
    st.markdown("### 📤 Generated Content")
    
if generate_btn and topic and openrouter_key:
        try:
            logger.info(f"User initiated content generation for topic: {topic}")
            # Initialize workflow
            workflow = ContentWorkflow(openrouter_key)
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🎨 Selecting styles...")
            progress_bar.progress(20)
            time.sleep(0.5)
            
            status_text.text("✍️ Generating blog post...")
            progress_bar.progress(50)
            
            # Run workflow
            result = workflow.run_workflow(topic)
            
            status_text.text("🖼️ Generating visual asset...")
            progress_bar.progress(80)
            time.sleep(0.3)
            
            status_text.text("✅ Complete!")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.success(f"✅ Content generated in {result['execution_time']:.1f} seconds")
            
            # Metrics in a more compact format
            st.info(f"✅ **Generated in {result['execution_time']:.1f}s** | Words: {result['word_count']}")
            
            # Content in two columns
            content_col1, content_col2 = st.columns([3, 2])
            
            with content_col1:
                st.subheader("📝 LinkedIn Post")
                st.text_area(
                    "Ready to copy and paste:",
                    value=result['blog_post'],
                    height=400,
                    key="blog_output"
                )
            
            with content_col2:
                st.subheader("🖼️ Visual Asset")
                
                # Display image with better error handling
                if result.get('image_path') and os.path.exists(result['image_path']):
                    st.image(result['image_path'], caption="AI-Generated LinkedIn Visual", width=400)
                    st.success("✅ Image generated successfully")
                elif result.get('image_url'):
                    try:
                        st.image(result['image_url'], caption="AI-Generated LinkedIn Visual", width=400)
                        st.info("🔗 Image loaded from URL")
                    except:
                        st.warning("⚠️ Image display failed")
                        st.code(result['image_url'])
                else:
                    st.warning("⚠️ Image generation unavailable - content ready for use")
            
            st.markdown("---")
            st.subheader("💾 Download Your Content")
            
            # Prepare export data
            export_data = {
                "topic": topic,
                "generated_at": datetime.now().isoformat(),
                "execution_time": result['execution_time'],

                "word_count": result['word_count'],
                "blog_post": result['blog_post'],
                "image_url": result['image_url'],
                "image_path": result.get('image_path', ''),
                "post_style": "AI-Generated",
                "visual_style": "Professional",

            }
            
            # Download options in columns
            dl_col1, dl_col2, dl_col3 = st.columns(3)
            
            with dl_col1:
                st.download_button(
                    "📄 JSON Format",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"linkedin_content_{topic.replace(' ', '_')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with dl_col2:
                text_export = f"""LINKEDIN CONTENT - {topic.upper()}
{'='*50}

{result['blog_post']}

{'='*50}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Words: {result['word_count']} | Time: {result['execution_time']:.1f}s
Image: {result.get('image_path', 'N/A')}
"""
                st.download_button(
                    "📝 Text Format",
                    data=text_export,
                    file_name=f"linkedin_post_{topic.replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with dl_col3:
                if result.get('image_path') and os.path.exists(result['image_path']):
                    with open(result['image_path'], 'rb') as f:
                        st.download_button(
                            "🖼️ Download Image",
                            data=f.read(),
                            file_name=f"linkedin_visual_{topic.replace(' ', '_')}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                elif result.get('image_url'):
                    st.markdown("**Image URL:**")
                    st.code(result['image_url'])
                else:
                    st.info("📝 Text content ready - image generation optional")
            
            # Update stats
            st.session_state.workflow_stats["total_runs"] += 1
            logger.info(f"Content generation completed successfully. Total runs: {st.session_state.workflow_stats['total_runs']}")
            st.session_state.workflow_stats["avg_execution_time"] = (
                (st.session_state.workflow_stats["avg_execution_time"] * 
                 (st.session_state.workflow_stats["total_runs"] - 1) + 
                 result['execution_time']) / st.session_state.workflow_stats["total_runs"]
            )
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            st.error(f"❌ Error generating content: {str(e)}")
            st.info("🔧 Please check your .env file has a valid OPENROUTER_API_KEY")

# Footer stats
if st.session_state.workflow_stats["total_runs"] > 0:
    stats = st.session_state.workflow_stats
    st.markdown("---")
    st.markdown(f"📊 **Stats:** {stats['total_runs']} posts generated | Avg time: {stats['avg_execution_time']:.1f}s")