# ============================================================
# CRITICAL: logfire MUST be configured before ALL other imports
# so that spans from all modules are captured from the start.
# ============================================================
import logfire
import os
import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Ensure UTF-8 console output on Windows for Logfire emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

load_dotenv()

logfire_token = os.getenv("LOGFIRE_TOKEN")
try:
    if logfire_token:
        logfire.configure(token=logfire_token)
    else:
        logfire.configure(send_to_logfire=False)
except Exception as e:
    print(f"Logfire init warning: {e}")

# Now safe to import app modules - logfire is already active
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.agents.graph import rag_agent
from app.guardrails import initialize_rails, guard

from pydantic import BaseModel
from typing import Optional


@asynccontextmanager
async def lifespan(app: FastAPI):
    logfire.info("🚀 Starting Enterprise RAG API...")
    yield
    logfire.info("🛑 Shutting down Enterprise RAG API...")


# Initialize FastAPI
app = FastAPI(title="Enterprise Agentic RAG API", lifespan=lifespan)

# Enable CORS for cross-origin requests from Streamlit Cloud and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    q: str
    thread_id: Optional[str] = "default_user"
    
    
@app.get("/")
def home():
    return {"message": "Enterprise LangGraph RAG API is live.", "status": "ok"}


@app.get("/healthz")
def health_check():
    """Health check endpoint for cloud platform probes (Render, Railway, Kubernetes, etc.)"""
    return {"status": "healthy"}


@app.get("/graph")
def get_graph_image():
    """
    Returns the Mermaid image of the agent's workflow.
    """
    try:
        png_bytes = rag_agent.get_graph().draw_mermaid_png()
        return Response(content=png_bytes, media_type="image/png")
    except Exception as e:
        return {"error": f"Could not generate graph image: {e}"}
    
    
@app.post("/query")
async def query(request: QueryRequest):
    """
    Executes the LangGraph RAG flow with memory using a POST request.
    """
    q = request.q
    thread_id = request.thread_id

    initial_state = {
        "messages": [{"role": "user", "content": q}],
        "current_query": q,
        "documents": [],
        "plan": ["Start"],
        "status": "Initializing Graph..."
    }
    
    # Configuration for Memory (Thread ID)
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Gate 1: NeMo Guardrails — blocks off-topic, jailbreaks, and handles dialog
        rail_fired, rail_response = await guard(q)
        if rail_fired:
            logfire.info(f"🛡️ Request blocked by guardrails | thread={thread_id}")
            return {
                "question": q,
                "answer": rail_response,
                "thought_process": ["🛡️ Gate 1: NeMo Guardrails Fired", "Retrieval: Skipped"],
                "status": "Blocked by guardrails.",
                "sources": []
            }

        # Gate 2: LangGraph RAG pipeline
        # Run graph in thread pool so Uvicorn event loop stays 100% non-blocking
        import asyncio
        final_output = await asyncio.to_thread(rag_agent.invoke, initial_state, config=config)
        
        return {
            "question": q,
            "answer": final_output.get("final_answer"),
            "thought_process": final_output.get("plan"),
            "status": final_output.get("status"),
            "sources": final_output.get("documents", [])
        }
    except Exception as e:
        logfire.error(f"❌ Backend Execution Failed: {e}")
        return {
            "question": q,
            "answer": "I apologize, but I encountered an internal error while processing your request. Please try again later.",
            "thought_process": ["Error encountered during execution."],
            "status": "error",
            "sources": []
        }