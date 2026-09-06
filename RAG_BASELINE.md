# RAG Baseline Audit

## Current Pipeline
The system currently has two parallel RAG ingestion processes:
1. **Basic RAG (`rag_ingestor.py`)**: Blindly ingests PDFs from the `books/` directory.
2. **Advanced RAG (`advanced_rag.py`)**: Ingests JSON files from `data/extracted/` with some basic metadata attached.

## Current Index & Embedding Model
- **Database**: ChromaDB (`chroma_db/` for basic, `chroma_db_advanced/` for advanced).
- **Embedding Model**: `HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")`.

## Current Chunking Strategy
- **Basic RAG**: Arbitrary `RecursiveCharacterTextSplitter` with `chunk_size=1000` and `chunk_overlap=200`.
- **Advanced RAG**: Also uses `RecursiveCharacterTextSplitter(1000, 200)` but iterates over JSON page records.
- **Flaw**: Chunking is purely based on character count, tearing through technical rules and slokas, destroying context.

## Current Metadata
- **Basic RAG**: Only tracks `{"source": filename}`.
- **Advanced RAG**: Tracks `source, author, tradition, source_type, quality, provenance, document_hash, page_number, topic, sensitive_traditional_prediction`. This is much better but still relies on arbitrary text chunks instead of structured rule records.

## Current Retrieval
- **File**: `retrieval.py` -> `advanced_rag.py`
- **Method**: Standard `similarity_search` via Chroma with basic exact-match filtering for `tradition`.
- **Flaw**: Pure embedding cosine similarity is insufficient for complex astrological configurations (e.g., "10th lord in 7th").

## Current Failures & Unverified Material
- The basic RAG is a "garbage corpus" of raw PDF text that will inevitably introduce noise and hallucinatory results if queried directly.
- Disconnected knowledge: Neither RAG system actively feeds into a domain-specific `ASTROLOGY_REASONING_PACK` with contradiction logic.
- Source conflicts are not modeled.

## Action Plan
- Do NOT destroy Chroma or `advanced_rag.py`. Keep them as the base.
- Stop using `rag_ingestor.py` and arbitrary chunking for future data.
- Refactor data extraction to yield **structured rules** and **semantic chunks** (by chapter/rule).
- Introduce a Reranker to the `advanced_rag.py` pipeline.
