import os
import json
from advanced_rag import AdvancedRAG

_advanced_rag = None

def _get_rag():
    global _advanced_rag
    if _advanced_rag is None:
        _advanced_rag = AdvancedRAG()
    return _advanced_rag

def consult_astrology_books(query: str, num_results: int = 4, tradition: str = None) -> str:
    """
    Queries the classical Vedic astrology RAG knowledge base for specific rules or slokas.
    Returns a JSON string of matched excerpts.
    """
    try:
        rag = _get_rag()
        return rag.retrieve_with_filters(query, tradition=tradition, num_results=num_results)
    except Exception as e:
        return json.dumps({"error": str(e)})
