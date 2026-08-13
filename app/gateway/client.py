import os
import logfire
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from app.config import settings


def get_langchain_llm(feature: str = "rag", temperature: float = 0.0, model_name: str = "llama-3.3-70b-versatile"):
    """
    Returns ChatGroq directly for sub-second classification and ultra-fast RAG latency.
    Can be optionally routed through Portkey AI Gateway when USE_PORTKEY_GATEWAY=true.
    """
    use_portkey = os.getenv("USE_PORTKEY_GATEWAY", "false").lower() == "true"
    portkey_key = settings.PORTKEY_API_KEY or os.getenv("PORTKEY_API_KEY")
    
    if use_portkey and portkey_key:
        try:
            headers = createHeaders(
                api_key=portkey_key,
                metadata={
                    "feature": feature,
                    "_user": "enterprise-rag",
                    "environment": "production"
                }
            )
            logfire.info(f"🌐 Initializing Portkey AI Gateway LLM | feature={feature} model={model_name}")
            return ChatOpenAI(
                api_key=portkey_key,
                base_url=PORTKEY_GATEWAY_URL,
                model=f"@groq/{model_name}",
                temperature=temperature,
                default_headers=headers,
                request_timeout=20
            )
        except Exception as e:
            logfire.warning(f"⚠️ Portkey Gateway initialization error: {e}. Falling back to direct ChatGroq.")
    
    logfire.info(f"⚡ Using direct ChatGroq client ({model_name}) | feature={feature}")
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name=model_name,
        temperature=temperature,
        request_timeout=20
    )