"""
Advanced RAG Pipeline with HyDE + Cross-Encoder Reranker
Phase 1 of 10/10 Engine Upgrades

Key improvements:
  - HyDE (Hypothetical Document Embeddings): LLM rewrites vague user queries into
    dense astrological terminology BEFORE hitting the vector store. This massively
    improves retrieval quality for Sanskrit text corpora.
  - Cross-Encoder Reranker: After hybrid retrieval (vector + BM25), a cross-encoder
    model scores (query, document) pairs and re-orders results by semantic relevance.
  - Proper RRF (Reciprocal Rank Fusion): Merges vector and BM25 ranked lists correctly.
"""
import os
import json
import logging
from typing import List, Optional, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
import uuid
import re
def clean_ocr_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'\s[~|^_°§©®]+\s', ' ', text)
    return text.strip()


logger = logging.getLogger(__name__)

DB_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db_advanced')
EXTRACTED_DIR = os.path.join(os.path.dirname(__file__), 'data', 'extracted')
RULES_DIR = os.path.join(os.path.dirname(__file__), 'data', 'rules')


def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def _get_cross_encoder():
    """Load the cross-encoder model for reranking (lazy-loaded singleton)."""
    try:
        from sentence_transformers import CrossEncoder
        return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
    except ImportError:
        logger.warning("sentence-transformers not installed. Reranking disabled.")
        return None
    except Exception as e:
        logger.warning(f"Cross-encoder load failed: {e}. Reranking disabled.")
        return None


_cross_encoder_instance = None

def get_cross_encoder():
    global _cross_encoder_instance
    if _cross_encoder_instance is None:
        _cross_encoder_instance = _get_cross_encoder()
    return _cross_encoder_instance


def hyde_rewrite(query: str) -> str:
    """
    HyDE: Hypothetical Document Embeddings.
    
    Instead of embedding the user's vague question, we ask an LLM to write
    a short hypothetical passage from an ancient astrology text that would
    ANSWER the question. We then embed THAT passage for retrieval.
    
    This bridges the vocabulary gap between user queries ("Will I be rich?")
    and Sanskrit corpus terminology ("Dhana yogas, 2nd house lord, Jupiter
    in Taurus aspecting 11th house...").
    """
    try:
        from llm_provider import LLMProvider
        llm = LLMProvider.get_llm("auto")
        
        hyde_prompt = f"""You are an expert Vedic astrologer. Write a short passage (3-5 sentences) 
that would appear in a classical Jyotisha text like BPHS or Phala Deepika,
explaining the astrological principles relevant to this question:

Question: {query}

Write only the hypothetical passage, no preamble. Use astrological terminology 
(house lords, yogas, planetary strengths, dashas, nakshatras, etc.)."""
        
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=hyde_prompt)])
        content = response.content
        if isinstance(content, list):
            parts = [p if isinstance(p, str) else p.get("text", "") for p in content]
            hyde_text = " ".join(parts).strip()
        else:
            hyde_text = str(content).strip()
        logger.info(f"HyDE expanded query: {hyde_text[:100]}...")
        return hyde_text
    except Exception as e:
        logger.warning(f"HyDE rewrite failed: {e}. Using original query.")
        return query


def reciprocal_rank_fusion(ranked_lists: List[List], k: int = 60) -> List:
    """
    Proper Reciprocal Rank Fusion (RRF) to merge multiple ranked lists.
    
    RRF score for document d = sum(1 / (k + rank_i(d))) across all lists.
    k=60 is the standard constant that balances high-rank vs low-rank documents.
    """
    scores = {}
    doc_objects = {}
    
    for ranked_list in ranked_lists:
        for rank, doc in enumerate(ranked_list, start=1):
            doc_id = doc.page_content[:200]  # Use content prefix as key
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
            doc_objects[doc_id] = doc
    
    # Sort by RRF score descending
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [doc_objects[doc_id] for doc_id in sorted_ids]


def cross_encoder_rerank(query: str, docs: List, top_n: int = 4) -> List:
    cross_encoder = get_cross_encoder()
    if not cross_encoder or not docs:
        return docs[:top_n]
    
    try:
        candidates = docs[:8]
        pairs = [(query, doc.page_content[:400]) for doc in candidates]
        scores = cross_encoder.predict(pairs, batch_size=8, show_progress_bar=False)
        ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in ranked[:top_n]]
    except Exception as e:
        logger.warning(f"Cross-encoder reranking failed: {e}. Returning unranked.")
        return docs[:top_n]


