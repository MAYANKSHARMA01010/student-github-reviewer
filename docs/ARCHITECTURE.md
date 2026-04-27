# 🏗️ Architecture & Logic

This document explains the technical inner workings of DevMentor AI.

## 🧠 The Agent System (LangGraph)

DevMentor AI uses a state-driven workflow managed by **LangGraph**. The workflow consists of two primary nodes:

### 1. `extract_github_data`
- **Source**: GitHub REST API.
- **Process**: 
  - Fetches the user's bio and global stats.
  - Fetches up to **100 repositories** to determine accurate language distribution.
  - Ranks languages by frequency.
  - Extracts names, descriptions, and languages for the top 10 most recent repositories.

### 2. `code_mentor_review`
- **Engine**: Llama 3.1 (via Groq).
- **Process**: 
  - Takes the extracted data and passes it through a "Senior Developer" system prompt.
  - Generates a structured mentorship report focusing on global strategy and specific repo fixes.

---

## 🎨 Frontend (Streamlit)
- **Styling**: Uses a custom CSS injection to override default Streamlit themes with a premium "Glassmorphism" look.
- **Charts**: 
  - **Plotly**: Used for the interactive language donut chart.
  - **GitHub Stats API**: Used for external SVG stats cards.
  - **ghchart**: Used for the contribution heatmap.

---

## 🔄 State Flow
1.  **Input**: Username.
2.  **State**: `{ "username": "..." }`.
3.  **Extraction**: State updated with `{ "github_data": { ... } }`.
4.  **Review**: State updated with `{ "feedback": "..." }`.
5.  **Output**: Rendered UI.
