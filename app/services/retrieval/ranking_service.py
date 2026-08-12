import os
import time
import logfire

# Lazy initialization - Ranker is loaded on first use
_ranker = None
_ranker_failed = False


def _get_ranker():
    """
    Initializes the FlashRank engine lazily if enabled and memory permits.
    Bypasses FlashRank on free tier / constrained environments to prevent OOM process crashes.
    """
    global _ranker, _ranker_failed
    
    if _ranker_failed:
        return None
        
    if os.getenv("DISABLE_RERANKER", "false").lower() == "true":
        logfire.info("ℹ️ Reranker explicitly disabled via DISABLE_RERANKER env flag.")
        _ranker_failed = True
        return None

    if _ranker is None:
        logfire.info("🧠 Initializing FlashRank Reranker Model...")
        try:
            from flashrank import Ranker
            _ranker = Ranker(cache_dir="/tmp/flashrank")
        except Exception as e:
            logfire.warning(f"⚠️ FlashRank init skipped/failed: {e}. Defaulting to Qdrant vector scores.")
            _ranker_failed = True
            return None

    return _ranker


def rerank_documents(query: str, documents: list[str], top_n: int = 5) -> list[str]:
    """
    Refines retrieval results by re-scoring documents against the query semantically.
    Falls back gracefully to Qdrant vector order if reranker is unavailable or fails.
    """
    if not documents:
        return []

    ranker = _get_ranker()
    if ranker is None:
        return documents[:top_n]

    start_time = time.time()
    logfire.info(f"📡 [Reranker] Rescoring {len(documents)} docs via FlashRank Cross-Encoder...")

    try:
        from flashrank import RerankRequest
        passages = [
            {"id": i, "text": doc}
            for i, doc in enumerate(documents)
        ]

        request = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(request)
        
        reranked_docs = []
        for res in results[:top_n]:
            reranked_docs.append(res['text'])

        duration = time.time() - start_time
        top_score = results[0]['score'] if results else 'N/A'
        logfire.info(f"✅ [Reranker] Done in {duration:.2f}s. Top semantic score: {top_score}")
        
        return reranked_docs

    except Exception as e:
        logfire.warning(f"⚠️ [Reranker] Semantic Reranking Failed: {e}. Using Qdrant vector scores.")
        return documents[:top_n]