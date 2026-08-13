# ⚡ Enterprise Agentic RAG System (Nexus OS)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-DC2626?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![Portkey](https://img.shields.io/badge/Portkey_Gateway-00F2FE?style=for-the-badge)](https://portkey.ai)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)

An enterprise-grade, stateful **Agentic Retrieval-Augmented Generation (RAG)** system designed for high-precision technical documentation queries (Kubernetes, Intel hardware acceleration, and enterprise networking). 

Powered by **LangGraph state machines**, **Portkey AI Gateway**, **Qdrant Vector Database**, **NeMo Guardrails**, **Pydantic Logfire observability**, and a **futuristic Glassmorphism Streamlit UI**.

---

## 🌐 Live Production Endpoints

| Service / Component | Live Production URL | Status |
|---|---|---|
| **🚀 Backend API Base** | [`https://enterprise-rag-api-amgm.onrender.com`](https://enterprise-rag-api-amgm.onrender.com) | `Active` |
| **⚡ Health Check Probe** | [`https://enterprise-rag-api-amgm.onrender.com/healthz`](https://enterprise-rag-api-amgm.onrender.com/healthz) | `200 OK` |
| **👁️ Live Workflow Graph** | [`https://enterprise-rag-api-amgm.onrender.com/graph`](https://enterprise-rag-api-amgm.onrender.com/graph) | `PNG Render` |
| **🖥️ Frontend Interface** | [`https://kubernetes-rag.streamlit.app`](https://kubernetes-rag.streamlit.app) | `Active` |

---

## 📸 Interface Screenshots

### Futuristic Cyberpunk Glassmorphic Dashboard
![Nexus UI Interface 1](./images/Screenshot%202026-08-13%20162946.png)

### Live Query Execution & Retrieved Vector Chunks
![Nexus UI Interface 2](./images/Screenshot%202026-08-13%20163051.png)

---

## 🧠 System Architecture & Workflow

```mermaid
flowchart TD
    User([👤 User / Client UI]) -->|POST /query| FastAPI[🚀 FastAPI Backend Gateway]
    FastAPI -->|Check Gate 1| Guardrails{🛡️ NeMo Guardrails / Keyword Gate}
    
    Guardrails -->|Off-Topic / Jailbreak| Blocked[🛑 Instant Safety Response]
    Guardrails -->|Clean Query| LangGraph[🧠 LangGraph State Machine]
    
    subgraph Agentic Orchestration [LangGraph Cycle]
        Planner[🧠 Planner Node\nllama-3.1-8b-instant] -->|Intent Route| Router{Query Type?}
        Router -->|Conversational| Responder[✍️ Responder Node\nllama-3.1-8b-instant]
        Router -->|Technical Research| Retriever[🔍 Retriever Node\nQdrant Vector Search]
        Retriever -->|Rerank Chunks| ResponderTech[✍️ Technical Responder Node\nllama-3.3-70b-versatile]
    end
    
    LangGraph --> Portkey[🌐 Portkey AI Gateway]
    Portkey --> Groq[⚡ Groq Llama Models]
    Retriever --> Qdrant[(🗄️ Qdrant Cloud Vector DB)]
    
    Responder --> FinalAns[✅ Synthesized Answer & Sources]
    ResponderTech --> FinalAns
    FinalAns --> Streamlit[🖥️ Streamlit Glassmorphic UI]

    subgraph Observability
        FastAPI --> Logfire[🔥 Pydantic Logfire Tracing]
        FastAPI --> LangSmith[📊 LangSmith Telemetry]
    end
```

---

## Key Features & Highlights

* ⚡ **Multi-Tier Model Routing**:
  * **Sub-Second Intent Classification**: Uses `llama-3.1-8b-instant` (~0.3s) for intent planning and conversational chit-chat.
  * **Deep Technical Synthesis**: Uses `llama-3.3-70b-versatile` (~1.8s) for technical document synthesis.
* 🧠 **Stateful Context Memory**: Built-in LangGraph `MemorySaver` checkpointer maintaining thread-based multi-turn conversation history (`thread_id`).
* 🛡️ **Multi-Layer Safety Rails**: NVIDIA NeMo Guardrails + keyword-based instant safety gate preventing off-topic queries and prompt injection.
* 🌐 **Portkey AI Gateway**: Unified LLM proxy with fallback strategies, rate limiting, cost tracking, and response caching.
* 🗄️ **High-Precision Vector Retrieval**: Qdrant Cloud vector search paired with FlashRank semantic cross-encoder reranking.
* 🎨 **Futuristic UI Aesthetics**: Cyberpunk dark glassmorphic Streamlit interface with neon status badges, live pulse dots, interactive prompt recommendation chips, and streaming typewriter output.
* 📊 **End-to-End Observability**: Full distributed tracing via **Pydantic Logfire** and **LangSmith**.

---

## 📁 Repository Structure

```text
scalable rag/
├── app/
│   ├── main.py                   # FastAPI REST API entry point (CORS, lifespan, /query, /healthz, /graph)
│   ├── config.py                 # Centralized settings & environment variables
│   ├── agents/
│   │   ├── graph.py              # LangGraph StateGraph & MemorySaver checkpointer
│   │   ├── state.py              # AgentState TypedDict definition
│   │   └── nodes/
│   │       ├── planner.py        # Intent classification node (llama-3.1-8b-instant)
│   │       ├── retriever.py      # Qdrant search & reranking node
│   │       └── responder.py      # Response synthesis node (llama-3.3-70b-versatile)
│   ├── gateway/
│   │   └── client.py             # Portkey AI Gateway & ChatGroq LLM factory
│   ├── guardrails/
│   │   └── rails.py              # NeMo Guardrails & keyword safety gate
│   └── services/
│       └── retrieval/
│           ├── embeddings.py     # Gemini embeddings with retry backoff
│           ├── qdrant_service.py # Qdrant Cloud vector search client
│           └── ranking_service.py# Memory-safe semantic reranking
├── ui/
│   ├── app.py                    # Local Streamlit UI application
│   └── st_cloud_ui.py            # Production Streamlit Community Cloud UI application
├── images/                       # UI screenshots and visual assets
├── docs/                         # Deployment & architecture documentation
├── Dockerfile                    # Multi-stage production Dockerfile (FastAPI Backend)
├── Dockerfile.ui                 # Production Dockerfile (Streamlit UI)
├── render.yaml                   # 1-Click Render Blueprint infrastructure manifest
├── requirements.txt              # Production Python runtime dependencies
└── .env.example                  # Environment variable key template
```

---

## ⚙️ Local Development Setup

### 1. Prerequisites
* Python 3.11+
* Git
* Virtual Environment tool (`venv`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/pranjalgupta0280/kubernetes_rag.git
cd kubernetes_rag

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install --prefer-binary -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

```ini
GEMINI_API_KEY=your_gemini_api_key
QDRANT_CLUSTER_ENDPOINT=https://your-qdrant-url.qdrant.tech
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=gsk_your_groq_api_key
PORTKEY_API_KEY=your_portkey_api_key
LOGFIRE_TOKEN=your_logfire_token
```

### 4. Run the Backend API
```bash
uvicorn app.main:app --reload --port 8000
```
* API Docs: [`http://localhost:8000/docs`](http://localhost:8000/docs)
* Health Check: [`http://localhost:8000/healthz`](http://localhost:8000/healthz)

### 5. Run the Streamlit Frontend UI
```bash
streamlit run ui/app.py
```
Open [`http://localhost:8501`](http://localhost:8501) in your browser.

---

## 📡 API Endpoint Reference

### `POST /query`
Executes the RAG agent workflow for a prompt.

**Request Header**: `Content-Type: application/json`  
**Request Body**:
```json
{
  "q": "What is Kubernetes pod scheduling?",
  "thread_id": "user_session_99"
}
```

**Response (200 OK)**:
```json
{
  "question": "What is Kubernetes pod scheduling?",
  "answer": "Kubernetes pod scheduling refers to the process of assigning a pod to a node in the cluster where it can run...",
  "thought_process": [
    "Intent: Technical",
    "Search Term: Kubernetes pod scheduling",
    "Context Retrieved"
  ],
  "status": "Response generated.",
  "sources": [
    "CONTENT: Pod scheduling is handled by the kube-scheduler..."
  ]
}
```

---

## 🚀 Live Cloud Deployment

### 1. Backend API (Render.com)
* **Environment**: `Python 3`
* **Python Version**: `3.11.8`
* **Build Command**: `pip install --upgrade pip setuptools wheel && pip install --prefer-binary -r requirements.txt`
* **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2. Frontend UI (Streamlit Community Cloud)
* **Main File Path**: `ui/st_cloud_ui.py`
* **Secrets (TOML)**:
  ```toml
  BACKEND_URL = "https://enterprise-rag-api-amgm.onrender.com"
  ```

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for details.
