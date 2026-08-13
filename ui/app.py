import os
import streamlit as st
import requests
import time
import uuid
import logfire
from dotenv import load_dotenv

# Load environment variables explicitly from the root directory
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)

# Initialize Logfire
try:
    token = os.getenv("LOGFIRE_TOKEN")
    if not token:
        print("ERROR: LOGFIRE_TOKEN is empty or None!")
    logfire.configure(token=token)
    LOGFIRE_STATUS = "Connected & Tracing"
except Exception as e:
    print(f"Logfire Init Error in UI: {e}")
    LOGFIRE_STATUS = f"Standby (Error: {e})"

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Nexus Agentic OS - Enterprise RAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUTURISTIC GLASSMORPHISM STYLING ---
FUTURISTIC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* Main Background */
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 50% 0%, #1e1b4b 0%, #0d1117 60%, #07090e 100%) !important;
    font-family: 'Outfit', sans-serif !important;
    color: #f3f4f6 !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: rgba(11, 15, 25, 0.85) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(0, 242, 254, 0.15) !important;
}

/* Main Container Padding */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}

/* Glassmorphic Cards */
.glass-panel {
    background: rgba(17, 24, 39, 0.7);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
}

/* Glowing Header Text */
.hero-title {
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00f5d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -0.8px;
    margin-bottom: 2px;
    line-height: 1.2;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 400;
    margin-bottom: 16px;
}

/* Neon Badges */
.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 14px;
    border-radius: 20px;
    background: rgba(0, 242, 254, 0.1);
    border: 1px solid rgba(0, 242, 254, 0.3);
    color: #00f2fe;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-right: 8px;
}

/* Live Pulse Dot */
.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #00f5d4;
    box-shadow: 0 0 0 0 rgba(0, 245, 212, 0.7);
    animation: pulse 1.8s infinite;
    display: inline-block;
    margin-right: 8px;
}

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 245, 212, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 245, 212, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 245, 212, 0); }
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    border-radius: 16px !important;
    border: 1px solid rgba(0, 242, 254, 0.3) !important;
    background: rgba(15, 23, 42, 0.9) !important;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.15) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #00f2fe !important;
    box-shadow: 0 0 30px rgba(0, 242, 254, 0.35) !important;
}

/* Chat Message Bubbles */
[data-testid="stChatMessage"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
    backdrop-filter: blur(10px) !important;
}

/* Custom Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(0, 242, 254, 0.15) 0%, rgba(121, 40, 202, 0.25) 100%) !important;
    border: 1px solid rgba(0, 242, 254, 0.35) !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #00f2fe 0%, #7928ca 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.5) !important;
    transform: translateY(-2px) !important;
}

/* Code Blocks */
code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
"""

st.markdown(FUTURISTIC_CSS, unsafe_allow_html=True)

# --- AVATARS & CONSTANTS ---
AI_AVATAR = "🤖"
USER_AVATAR = "👤"

# --- SESSION MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    logfire.info(f"✨ New User Session Created: {st.session_state.session_id}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BACKEND URL RESOLUTION ---
def get_backend_url():
    url = None
    try:
        if "BACKEND_URL" in st.secrets:
            url = str(st.secrets["BACKEND_URL"]).strip()
    except Exception:
        pass
    if not url:
        url = os.getenv("BACKEND_URL", "http://localhost:8000").strip()
    
    url = url.rstrip("/")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
    return url

base_url = get_backend_url()

# --- SIDEBAR DASHBOARD ---
with st.sidebar:
    st.markdown('<div style="font-size: 1.4rem; font-weight: 800; color: #00f2fe; margin-bottom: 8px;">🧠 NEXUS AGENT OS</div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #64748b; font-size: 0.85rem; margin-bottom: 20px;">Autonomous RAG Architecture</div>', unsafe_allow_html=True)
    
    st.markdown("### ⚡ System Status")
    st.markdown(f'<div class="status-badge"><span class="pulse-dot"></span>LIVE ARCHITECTURE</div>', unsafe_allow_html=True)
    st.caption(f"**Backend API**: `{base_url}`")
    st.caption(f"**Logfire Tracing**: `{LOGFIRE_STATUS}`")
    st.caption(f"**Session Memory**: `{st.session_state.session_id[:8]}`")
    
    st.markdown("---")
    st.markdown("### 🛠️ Control Panel")
    
    if st.button("🗑️ Reset Session & Memory", use_container_width=True):
        logfire.warning(f"🗑️ Memory Wipe Triggered for session: {st.session_state.session_id}")
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.markdown("### 🌐 Live Architecture Graph")
    with st.expander("👁️ View Agent State Machine"):
        st.image(f"{base_url}/graph", caption="LangGraph Workflow Pipeline", use_container_width=True)

# --- HERO HEADER ---
st.markdown("""
<div class="glass-panel">
    <div class="hero-title">⚡ Nexus Agentic Assistant</div>
    <div class="hero-subtitle">Enterprise IT Intelligence Engine • Powered by Portkey AI Gateway & Qdrant Vector Engine</div>
    <div>
        <span class="status-badge">☸️ KUBERNETES READY</span>
        <span class="status-badge">🛡️ NEMO SAFETY RAILS</span>
        <span class="status-badge">⚡ GROQ LLAMA 3.3 70B</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SUGGESTED PROMPT CHIPS (If chat is empty) ---
