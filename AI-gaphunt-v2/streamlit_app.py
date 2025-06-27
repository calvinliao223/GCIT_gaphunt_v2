#!/usr/bin/env python3
"""
Gap Hunter Bot - Streamlit Web Interface
Modern web-based UI for academic research gap identification
"""

import streamlit as st
import pandas as pd
import yaml
import json
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import sys
import os

# Import the existing Gap Hunter Bot logic
sys.path.append('.')
from clean_gap_hunter import GapHunterBot

# Page configuration
st.set_page_config(
    page_title="Gap Hunter Bot - Academic Research",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .research-gap-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .paper-info {
        background-color: #e8f4fd;
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin-bottom: 0.5rem;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
    }
    .q1-journal {
        background-color: #d4edda;
        color: #155724;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
    .non-q1-journal {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'bot' not in st.session_state:
        st.session_state.bot = GapHunterBot()

def display_header():
    """Display the main header and introduction"""
    st.markdown('<h1 class="main-header">🎓 Gap Hunter Bot</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Academic Research Gap Identification & Idea Development</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    **Welcome to Gap Hunter Bot!** 🔍 I fetch fresh research gaps and rate their novelty.
    
    **How it works:**
    1. Enter your research topic
    2. I search recent papers from Semantic Scholar, CORE, and Crossref
    3. I identify research gaps and generate expansion keywords
    4. I assign novelty scores (1-5, score < 3 = "rethink")
    5. I check Q1 journal rankings and provide next steps
    """)

def display_sidebar():
    """Display sidebar with search options and history"""
    st.sidebar.markdown("## 🔧 Search Options")
    
    # API Status
    st.sidebar.markdown("### 📡 API Status")
    st.sidebar.success("✅ Semantic Scholar API")
    st.sidebar.success("✅ CORE API") 
    st.sidebar.success("✅ Crossref API")
    
    # Search History
    if st.session_state.search_history:
        st.sidebar.markdown("### 📚 Recent Searches")
        for i, search in enumerate(reversed(st.session_state.search_history[-5:])):
            if st.sidebar.button(f"🔍 {search['topic']}", key=f"history_{i}"):
                st.session_state.search_topic = search['topic']
                st.rerun()
    
    # Export Options
    if st.session_state.search_results:
        st.sidebar.markdown("### 💾 Export Results")
        
        # YAML Export
        yaml_data = yaml.dump(st.session_state.search_results, default_flow_style=False)
        st.sidebar.download_button(
            label="📄 Download YAML",
            data=yaml_data,
            file_name=f"research_gaps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml",
            mime="text/yaml"
        )
        
        # JSON Export
        json_data = json.dumps(st.session_state.search_results, indent=2)
        st.sidebar.download_button(
            label="📊 Download JSON",
            data=json_data,
            file_name=f"research_gaps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def search_research_gaps(topic):
    """Search for research gaps using the Gap Hunter Bot"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize bot
        bot = st.session_state.bot
        
        # Update progress
        progress_bar.progress(10)
        status_text.text("🔍 Starting research gap search...")
        
        # Search for gaps
        progress_bar.progress(30)
        status_text.text("📚 Searching academic databases...")
        
        results = bot.hunt_gaps(topic)
        
        progress_bar.progress(80)
        status_text.text("🧠 Analyzing research gaps...")
        
        # Simulate processing time for better UX
        time.sleep(1)
        
        progress_bar.progress(100)
        status_text.text("✅ Research gap analysis complete!")
        
        # Clear progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return results
        
    except Exception as e:
        st.error(f"❌ Error during search: {str(e)}")
        progress_bar.empty()
        status_text.empty()
        return None

def display_results(results):
    """Display search results in a formatted way"""
    if not results:
        st.warning("No results found. Please try a different research topic.")
        return
    
    # Check for error
    if len(results) == 1 and 'error' in results[0]:
        st.error(f"❌ {results[0]['error']}")
        st.info("💡 Try a more general topic or check your internet connection.")
        return
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Papers Found", len(results))
    
    with col2:
        avg_score = sum(r.get('score', 0) for r in results) / len(results)
        st.metric("📊 Avg Novelty Score", f"{avg_score:.1f}")
    
    with col3:
        q1_count = sum(1 for r in results if r.get('q1', False))
        st.metric("🏆 Q1 Journals", f"{q1_count}/{len(results)}")
    
    with col4:
        rethink_count = sum(1 for r in results if r.get('note') == 'rethink')
        st.metric("⚠️ Rethink Needed", rethink_count)
    
    # Display individual results
    st.markdown("## 📋 Research Gaps Found")

    for i, result in enumerate(results):
        with st.expander(f"📄 Gap {i+1}: {result.get('paper', 'Unknown Paper')}", expanded=True):
            display_single_result(result, i)

        # Add YAML output as a separate collapsible section
        with st.expander(f"📋 YAML Output for Gap {i+1}", expanded=False):
            yaml_output = yaml.dump([result], default_flow_style=False)
            st.code(yaml_output, language='yaml')
    
    # Display novelty score distribution
    if len(results) > 1:
        display_score_chart(results)

def display_single_result(result, index):
    """Display a single research gap result"""
    col1, col2 = st.columns([2, 1])

    with col1:
        # Paper information
        st.markdown(f"**📄 Paper:** {result.get('paper', 'Unknown')}")

        # Research gap
        st.markdown(f"**🔍 Research Gap:**")
        st.markdown(f"*{result.get('gap', 'No gap identified')}*")

        # Keywords
        keywords = result.get('keywords', [])
        if keywords:
            keyword_badges = " ".join([f"`{kw}`" for kw in keywords])
            st.markdown(f"**🏷️ Keywords:** {keyword_badges}")

        # Next steps
        next_steps = result.get('NEXT_STEPS', '')
        if next_steps:
            st.markdown(f"**🎯 Next Steps:** {next_steps}")

    with col2:
        # Novelty score
        score = result.get('score', 0)
        if score >= 4:
            score_class = "score-high"
            score_emoji = "🟢"
        elif score >= 3:
            score_class = "score-medium"
            score_emoji = "🟡"
        else:
            score_class = "score-low"
            score_emoji = "🔴"

        st.markdown(f"**📊 Novelty Score:**")
        st.markdown(f'<span class="{score_class}">{score_emoji} {score}/5</span>', unsafe_allow_html=True)

        # Note
        note = result.get('note', '')
        if note == 'rethink':
            st.warning("⚠️ Rethink needed")
        else:
            st.success("✅ Good novelty")

        # Q1 Journal status
        q1_status = result.get('q1', False)
        if q1_status:
            st.markdown('<span class="q1-journal">🏆 Q1 Journal</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="non-q1-journal">📄 Non-Q1 Journal</span>', unsafe_allow_html=True)

    # YAML output is now handled separately outside this function

def display_score_chart(results):
    """Display novelty score distribution chart"""
    st.markdown("## 📊 Novelty Score Distribution")
    
    scores = [r.get('score', 0) for r in results]
    score_counts = pd.Series(scores).value_counts().sort_index()
    
    fig = px.bar(
        x=score_counts.index,
        y=score_counts.values,
        labels={'x': 'Novelty Score', 'y': 'Number of Papers'},
        title="Distribution of Novelty Scores",
        color=score_counts.values,
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        xaxis_title="Novelty Score",
        yaxis_title="Number of Papers",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main Streamlit application"""
    initialize_session_state()
    display_header()
    display_sidebar()
    
    # Main search interface
    st.markdown("## 🔍 Search for Research Gaps")
    
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            topic = st.text_input(
                "Enter your research topic:",
                placeholder="e.g., machine learning, computer vision, natural language processing",
                help="Enter any academic research topic to find research gaps and generate ideas"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            search_button = st.form_submit_button("🔍 Hunt Gaps", use_container_width=True)
    
    # Example topics
    st.markdown("**💡 Example topics:** `artificial intelligence`, `deep learning`, `computer vision`, `natural language processing`, `machine learning for healthcare`")
    
    # Handle search
    if search_button and topic:
        # Add to search history
        search_entry = {
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.search_history.append(search_entry)
        
        # Perform search
        with st.spinner("🔍 Hunting for research gaps..."):
            results = search_research_gaps(topic)
            st.session_state.search_results = results
        
        # Display results
        if results:
            display_results(results)
    
    elif search_button and not topic:
        st.warning("⚠️ Please enter a research topic to search for gaps.")
    
    # Display previous results if available
    elif st.session_state.search_results:
        st.markdown("## 📋 Previous Search Results")
        display_results(st.session_state.search_results)

if __name__ == "__main__":
    main()
