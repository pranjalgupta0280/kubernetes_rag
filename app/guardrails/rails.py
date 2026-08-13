import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import logfire
from langchain_groq import ChatGroq
from nemoguardrails import RailsConfig, LLMRails

from app.config import settings
from app.guardrails.colang_rules import COLANG_CONTENT, YAML_CONTENT, RAIL_INDICATORS


_rails: LLMRails | None = None


def initialize_rails() -> None:
    """
    Build the NeMo LLMRails singleton at app startup.
    Defaulted to bypassed on cloud hosting environments to keep memory under 50 MB.
    """
    global _rails

    disable_nemo = os.getenv("DISABLE_NEMO_GUARD", "true").lower() == "true"
    if disable_nemo:
        logfire.info("ℹ️ NeMo Guardrails bypassed to conserve memory on cloud hosting tier.")
        _rails = None
        return

    try:
        guard_llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0
        )

        config = RailsConfig.from_content(
            colang_content=COLANG_CONTENT,
            yaml_content=YAML_CONTENT
        )

        _rails = LLMRails(config, llm=guard_llm)
        logfire.info("🛡️ NeMo Guardrails initialised (llama-3.1-8b-instant).")
    except Exception as e:
        logfire.warning(f"⚠️ NeMo Guardrails initialization skipped/failed: {e}")
        _rails = None




OFF_TOPIC_KEYWORDS = [
    "netflix", "movie", "movies", "tv show", "tv series", "cinema", "film", "films",
    "joke", "poem", "song", "weather", "recipe", "restaurant", "football", "basketball",
    "cricket", "game", "sports", "actor", "actress", "celebrity"
]


async def guard(message: str) -> tuple[bool, str | None]:
    """
    Run a user message through the NeMo rails gate.

    Returns:
        (True,  rail_response) — a rail fired; return this response immediately,
                                skip the RAG pipeline entirely.
        (False, None)          — message is clean; proceed to LangGraph.
    """
    msg_lower = message.lower()

    # 1. Quick off-topic keyword gate check (instant response without LLM call)
    if any(kw in msg_lower for kw in OFF_TOPIC_KEYWORDS):
        logfire.info(f"🛡️ Guardrails fired (keyword match) | query='{message[:80]}'")
        return True, "I'm an Enterprise IT Assistant focused on Kubernetes, Intel hardware, and networking. I can't help with that — but ask me anything technical!"

    if _rails is None and os.getenv("DISABLE_NEMO_GUARD", "false").lower() != "true":
        try:
            initialize_rails()
        except Exception:
            pass

    if _rails is None:
        logfire.info("⚠️ Guardrails uninitialized/bypassed — passing through.")
        return False, None

    with logfire.span("🛡️ Guardrails Check"):
        try:
            import asyncio
            result = await asyncio.to_thread(_rails.generate, messages=[{"role": "user", "content": message}])

            # NeMo returns {'role': 'assistant', 'content': '...'} — extract text
            if isinstance(result, dict):
                content = result.get("content", "")
            elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                content = result[0].get("content", "")
            else:
                content = str(result)

            fired = any(indicator.lower() in content.lower() for indicator in RAIL_INDICATORS)

            if fired:
                logfire.info(f"🛡️ Guardrails fired | query='{message[:80]}'")
                return True, content

            logfire.info("✅ Guardrails passed.")
            return False, None
        except Exception as e:
            logfire.error(f"❌ Guardrail execution error: {e}")
            return False, None
        except BaseException as b_err:
            logfire.error(f"❌ Critical Guardrail error bypassed: {b_err}")
            return False, None