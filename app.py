"""
🔥 FIRE Fact-Checker - Streamlit Web App
Fact-checking with Iterative Retrieval and Verification using Google Gemini
"""

import os
import time
import json
import dataclasses
import streamlit as st
from common.modeling import Model
from common.shared_config import google_api_key, serper_api_key
from eval.fire.verify_atomic_claim import verify_atomic_claim

# Set API keys
os.environ["GOOGLE_API_KEY"] = google_api_key
os.environ["SERPER_API_KEY"] = serper_api_key

# Page configuration
st.set_page_config(
    page_title="🔥 FIRE Fact-Checker",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .result-true {
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 20px 0;
    }
    .result-false {
        background: linear-gradient(135deg, #EF4444, #DC2626);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 20px 0;
    }
    .search-card {
        background: #f8f9fa;
        border-left: 4px solid #4F46E5;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .step-item {
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 6px;
        background: #f0f0f0;
    }
    .step-done {
        background: #d1fae5;
        border-left: 3px solid #10B981;
    }
    .step-running {
        background: #fef3c7;
        border-left: 3px solid #F59E0B;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'model' not in st.session_state:
    st.session_state.model = None

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/mbzuai-nlp/fire/main/assets/logo.png", width=80)
    st.title("⚙️ Settings")
    
    model_option = st.selectbox(
        "Select Model",
        ["gemini-2.5-flash-lite","gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        index=0
    )
    
    temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
    max_tokens = st.slider("Max Tokens", 512, 4096, 2048, 256)
    
    st.divider()
    st.markdown("### 📊 Session Stats")
    total_claims = len(st.session_state.history)
    correct = sum(1 for h in st.session_state.history if h.get('correct', False))
    st.metric("Claims Verified", total_claims)
    if total_claims > 0:
        st.metric("Accuracy", f"{correct/total_claims*100:.1f}%")
    
    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown("""
    **FIRE** (Fact-checking with Iterative Retrieval and Verification) 
    is an agent-based framework that dynamically decides when to search 
    for more evidence or make a final judgment.
    """)

# Main content
st.title("🔥 FIRE Fact-Checker")
st.markdown("*Verify claims with AI-powered fact-checking*")

# Input section
with st.form("claim_form"):
    claim_input = st.text_area(
        "📝 Enter a claim to verify:",
        placeholder="Example: The Eiffel Tower is located in Paris, France.",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.form_submit_button("🔍 Verify Claim", use_container_width=True)

# Process claim
if submit_button and claim_input.strip():
    claim = claim_input.strip()
    
    # Initialize model if needed
    model_name = f"google:{model_option}"
    
    with st.spinner("Initializing model..."):
        if st.session_state.model is None or st.session_state.model.model_id != model_option:
            st.session_state.model = Model(model_name, temperature=temperature, max_tokens=max_tokens)
    
    # Create containers for real-time updates
    progress_container = st.container()
    result_container = st.container()
    
    with progress_container:
        st.markdown("### 📊 Verification Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
        steps_container = st.empty()
        
    steps = []
    
    def update_progress(step_num, total_steps, message, status="running"):
        steps.append({"message": message, "status": status})
        progress_bar.progress(step_num / total_steps)
        status_text.markdown(f"**{message}**")
        
        # Display all steps
        steps_html = ""
        for i, step in enumerate(steps):
            icon = "✅" if step["status"] == "done" else "⏳" if step["status"] == "running" else "📋"
            css_class = "step-done" if step["status"] == "done" else "step-running"
            steps_html += f'<div class="step-item {css_class}">{icon} {step["message"]}</div>'
        steps_container.markdown(steps_html, unsafe_allow_html=True)
    
    # Step 1: Start
    update_progress(1, 5, "Starting fact-check process...", "done")
    time.sleep(0.3)
    
    # Step 2: Call verification
    update_progress(2, 5, "Calling LLM for analysis...", "running")
    
    try:
        start_time = time.time()
        result, searches, usage = verify_atomic_claim(claim, st.session_state.model)
        elapsed_time = time.time() - start_time
        
        # Update steps
        steps[-1]["status"] = "done"
        
        num_searches = len(searches.get('google_searches', []))
        if num_searches > 0:
            update_progress(3, 5, f"Performed {num_searches} web search(es)", "done")
        else:
            update_progress(3, 5, "No additional searches needed", "done")
        
        update_progress(4, 5, "Analyzing evidence...", "done")
        update_progress(5, 5, "Completed!", "done")
        progress_bar.progress(100)
        
        # Display result
        with result_container:
            st.markdown("---")
            
            if result is not None:
                answer = result.answer.upper()
                is_true = answer == "TRUE"
                
                # Result badge
                result_class = "result-true" if is_true else "result-false"
                result_icon = "✅" if is_true else "❌"
                st.markdown(f'<div class="{result_class}">{result_icon} {answer}</div>', unsafe_allow_html=True)
                
                # Stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<div class="stats-card">🔍<br><b>Searches</b><br>' + str(num_searches) + '</div>', unsafe_allow_html=True)
                with col2:
                    if usage:
                        total_tokens = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                        st.markdown(f'<div class="stats-card">📊<br><b>Tokens</b><br>{total_tokens}</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="stats-card">⏱️<br><b>Time</b><br>{elapsed_time:.1f}s</div>', unsafe_allow_html=True)
                
                # Evidence section
                if num_searches > 0:
                    st.markdown("### 📚 Evidence from Web Searches")
                    for i, search in enumerate(searches.get('google_searches', [])):
                        with st.expander(f"🔍 Search {i+1}: {search.get('query', 'N/A')[:50]}...", expanded=(i==0)):
                            st.markdown(f"**Query:** {search.get('query', 'N/A')}")
                            
                            # Parse result to extract sources
                            result_text = search.get("result", "No result")
                            
                            # Extract [Source: URL] patterns
                            import re
                            source_pattern = r'\[Source: (https?://[^\]]+)\]'
                            sources = re.findall(source_pattern, result_text)
                            
                            # Remove [Source: ...] from display text for cleaner view
                            clean_text = re.sub(source_pattern, '', result_text).strip()
                            
                            st.markdown("**Evidence:**")
                            st.markdown(f'<div class="search-card">{clean_text}</div>', unsafe_allow_html=True)
                            
                            # Display sources as clickable links
                            if sources:
                                st.markdown("**📎 Sources:**")
                                for j, source in enumerate(set(sources)):  # Use set to remove duplicates
                                    st.markdown(f"{j+1}. [{source[:60]}...]({source})" if len(source) > 60 else f"{j+1}. [{source}]({source})")
                
                # LLM Response
                with st.expander("🤖 Full LLM Response"):
                    st.markdown(result.response)
                
                # Add to history
                st.session_state.history.append({
                    'claim': claim,
                    'result': answer,
                    'searches': num_searches,
                    'time': elapsed_time,
                    'correct': None  # Unknown
                })
                
            else:
                st.error("❌ Failed to verify the claim. Please try again.")
                
    except Exception as e:
        st.error(f"❌ Error during verification: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())

# History section
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📜 Verification History")
    
    for i, item in enumerate(reversed(st.session_state.history[-5:])):  # Show last 5
        result_emoji = "✅" if item['result'] == "TRUE" else "❌"
        with st.expander(f"{result_emoji} {item['claim'][:60]}..."):
            st.markdown(f"**Claim:** {item['claim']}")
            st.markdown(f"**Result:** {item['result']}")
            st.markdown(f"**Searches:** {item['searches']} | **Time:** {item['time']:.1f}s")
