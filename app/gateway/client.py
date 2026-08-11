import os
import logfire
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from app.config import settings


def get_langchain_llm(feature: str = "rag", temperature: float = 0.0):
    """
    Returns a Portkey AI Gateway-backed ChatOpenAI model if PORTKEY_API_KEY is configured.
    Falls back to direct ChatGroq if Portkey is unconfigured or encounters initialization issues.
    """
    portkey_key = settings.PORTKEY_API_KEY or os.getenv("PORTKEY_API_KEY")
    
    if portkey_key:
        try:
            headers = createHeaders(
                api_key=portkey_key,
                metadata={
                    "feature": feature,
                    "_user": "enterprise-rag",
                    "environment": "production"
                }
            )
            logfire.info(f"🌐 Initializing Portkey AI Gateway LLM | feature={feature}")
            return ChatOpenAI(
                api_key=portkey_key,
                base_url=PORTKEY_GATEWAY_URL,
                model="@groq/llama-3.3-70b-versatile",
                temperature=temperature,
                default_headers=headers
            )
        except Exception as e:
            logfire.warning(f"⚠️ Portkey Gateway initialization error: {e}. Falling back to direct ChatGroq.")
    
    logfire.info("⚡ Using direct ChatGroq client (Portkey gateway bypassed).")
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile",
        temperature=temperature
    )