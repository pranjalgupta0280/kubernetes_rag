import logfire
from app.agents.state import AgentState
from app.config import settings
from langchain_groq import ChatGroq

def generate_node(state: AgentState):
    """
    Synthesizes a response using both Documentation Context AND Conversation History.
    Uses ChatGroq directly via LangChain (Gateway/Cache logic removed).
    """
    query = state["current_query"]

    history_str = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"

    user_msg = state["messages"][-1]["content"] if state["messages"] else ""

    if query == "CONVERSATIONAL":
        logfire.info("Generating conversational response using memory.")
        prompt = f"""
        You are an Enterprise IT Assistant focused ONLY on Kubernetes, Intel hardware, and enterprise networking.

        RULES:
        1. If the user's message is a greeting, farewell, or asking about your capabilities/identity, respond politely.
        2. If the user asks about ANY off-topic subject (such as movies, TV shows, Netflix, sports, entertainment, food, general trivia, personal advice), respond ONLY with:
           "I'm an Enterprise IT Assistant focused on Kubernetes, Intel hardware, and networking. I can't help with that — but ask me anything technical!"
        3. Do NOT recommend movies, TV shows, or answer non-IT questions under any circumstances.

        CONVERSATION HISTORY:
        {history_str}

        LATEST MESSAGE:
        "{user_msg}"
        """
    else:
        logfire.info("Generating technical RAG response.")
        max_context_chars = 25000
        full_context = ""

        for doc in state.get("documents", []):
            if len(full_context) + len(doc) < max_context_chars:
                full_context += doc + "\n\n"
            else:
                logfire.warning("Context truncated to fit Groq TPM limits.")
                break

        prompt = f"""
        You are a Senior Technical Architect.
        Answer the question using the TECHNICAL CONTEXT provided.

        TECHNICAL CONTEXT:
        {full_context}

        CONVERSATION HISTORY:
        {history_str}

        USER QUESTION:
        "{user_msg}"
        """

    with logfire.span("✍️ LLM Synthesis"):
        try:
            # Initialize ChatGroq using your config
            llm = ChatGroq(
                api_key=settings.GROQ_API_KEY, 
                model_name="llama-3.3-70b-versatile", # Or pull this from settings if you have it
                temperature=0.1
            )
            
            # Use LangChain's invoke method
            response = llm.invoke(prompt)
            content = response.content

            logfire.info("✅ Response synthesised via LLM.")

            return {
                "final_answer": content,
                "status": "Response generated.",
                "plan": state.get("plan", []),
                "messages": [{"role": "assistant", "content": content}]
            }

        except Exception as e:
            logfire.error(f"LLM Generation failed: {e}")
            raise e