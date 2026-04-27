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
    You are 'Senior Arch', a world-class Principal Engineer and Mentor.
    Analyze this GitHub data for '{username}':
    Bio: {data.get('bio', 'No bio provided')}
    Stats: {data.get('public_repos_count')} repos, {data.get('followers')} followers
    Languages: {data.get('primary_languages', [])}
    Recent Projects: {data.get('recent_repos', [])[:10]}

    Provide a deep, actionable review in easy-to-understand English. 
    Focus on "Real-World" improvements that a Senior Developer would look for.

    Structure your response as follows:

    ### 🌍 Global Portfolio Strategy
    - What is the overall "vibe" of this portfolio? (e.g., "The Experimentalist", "The System Builder").
    - What is missing globally? (e.g., a consistent README style, license files, or a professional profile picture/bio).
    - One big "Global Fix" that would double their profile's impact.

    ### 🔍 Deep Dive: Top 5 Repositories
    Pick the 5 most interesting repositories from the list above. For EACH one, provide:
    1. **[Repo Name]**: A 1-sentence critique of what it is.
    2. **The "Senior" Fix**: One specific technical improvement (e.g., "Add an `.env.example` file," "This needs a CI/CD workflow," or "The description is too vague—explain the *problem* it solves").

    ### 💡 Senior Developer "Pro-Tips"
    Provide 3 high-level pieces of advice for their career growth based on their stack.
    Example: "You use Python a lot; have you tried implementing Type Hints? It makes your code look 10x more professional."

    ### 🎯 Next Steps
    A simple bulleted list of the first 3 things they should do TODAY to improve.

    Keep it encouraging but be honest like a real mentor. Use simple English.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"feedback": response.content}