class AdvancedRAG:
    def __init__(self):
        self.embeddings = get_embedding_model()
        self.vector_store = Chroma(persist_directory=DB_DIR, embedding_function=self.embeddings)
        self.bm25_retriever = None
        self._initialize_bm25()

    def _initialize_bm25(self, force_rebuild=False):
        """Initialize BM25 with local disk caching to prevent memory leaks and slow startups. Includes cache validation and atomic writing."""
        import pickle
        import os
        cache_path = os.path.join(os.path.dirname(__file__), 'bm25_cache.pkl')
        
        try:
            vector_doc_count = self.vector_store._collection.count() if hasattr(self.vector_store, '_collection') else 0
        except Exception as e:
            logger.warning(f"Could not read vector store count: {e}")
            vector_doc_count = 0

        try:
            if os.path.exists(cache_path) and not force_rebuild:
                with open(cache_path, 'rb') as f:
                    cached_bm25 = pickle.load(f)
                
                cached_count = len(cached_bm25.docs) if hasattr(cached_bm25, 'docs') else 0
                if cached_count == vector_doc_count:
                    self.bm25_retriever = cached_bm25
                    return
                else:
                    logger.info(f"BM25 cache stale (DB has {vector_doc_count} docs, cache has {cached_count}). Rebuilding...")

            if vector_doc_count > 0:
                vector_docs = self.vector_store.get()
                if vector_docs and vector_docs.get("documents"):
                    self.bm25_retriever = BM25Retriever.from_texts(vector_docs["documents"])
                    self.bm25_retriever.k = 8  # Fetch more candidates for RRF
                    
                    # Atomic Write (P1 Bug Fix)
                    temp_path = cache_path + f".tmp.{os.getpid()}"
                    with open(temp_path, 'wb') as f:
                        pickle.dump(self.bm25_retriever, f)
                    os.replace(temp_path, cache_path)
                
        except Exception as e:
            logger.warning(f"BM25 Initialization skipped/failed: {e}")
        
    def ingest_structured_records(self):
        if not os.path.exists(EXTRACTED_DIR):
            print("No extracted data found.")
            return
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        for filename in os.listdir(EXTRACTED_DIR):
            if not filename.endswith(".json"):
                continue
                
            file_path = os.path.join(EXTRACTED_DIR, filename)
            with open(file_path, "r") as f:
                data = json.load(f)
                
            metadata = data.get("metadata", {})
            pages = data.get("pages", [])
            
            if metadata.get("rag_status") == "COMPLETED":
                print(f"Skipping {filename}, already in RAG.")
                continue
                
            print(f"Ingesting {filename}...")
            
            for page in pages:
                chunks = text_splitter.split_text(page["text"])
                
                for chunk in chunks:
                    topics = ",".join(metadata.get("topic", []))
                    
                    chunk_meta = {
                        "source_id": metadata.get("source_id", "Unknown"),
                        "title": metadata.get("title", "Unknown"),
                        "author": metadata.get("author", "Unknown"),
                        "tradition": metadata.get("tradition", "Unknown"),
                        "methodology": metadata.get("methodology", "Unknown"),
                        "domain": metadata.get("domain", "Unknown"),
                        "source_type": metadata.get("source_type", "Unknown"),
                        "quality": metadata.get("quality", "Unknown"),
                        "provenance": metadata.get("provenance", "Unknown"),
                        "document_hash": metadata.get("document_hash", "Unknown"),
                        "chapter": metadata.get("chapter", "Unknown"),
                        "page": page.get("page", 0),
                        "topic": topics,
                        "technique_ids": ",".join(metadata.get("technique_ids", [])),
                        "case_id": metadata.get("case_id", "None"),
                        "sensitive_traditional_prediction": "O_LONGEVITY_DEATH_MARAKA" in topics
                    }
                    
                    self.vector_store.add_texts(
                        texts=[chunk],
                        metadatas=[chunk_meta],
                        ids=[str(uuid.uuid4())]
                    )
                    
            print(f"Finished ingesting {filename}.")

    def retrieve_with_filters(
        self,
        query: str,
        tradition: str = None,
        methodology: str = None,
        topic: str = None,
        domain: str = None,
        source_quality: str = None,
        num_results: int = 4,
        use_hybrid: bool = True,
        use_hyde: bool = False,
        use_reranker: bool = True
    ):
        """
        Elite retrieval pipeline:
          1. HyDE query rewriting (LLM expands vague query to rich astrological text)
          2. Parallel vector search + BM25 keyword search
          3. Reciprocal Rank Fusion to merge ranked lists
          4. Cross-encoder reranking of final candidates
        """
        # ── Step 1: HyDE Query Rewriting ──────────────────────────────────────────
        retrieval_query = query
        hyde_query = query
        if use_hyde:
            hyde_query = hyde_rewrite(query)
            # We use hyde_query for vector search (semantic) and original for BM25 (keyword)
            retrieval_query = hyde_query

        # ── Step 2: Build metadata filter ────────────────────────────────────────
        filter_dict = {}
        if tradition:
            filter_dict["tradition"] = tradition
        if methodology:
            filter_dict["methodology"] = methodology
        if domain:
            filter_dict["domain"] = domain
        if source_quality:
            filter_dict["quality"] = source_quality
            
        search_kwargs = {"k": num_results * 3}  # Fetch more candidates for reranking
        if filter_dict:
            search_kwargs["filter"] = filter_dict

        # ── Step 3: Vector Search (with HyDE query) ───────────────────────────────
        vector_results = self.vector_store.similarity_search(retrieval_query, **search_kwargs)

        # ── Step 4: BM25 Keyword Search (with ORIGINAL query) ─────────────────────
        ranked_lists = [vector_results]
        if use_hybrid and self.bm25_retriever:
            try:
                # BM25 uses original query (keyword matching), not HyDE
                bm25_results = self.bm25_retriever.invoke(query)
                ranked_lists.append(bm25_results)
            except Exception as e:
                logger.warning(f"BM25 search failed: {e}")

        # ── Step 5: Reciprocal Rank Fusion ────────────────────────────────────────
        try:
            if len(ranked_lists) > 1:
                merged_docs = reciprocal_rank_fusion(ranked_lists)
            else:
                merged_docs = vector_results
        except Exception as e:
            logger.warning(f"RRF failed: {e}. Falling back to vector search.")
            merged_docs = vector_results

        # ── Step 6: Cross-Encoder Reranking ──────────────────────────────────────
        # Use original query for reranking (we want relevance to user's intent, not HyDE)
        if use_reranker and merged_docs:
            final_docs = cross_encoder_rerank(query, merged_docs, top_n=num_results)
        else:
            final_docs = merged_docs[:num_results]

        # ── Step 7: Format Output ─────────────────────────────────────────────────
        output = []
        for doc in final_docs:
            output.append({
                "text": doc.page_content,
                "metadata": doc.metadata
            })
        
        return json.dumps({
            "query": query,
            "hyde_query": hyde_query if use_hyde else None,
            "results": output
        }, indent=2)

    def analyze_contradictions(self, query: str, retrieved_docs: List[Dict]) -> Dict:
        """
        Takes retrieved documents and asks the LLM to identify differing opinions
        across the retrieved chunks on a specific astrological combination.
        """
        try:
            from llm_provider import LLMProvider
            llm = LLMProvider.get_llm("auto")
            
            docs_text = "\n\n".join([f"Source: {doc['metadata'].get('source', 'Unknown')}\n{doc['text']}" for doc in retrieved_docs])
            
            prompt = f"""You are an expert Vedic astrologer analyzing different texts for contradictions.
            
Query: {query}

Documents:
{docs_text}

Analyze the provided documents. Identify if there are contradicting ideologies, differing opinions, or different methodologies concerning the query. 
Summarize the varying opinions, mentioning the sources. If there are no contradictions, state that the texts agree.

Output your analysis as a structured summary."""
            
            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            if isinstance(content, list):
                parts = [p if isinstance(p, str) else p.get("text", "") for p in content]
                resp_text = " ".join(parts).strip()
            else:
                resp_text = str(content).strip()
            
            return {
                "contradiction_analysis": resp_text,
                "has_contradictions": "contradict" in resp_text.lower() or "differ" in resp_text.lower()
            }
        except Exception as e:
            logger.warning(f"Contradiction analysis failed: {e}")
            return {"contradiction_analysis": "Failed to analyze contradictions.", "has_contradictions": False}


if __name__ == '__main__':
    rag = AdvancedRAG()
    rag.ingest_structured_records()
