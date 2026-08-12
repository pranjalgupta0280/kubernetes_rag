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
    

def get_backend_url():
    """Dynamically determine FastAPI backend URL from Streamlit secrets or env vars."""
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


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Enterprise Agentic RAG",
    page_icon="🤖",
    layout="wide",
)

# --- AVATARS ---
AI_AVATAR = "🤖"
USER_AVATAR = "👤"


# --- SESSION MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    logfire.info(f"✨ New User Session Created: {st.session_state.session_id}")

if "messages" not in st.session_state:
    st.session_state.messages = []


# --- SIDEBAR ---
with st.sidebar:
    st.title("🧠 Agent OS")
    st.markdown("---")
    st.success(f"Logfire: {LOGFIRE_STATUS}")
    st.info(f"Memory ID: {st.session_state.session_id[:8]}")
    
    if st.button("🗑️ Clear History & Memory", use_container_width=True, type="primary"):
        logfire.warn(f"🗑️ Memory Wipe Triggered for session: {st.session_state.session_id}")
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# --- MAIN CHAT ---
st.title("🤖 Enterprise Agentic Assistant")


# Display history
for message in st.session_state.messages:
    avatar = AI_AVATAR if message["role"] == "assistant" else USER_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about your documentation..."):
    # START TRACE: User Interaction
    with logfire.span("💬 User Chat Interaction", user_query=prompt, session_id=st.session_state.session_id):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        # Assistant Response
        with st.chat_message("assistant", avatar=AI_AVATAR):
            data = None
            with st.status("🔍 Agent is thinking...", expanded=True) as status:
                try:
                    # DISTRIBUTED TRACE: Calling Backend
                    with logfire.span("📡 Calling RAG Backend"):
                        base_url = get_backend_url()
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
                                    st.write(f"⚡ Backend is waking up from idle (Render cold start)... Retrying ({attempt+1}/{max_retries})...")
                                    time.sleep(12)
                                else:
                                    response.raise_for_status()
                            except Exception as req_err:
                                if attempt < max_retries - 1:
                                    st.write(f"⚡ Waking backend server... Retrying in 10s...")
                                    time.sleep(10)
                                else:
                                    raise req_err
                    
                    # Show Reasoning Steps from Backend
                    steps = data.get("thought_process", [])
                    for step in steps:
                        st.write(f"⚙️ {step}")
                    
                    status.update(label="✅ Answer Synthesized", state="complete", expanded=False)
                except Exception as e:
                    logfire.error(f"❌ UI-Backend Connection Failed: {e}")
                    status.update(label="❌ Connection Failed", state="error")
                    st.error(f"Backend Connection Error: {e}")
                    st.stop()

            # Render Answer and Sources OUTSIDE st.status container to prevent illegal nested expanders
            if data:
                # Final Answer Streaming
                answer_placeholder = st.empty()
                full_answer = data.get("answer", "No response.")
                
                curr_text = ""
                for char in full_answer:
                    curr_text += char
                    answer_placeholder.markdown(curr_text + "▌")
                    time.sleep(0.005)
                
                answer_placeholder.markdown(full_answer)
                st.session_state.messages.append({"role": "assistant", "content": full_answer})

                # Show Sources (Top-level expander, avoiding nested expander crash)
                sources = data.get("sources", [])
                if sources:
                    with st.expander("📄 View Retrieved Context (Sources)"):
                        for i, source in enumerate(sources):
                            st.markdown(f"**Chunk {i+1}:**")
                            st.info(source)

                logfire.info("✅ Chat cycle completed successfully.")