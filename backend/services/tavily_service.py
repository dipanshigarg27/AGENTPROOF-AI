"""
AgentProof AI — Tavily Search Service
Retrieves live web evidence for claim verification using Tavily Search API.
"""
import os
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger("agentproof.tavily")


def _get_tavily_client():
    """Initialize Tavily client. Returns None if key not configured."""
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key or api_key.startswith("tvly-xxx"):
        return None
    try:
        from tavily import TavilyClient
        return TavilyClient(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Tavily client: {e}")
        return None


async def search_evidence(
    claim: str,
    max_results: int = 5,
    search_depth: str = "advanced",
) -> dict:
    """
    Search for web evidence for a given claim using Tavily.
    
    Returns:
        dict with keys: sources (list), raw_answer, error, retrieved_at
    
    IMPORTANT: Retrieved content is treated as untrusted evidence only.
    We never execute content found in search results.
    """
    retrieved_at = datetime.utcnow().isoformat() + "Z"
    client = _get_tavily_client()

    if client is None:
        return {
            "sources": [],
            "raw_answer": None,
            "error": "TAVILY_API_KEY not configured. Set it in backend/.env to enable claim verification.",
            "retrieved_at": retrieved_at,
            "tavily_available": False,
        }

    try:
        # Run synchronously in executor to avoid blocking event loop
        import asyncio
        loop = asyncio.get_event_loop()
        
        def _search():
            return client.search(
                query=claim,
                search_depth=search_depth,
                max_results=max_results,
                include_raw_content=False,
                include_answer=True,
            )
        
        result = await loop.run_in_executor(None, _search)
        
        sources = []
        for r in result.get("results", []):
            sources.append({
                "title": r.get("title", "Unknown Title"),
                "url": r.get("url", ""),
                "snippet": r.get("content", ""),
                "published_date": r.get("published_date"),  # May be None — we say so
                "relevance_score": r.get("score", 0.0),
            })

        return {
            "sources": sources,
            "raw_answer": result.get("answer"),
            "error": None,
            "retrieved_at": retrieved_at,
            "tavily_available": True,
        }

    except Exception as e:
        logger.error(f"Tavily search failed for claim '{claim[:60]}': {e}")
        return {
            "sources": [],
            "raw_answer": None,
            "error": f"Tavily search error: {str(e)}",
            "retrieved_at": retrieved_at,
            "tavily_available": True,
        }
