import os
import streamlit as st
import requests
import json
import sys
import plotly.express as px
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

# --- Global Styles ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #070d1a;
        color: #e2e8f0;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp {
        animation: fadeIn 0.8s ease-out;
    }

    .main .block-container {
        padding-top: 3rem;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    .hero-container {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #070d1a 0%, #0c1830 100%);
        border-radius: 32px;
        border: 1px solid #1e2d45;
        margin-bottom: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    }

    .hero-title {
        font-size: clamp(2.5rem, 6vw, 4rem) !important;
        font-weight: 800 !important;
        letter-spacing: -0.05em !important;
        line-height: 1.05 !important;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem !important;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.25rem;
        max-width: 700px;
        line-height: 1.6;
    }

    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid #1e2d45;
        border-radius: 20px;
        padding: 24px;
        text-align: center;
    }

    .feedback-wrapper {
        background: #0f172a;
        border: 1px solid #1e2d45;
        border-radius: 24px;
        padding: 2.5rem;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }

    .feedback-wrapper h3 {
        color: #38bdf8 !important;
        margin-top: 2rem !important;
        font-weight: 700 !important;
        border-bottom: 1px solid #1e2d45;
        padding-bottom: 0.75rem;
    }

    .chart-box {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid #1e2d45;
        border-radius: 24px;
        padding: 30px;
        width: 100%;
        text-align: center;
        margin-bottom: 20px;
    }

    .chart-box img {
        max-width: 100%;
        border-radius: 12px;
    }
    
    .stats-card-img {
        max-width: 100%;
        border-radius: 16px;
        border: 1px solid #1e2d45;
        margin-top: 15px;
    }

    .footer {
        text-align: center;
        padding: 4rem 0 2rem;
        color: #475569;
        font-size: 0.9rem;
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

# --- Search Section ---
c_left, c_mid, c_right = st.columns([1, 2, 1])
with c_mid:
    username = st.text_input("Enter GitHub Username", placeholder="e.g. torvalds", label_visibility="collapsed")
    analyze = st.button("Generate Review", use_container_width=True)

# --- Logic & Results ---
if analyze:
    if not username.strip():
        st.warning("Please enter a GitHub username to begin your review.")
    else:
        with st.spinner(f"DevMentor AI is analyzing **@{username}**..."):
            try:
                if DIRECT_MODE:
                    initial_state = {"username": username}
                    result = github_reviewer_app.invoke(initial_state)
                    extracted = result.get("github_data", {})
                    feedback = result.get("feedback", "")
                    status_code = 200
                else:
                    response = requests.post(f"{BACKEND_URL}/review?username={username}", timeout=120)
                    status_code = response.status_code
                    if status_code == 200:
                        data = response.json()
                        extracted = data.get("extracted_data", {})
                        feedback = data.get("mentor_feedback", "")

                if status_code == 200:
                    if "error" in extracted:
                        st.error(f"Analysis failed: {extracted['error']}")
                    else:
                        st.success(f"Analysis Complete for @{username}")
                        
                        # --- Stats Dashboard ---
                        st.markdown("<br>", unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        repos = extracted.get("recent_repos", [])
                        primary_languages = extracted.get("primary_languages", [])
                        all_langs = extracted.get("all_languages", {})
                        repo_count = extracted.get("public_repos_count", 0)
                        followers = extracted.get("followers", 0)

                        with m1: st.metric("Total Public Repos", repo_count)
                        with m2: st.metric("Primary Stack", primary_languages[0] if primary_languages else "N/A")
                        with m3: st.metric("Followers", followers)

                        # --- Visual Charts Section ---
                        st.markdown("<br>", unsafe_allow_html=True)
                        chart_col1, chart_col2 = st.columns([1, 1.2], gap="medium")
                        
                        with chart_col1:
                            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                            st.markdown("<h4 style='color:#94a3b8; margin-bottom:15px; font-weight:600;'>Language Distribution</h4>", unsafe_allow_html=True)
                            if all_langs:
                                fig = px.pie(
                                    values=list(all_langs.values()),
                                    names=list(all_langs.keys()),
                                    hole=0.6,
                                    color_discrete_sequence=px.colors.qualitative.Pastel
                                )
                                fig.update_layout(
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    showlegend=True,
                                    legend=dict(font=dict(color="#94a3b8"), orientation="h", y=-0.1),
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    font=dict(color="#e2e8f0")
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Not enough language data for distribution chart.")
                            st.markdown('</div>', unsafe_allow_html=True)

                        with chart_col2:
                            # 1. Contribution Activity
                            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                            st.markdown("<h4 style='color:#94a3b8; margin-bottom:15px; font-weight:600;'>Contribution Activity</h4>", unsafe_allow_html=True)
                            st.markdown(f"""
                            <div style="overflow-x: auto; margin-top: 10px;">
                                <img src="https://ghchart.rshah.org/38bdf8/{username}" alt="Activity Chart" />
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 2. Stats & Most Used Languages below Activity
                            st.markdown(f"""
                            <div style="display: flex; gap: 15px; width: 100%; flex-wrap: wrap; justify-content: center; margin-top: 20px;">
                                <img class="stats-card-img" src="https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme=tokyonight&bg_color=0f172a&title_color=38bdf8&icon_color=38bdf8&text_color=94a3b8&border_color=1e2d45" alt="Stats Card" />
                                <img class="stats-card-img" src="https://github-readme-stats.vercel.app/api/top-langs/?username={username}&layout=compact&theme=tokyonight&bg_color=0f172a&title_color=38bdf8&text_color=94a3b8&border_color=1e2d45" alt="Langs Card" />
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # --- Details Layout ---
                        st.markdown("<br>", unsafe_allow_html=True)
                        c1, c2 = st.columns([1, 2], gap="large")
                        
                        with c1:
                            st.markdown("#### 🌍 Total Primary Languages")
                            if all_langs:
                                for lang, count in sorted(all_langs.items(), key=lambda x: x[1], reverse=True):
                                    st.markdown(f"- **{lang}**: {count} repositories")
                            else:
                                for lang in primary_languages:
                                    st.markdown(f"- `{lang}`")
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("#### 🚀 Recent Projects")
                            for repo in repos:
                                repo_name = repo['name'] if isinstance(repo, dict) else repo
                                st.markdown(f"- [{repo_name}](https://github.com/{username}/{repo_name})")

                        with c2:
                            st.markdown("#### 🤖 Mentor AI Feedback")
                            st.markdown('<div class="feedback-wrapper">', unsafe_allow_html=True)
                            st.markdown(feedback)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            report_content = f"# DevMentor AI Review for @{username}\n\n{feedback}"
                            st.download_button(
                                label="📥 Download Mentorship Report",
                                data=report_content,
                                file_name=f"devmentor_review_{username}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )

                elif status_code == 404:
                    st.error(f"User `@{username}` was not found on GitHub.")
                else:
                    st.error(f"The AI service is temporarily unavailable.")

            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown(f"""
<div class="footer">
    Powered by <b>LangGraph</b> & <b>Groq (Llama 3.1)</b> • Crafted with ❤️ by <b>Mayank Sharma</b>
</div>
""", unsafe_allow_html=True)