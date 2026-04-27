import os
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from .state import ReviewState
load_dotenv()
# Set up the Groq AI brain using Llama 3.1
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
def extract_github_data(state: ReviewState):
    username = state["username"]
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}
    
    try:
        # Fetch User Bio and Stats
        user_url = f"https://api.github.com/users/{username}"
        user_resp = requests.get(user_url, headers=headers)
        
        # Fetch Top 10 Repos (sorted by stars/updates)
        repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10"
        repos_resp = requests.get(repos_url, headers=headers)
        
        if user_resp.status_code == 200 and repos_resp.status_code == 200:
            u_data = user_resp.json()
            r_data = repos_resp.json()
            
            repo_details = [
                {"name": r["name"], "desc": r.get("description", ""), "lang": r.get("language", "")} 
                for r in r_data
            ]
            
            languages = list(set([r["lang"] for r in repo_details if r["lang"]]))
            
            real_data = {
                "bio": u_data.get("bio", ""),
                "public_repos_count": u_data.get("public_repos", 0),
                "followers": u_data.get("followers", 0),
                "recent_repos": repo_details,
                "primary_languages": languages,
            }
            return {"github_data": real_data}
        else:
            return {"github_data": {"error": f"API Error: User {username} not found."}}
    except Exception as e:
        return {"github_data": {"error": str(e)}}
def code_mentor_review(state: ReviewState):
    username = state["username"]
    data = state["github_data"]
    
    if "error" in data:
        return {"feedback": f"❌ **Error:** {data['error']}"}

    prompt = f"""
    You are 'DevMentor AI', an elite technical recruiter and engineering manager.
    Analyze the following GitHub portfolio data for the user '{username}':
    {data}

    Your goal is to provide a comprehensive, high-signal review that feels personal and expert-level.
    Avoid generic praise. Be specific about their tech stack.

    Please structure your response exactly as follows:

    ### 🚀 The Verdict
    A one-sentence punchy summary of their developer persona (e.g., "A promising Frontend specialist with a clear focus on React ecosystems").

    ### 🛠️ Tech Stack Mastery
    Analyze the languages used ({data.get('primary_languages', [])}). 
    - What does this combination say about their role (Backend, Frontend, Fullstack, etc.)?
    - Are they using modern or niche languages?

    ### 📂 Portfolio Hygiene
    Look at their recent projects ({data.get('recent_repos', [])}). 
    - Comment on project naming and variety.
    - Mention if they seem to be building tools, apps, or learning exercises.

    ### 💡 Actionable Growth Plan
    Give 3 specific, non-generic suggestions for this specific developer. 
    Examples: 
    - "Since you use TypeScript, consider adding Zod for schema validation in your next project."
    - "Your repos seem focused on logic; try adding a 'Docs' folder with architectural diagrams."
    - "Contribution activity seems focused on personal repos; try contributing to one of these 3 open source projects related to {data.get('primary_languages', ['your stack'])[0]}."

    ### 🌟 Final Mentorship Note
    An encouraging, high-energy closing statement.

    Use professional yet modern developer terminology. Use emojis sparingly but effectively.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"feedback": response.content}