# Enterprise Agentic RAG — Live Hosting & Deployment Guide

This guide details step-by-step instructions to host the **Enterprise Agentic RAG** system live on free or low-cost cloud platforms.

---

## 🛠️ Recommended Architecture

| Component | Technology | Hosting Platform | Cost Tier |
|---|---|---|---|
| **Backend API** | FastAPI + Uvicorn | [Render.com](https://render.com) (Web Service) | 100% Free |
| **Frontend UI** | Streamlit | [Streamlit Community Cloud](https://share.streamlit.io) | 100% Free |
| **Vector DB** | Qdrant | [Qdrant Cloud](https://cloud.qdrant.io) | Managed Free Tier |
| **Tracing** | Pydantic Logfire / LangSmith | Logfire / LangSmith Dashboard | Free Tier |

---

## Option 1: Render (FastAPI) + Streamlit Cloud (UI) [RECOMMENDED]

### Step 1: Push Code to GitHub
Ensure your code is committed and pushed to a GitHub repository:
```bash
git add .
git commit -m "Configure production deployment settings"
git push origin main
```

---

### Step 2: Deploy FastAPI Backend on Render.com

1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Fill in the service configuration:
   - **Name**: `enterprise-rag-api`
   - **Environment**: `Python 3`
   - **Region**: Choose the closest region (e.g., Oregon or Frankfurt).
   - **Branch**: `main`
   - **Build Command**: 
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
4. Scroll down to **Environment Variables** and add the following keys from your `.env`:
   - `GEMINI_API_KEY`
   - `QDRANT_CLUSTER_ENDPOINT`
   - `QDRANT_API_KEY`
   - `GROQ_API_KEY`
   - `GROQ_FALLBACK_API_KEY`
   - `PORTKEY_API_KEY`
   - `LOGFIRE_TOKEN`
   - `LANGSMITH_TRACING` = `true`
   - `LANGSMITH_API_KEY`
   - `LANGSMITH_PROJECT` = `rag_scale_test`

5. Click **Create Web Service**.
6. Once deployed, copy your backend URL (e.g., `https://enterprise-rag-api.onrender.com`).

---

### Step 3: Deploy Streamlit UI on Streamlit Community Cloud

1. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click **New app**.
3. Select your repository, branch (`main`), and set the main file path:
   - **Main file path**: `ui/st_cloud_ui.py` (or `ui/app.py`)
4. Click **Advanced settings...** -> **Secrets**.
5. Paste the following secrets in TOML format:
   ```toml
   BACKEND_URL = "https://enterprise-rag-api.onrender.com"
   LOGFIRE_TOKEN = "your_pydantic_logfire_token_here"
   ```
6. Click **Deploy!**.

---

## Option 2: 1-Click Multi-Service Deployment on Render (render.yaml)

If you prefer deploying both the API and UI on Render using Render Blueprints:

1. Go to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Blueprint**.
3. Connect your repository containing `render.yaml`.
4. Render will automatically detect the two services defined in `render.yaml`:
   - `enterprise-rag-api`
   - `enterprise-rag-ui`
5. Supply the required environment secret values when prompted.
6. Click **Apply**.

---

## Option 3: Docker Deployment (Self-Hosted / VPS / Railway / GCP Cloud Run)

### Build and Run Backend Container Locally or on VPS
```bash
# Build Backend Image
docker build -t enterprise-rag-api:latest .

# Run Container
docker run -d \
  --name rag-api \
  -p 8000:8000 \
  --env-file .env \
  enterprise-rag-api:latest
```

### Build and Run Streamlit UI Container
```bash
# Build UI Image
docker build -f Dockerfile.ui -t enterprise-rag-ui:latest .

# Run Container
docker run -d \
  --name rag-ui \
  -p 8501:8501 \
  -e BACKEND_URL="http://host.docker.internal:8000" \
  -e LOGFIRE_TOKEN="your_token" \
  enterprise-rag-ui:latest
```

---

## 🔍 Verification & Health Checks

1. **API Health Endpoint**:
   Navigating to `https://your-api-domain.onrender.com/healthz` should return:
   ```json
   { "status": "healthy" }
   ```

2. **Mermaid Graph Endpoint**:
   Navigating to `https://your-api-domain.onrender.com/graph` will display the live agent workflow diagram.

3. **CORS Verification**:
   The API has `CORSMiddleware` configured allowing Streamlit Cloud to send `POST /query` requests seamlessly.

4. **Observability**:
   Check your [Logfire Dashboard](https://logfire.pydantic.dev) and [LangSmith Dashboard](https://smith.langchain.com) to see live distributed traces originating from UI user prompts down to NeMo Guardrails and LangGraph execution nodes.
