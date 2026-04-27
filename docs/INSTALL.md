# 🛠️ Installation Guide

This guide will help you set up DevMentor AI on your local machine from scratch.

## 📋 Prerequisites

- **Python 3.10+**: Ensure you have Python installed.
- **Git**: To clone the repository.
- **Groq API Key**: Get one from [Groq Cloud](https://console.groq.com/).

---

## 🏗️ Step-by-Step Setup

### 1. Clone the Repository
Open your terminal and run:
```bash
git clone https://github.com/MAYANKSHARMA01010/student-github-reviewer.git
cd student-github-reviewer
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to avoid dependency conflicts.
```bash
python -m venv venv
```
Activate it:
- **macOS / Linux**: `source venv/bin/activate`
- **Windows**: `venv\Scripts\activate`

### 3. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a file named `.env` in the root folder:
```bash
touch .env
```
Add the following content to `.env`:
```env
GROQ_API_KEY=your_actual_key_here
GITHUB_TOKEN=your_github_token_here
```
> [!TIP]
> A GitHub Token is optional but recommended to avoid rate limiting when analyzing multiple profiles.

---

## ✅ Verification
Run the following command to verify the installation:
```bash
streamlit run ui/app.py
```
If the browser opens with the DevMentor AI interface, you are all set!
