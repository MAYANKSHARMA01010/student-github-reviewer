# 🚢 Deployment Guide

DevMentor AI is optimized for containerized deployment, specifically on **Hugging Face Spaces**.

## ☁️ Deploying to Hugging Face (Docker)

### 1. Create the Space
- Go to [Hugging Face Spaces](https://huggingface.co/new-space).
- Set the **SDK** to `Docker`.
- Choose the **Blank** template or `Streamlit`.

### 2. Configure Environment Secrets
In your Space settings, add:
- `GROQ_API_KEY`: Your API key for Llama 3.1.
- `GITHUB_TOKEN`: (Optional) Your GitHub Personal Access Token.

### 3. Push your Code
You can push directly to the Hugging Face remote:
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git push hf main
```

---

## 🐳 Local Docker Deployment

If you want to run the container locally:

### Build the Image
```bash
docker build -t student-github-reviewer .
```

### Run the Container
```bash
docker run -p 7860:7860 --env-file .env student-github-reviewer
```
The app will be available at `http://localhost:7860`.

---

## 🛠️ Docker Details
- **Port**: The app runs on port `7860`.
- **Base Image**: Uses `python:3.10-slim` for a lightweight footprint.
- **Entrypoint**: Runs `streamlit run ui/app.py`.
