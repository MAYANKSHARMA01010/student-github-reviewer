import os
import streamlit as st
import requests
import json
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import the agent
sys.path.append(str(Path(__file__).parent.parent))

try:
    from agent.graph import github_reviewer_app
    DIRECT_MODE = True
except ImportError:
    DIRECT_MODE = False

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- Page Configuration ---
st.set_page_config(
    page_title="DevMentor AI | GitHub Portfolio Reviewer",
    page_icon="https://github.githubassets.com/favicons/favicon.png",
    layout="wide",
)

# --- Global Styles (Rich Aesthetics) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #070d1a;
        color: #e2e8f0;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1000px;
    }

    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #070d1a 0%, #0c1830 100%);
        border-radius: 24px;
        border: 1px solid #1e2d45;
        margin-bottom: 2rem;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    }

    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.1;
        margin-bottom: 1rem;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Input Styling */
    div.stTextInput > div > div > input {
        background-color: #0f172a !important;
        color: white !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease;
    }

    div.stTextInput > div > div > input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }

    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px rgba(29, 78, 216, 0.3);
        width: 100%;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 20px rgba(29, 78, 216, 0.4);
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(8px);
        border: 1px solid #1e2d45;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
    }

    /* Feedback Content Area */
    .feedback-card {
        background: #0f172a;
        border: 1px solid #1e2d45;
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }

    /* Custom Dividers */
    .stDivider {
        border-color: #1e2d45 !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #38bdf8 !important;
    }

    /* Lucide Icon Simulation */
    .icon-box {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background: rgba(56, 189, 248, 0.1);
        border-radius: 10px;
        color: #38bdf8;
        margin-right: 12px;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">Elevate Your Engineering <br> Career with DevMentor AI</h1>
    <p class="hero-subtitle">Get elite technical feedback on your GitHub portfolio. Built on LangGraph & Llama 3.1 for high-signal mentorship.</p>
</div>
""", unsafe_allow_html=True)

# --- Main Interaction ---
col1, col2 = st.columns([4, 1])
with col1:
    username = st.text_input(
        "Enter GitHub Username",
        placeholder="e.g. torvalds",
        label_visibility="collapsed",
    )
with col2:
    analyze = st.button("Generate Review")

# --- Logic & Results ---
if analyze:
    if not username.strip():
        st.warning("Please enter a GitHub username to begin your review.")
    else:
        with st.spinner(f"DevMentor AI is analyzing **@{username}**..."):
            try:
                if DIRECT_MODE:
                    # Run the agent directly
                    initial_state = {"username": username}
                    result = github_reviewer_app.invoke(initial_state)
                    
                    extracted = result.get("github_data", {})
                    feedback = result.get("feedback", "")
                    status_code = 200
                else:
                    # Fallback to backend API
                    response = requests.post(
                        f"{BACKEND_URL}/review?username={username}",
                        timeout=120,
                    )
                    status_code = response.status_code
                    if status_code == 200:
                        data = response.json()
                        extracted = data.get("extracted_data", {})
                        feedback = data.get("mentor_feedback", "")

                if status_code == 200:
                    if "error" in extracted:
                        st.error(f"Analysis failed: {extracted['error']}")
                    else:
                        st.success("Analysis Complete")
                        
                        # --- Stats Dashboard ---
                        st.markdown("<br>", unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        
                        repos = extracted.get("recent_repos", [])
                        languages = extracted.get("primary_languages", [])
                        repo_count = extracted.get("public_repos_count", 0)

                        with m1:
                            st.metric("Total Public Repos", repo_count)
                        with m2:
                            st.metric("Primary Languages", len(languages))
                        with m3:
                            st.metric("Recent Activity", len(repos))

                        # --- Two Column Layout for Details ---
                        st.markdown("<br>", unsafe_allow_html=True)
                        c1, c2 = st.columns([1, 2])
                        
                        with c1:
                            st.markdown("#### 📂 Tech Footprint")
                            with st.container():
                                st.markdown("**Languages:**")
                                for lang in languages:
                                    st.markdown(f"- `{lang}`")
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                                st.markdown("**Recent Projects:**")
                                for repo in repos:
                                    repo_name = repo['name'] if isinstance(repo, dict) else repo
                                    st.markdown(f"- [{repo_name}](https://github.com/{username}/{repo_name})")

                        with c2:
                            st.markdown("#### 🤖 Mentor AI Feedback")
                            st.markdown(f"""
                            <div class="feedback-card">
                                {feedback}
                            </div>
                            """, unsafe_allow_html=True)

                elif status_code == 404:
                    st.error(f"User `@{username}` was not found on GitHub.")
                else:
                    st.error(f"The AI service is temporarily unavailable (Status: {status_code}).")

            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem;">
    Powered by <b>LangGraph</b> & <b>Groq (Llama 3.1)</b> • Crafted with ❤️ by DevMentor AI
</div>
""", unsafe_allow_html=True)