if len(st.session_state.messages) == 0:
    st.markdown("### 💡 Recommended Prompts to Try:")
    col1, col2, col3 = st.columns(3)
    
    prompt_choice = None
    with col1:
        if st.button("☸️ What is Kubernetes pod scheduling?", use_container_width=True):
            prompt_choice = "What is Kubernetes pod scheduling?"
    with col2:
        if st.button("⚡ Explain Intel Xeon hardware acceleration", use_container_width=True):
            prompt_choice = "Explain Intel Xeon hardware acceleration"
    with col3:
        if st.button("🛡️ Show how NeMo guardrails block off-topic queries", use_container_width=True):
            prompt_choice = "Recommend me some good movies to watch"

    if prompt_choice:
        st.session_state.selected_prompt = prompt_choice

# --- RENDER CHAT HISTORY ---
for message in st.session_state.messages:
    avatar = AI_AVATAR if message["role"] == "assistant" else USER_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- HANDLE PROMPT INPUT ---
prompt = st.chat_input("Ask Nexus anything about your technical documentation...")

# Handle click from sample buttons
if "selected_prompt" in st.session_state and st.session_state.selected_prompt:
    prompt = st.session_state.selected_prompt
    st.session_state.selected_prompt = None

if prompt:
    # START TRACE
    with logfire.span("💬 User Chat Interaction", user_query=prompt, session_id=st.session_state.session_id):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        # Assistant Response
        with st.chat_message("assistant", avatar=AI_AVATAR):
            data = {}
            with st.status("🔍 Nexus Agent is synthesizing...", expanded=True) as status:
                try:
                    with logfire.span("📡 Calling RAG Backend"):
                        url = f"{base_url}/query"
                        payload = {"q": prompt, "thread_id": st.session_state.session_id}
                        
                        max_retries = 3
                        for attempt in range(max_retries):
                            try:
                                response = requests.post(url, json=payload, timeout=90)
                                if response.status_code == 200:
                                    data = response.json()
                                    break
                                elif response.status_code in (502, 503, 504) and attempt < max_retries - 1:
                                    st.write(f"⚡ Waking backend server from idle... Retrying ({attempt+1}/{max_retries})...")
                                    time.sleep(12)
                                else:
                                    st.error(f"Backend Error: {response.status_code} - {response.text[:300]}")
                                    st.stop()
                            except Exception as req_err:
                                if attempt < max_retries - 1:
                                    st.write("⚡ Waking backend server... Retrying in 10s...")
                                    time.sleep(10)
                                else:
                                    raise req_err

                    steps = data.get("thought_process", [])
                    for step in steps:
                        st.markdown(f"⚙️ `{step}`", unsafe_allow_html=False)

                    status.update(label="✅ Answer Synthesized via Portkey Gateway", state="complete", expanded=False)

                except Exception as e:
                    logfire.error(f"❌ UI-Backend Connection Failed: {e}")
                    status.update(label="❌ Connection Failed", state="error")
                    st.error("Backend Offline.")
                    st.stop()

            # Answer streaming — outside status container
            answer_placeholder = st.empty()
            full_answer = data.get("answer", "No response.")

            curr_text = ""
            for char in full_answer:
                curr_text += char
                answer_placeholder.markdown(curr_text + "▌")
                time.sleep(0.004)
            answer_placeholder.markdown(full_answer)

            # Retrieved Sources Container
            sources = data.get("sources", [])
            if sources:
                with st.expander(f"📄 Retrieved Technical Context ({len(sources)} Chunks)"):
                    for i, source in enumerate(sources):
                        st.caption(f"Vector Chunk {i + 1}")
                        st.info(source)
            else:
                st.caption("ℹ️ Conversational mode — no vector context retrieval required.")

            st.session_state.messages.append({"role": "assistant", "content": full_answer})
            logfire.info("✅ Chat cycle completed successfully.")