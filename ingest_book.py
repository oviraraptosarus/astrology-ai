#!/usr/bin/env python3
"""
Astrology AI — Automated Knowledge Base Ingestion & Learning Engine
Ingests PDFs, Markdown, TXT, or JSON files into ChromaDB + BM25 with
automatic tradition classification, domain tagging, and metadata validation.
"""

import os
import sys
import json
import uuid
import re
import hashlib
from typing import List, Dict, Any, Optional
# Lazy imports when ingesting
DB_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db_advanced')

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "BOOK_CATALOG.json")

TRADITION_KEYWORDS = {
    "PARASHARI": ["parashara", "bphs", "brihat", "phala deepika", "saravali", "hora", "santhanan", "varahamihira"],
    "JAIMINI": ["jaimini", "chara karaka", "arudha", "upapada", "sutras", "atmakaraka"],
    "KP": ["kp", "krishnamurti", "sub lord", "ruling planets", "cuspal interlinks"],
    "TAJAKA": ["tajaka", "varshaphala", "annual chart", "sahams", "ithasala"],
    "NADI": ["nadi", "bhrigu", "devakeralam", "dhruva"],
    "B.V. RAMAN": ["b.v. raman", "bv raman", "how to judge a horoscope", "three hundred important combinations"]
}

DOMAIN_KEYWORDS = {
    "CAREER": ["career", "profession", "10th house", "amatyakaraka", "job", "status", "dashamsha", "d10"],
    "MARRIAGE": ["marriage", "7th house", "spouse", "darakaraka", "navamsha", "d9", "upapada"],
    "WEALTH": ["wealth", "dhana", "2nd house", "11th house", "income", "assets", "hora", "d2"],
    "HEALTH": ["health", "disease", "6th house", "8th house", "12th house", "ayurdaya", "maraka", "d30"],
    "EDUCATION": ["education", "learning", "knowledge", "4th house", "5th house", "siddhamsa", "d24"],
    "SPIRITUALITY": ["moksha", "spirituality", "12th house", "9th house", "atmakaraka", "vimshamsha", "d20", "d60"]
}

def detect_tradition(text: str, filename: str) -> str:
    combined = (filename + " " + text[:2000]).lower()
    for trad, keywords in TRADITION_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return trad
    return "PARASHARI"  # Default classical tradition

def detect_domains(text: str) -> List[str]:
    text_lower = text.lower()
    matched = []
    for domain, kws in DOMAIN_KEYWORDS.items():
        if any(kw in text_lower for kw in kws):
            matched.append(domain)
    return matched or ["GENERAL"]

def compute_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def extract_text_from_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Extracts pages/sections from PDF, TXT, MD, or JSON.
    Returns: [{"page": int, "text": str}]
    """
    ext = os.path.splitext(filepath)[1].lower()
    pages_data = []

    if ext == ".pdf":
        import pymupdf
        doc = pymupdf.open(filepath)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            cleaned = re.sub(r'\n+', '\n', text).strip()
            if len(cleaned) > 50:  # Skip blank pages
                pages_data.append({"page": page_num + 1, "text": cleaned})
        doc.close()

    elif ext in [".txt", ".md"]:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()
        # Split into logical sections by double newlines or headers
        sections = re.split(r'\n(?=#{1,3}\s|\n\n)', full_text)
        for idx, sec in enumerate(sections, 1):
            cleaned = sec.strip()
            if len(cleaned) > 40:
                pages_data.append({"page": idx, "text": cleaned})

    elif ext == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for idx, item in enumerate(data, 1):
                t = str(item.get("text") or item.get("content") or item)
                pages_data.append({"page": idx, "text": t})
        elif isinstance(data, dict):
            pages = data.get("pages", [])
            if pages:
                pages_data = pages
            else:
                for k, v in data.items():
                    pages_data.append({"page": 1, "text": f"{k}: {v}"})

    return pages_data

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "INGESTED_REGISTRY.json")

class BookIngestionEngine:
    def __init__(self):
        self._rag = None
        self.registry = self._load_registry()

    def get_rag(self):
        if self._rag is None:
            from advanced_rag import AdvancedRAG
            self._rag = AdvancedRAG()
        return self._rag

    def _load_registry(self) -> Dict[str, Any]:
        if os.path.exists(REGISTRY_PATH):
            try:
                with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                return {}
        return {}

    def _save_registry(self):
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2)

    @staticmethod
    def get_ingested_sources() -> List[Dict[str, Any]]:
        if os.path.exists(REGISTRY_PATH):
            try:
                with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return list(data.values())
            except Exception:
                return []
        return []

    def list_ingested_sources(self) -> List[Dict[str, Any]]:
        return list(self.registry.values())

    def ingest_file(self, filepath: str, custom_author: str = None, custom_tradition: str = None, force: bool = False) -> Dict[str, Any]:
        """
        Ingests a single book/document into the ChromaDB vector store and rebuilds BM25 index.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File '{filepath}' does not exist.")

        filename = os.path.basename(filepath)
        file_hash = compute_file_hash(filepath)

        if not force and file_hash in self.registry:
            existing = self.registry[file_hash]
            return {
                "status": "SKIPPED",
                "message": f"'{filename}' was already ingested on {existing.get('ingested_at', 'earlier')}.",
                "chunks_count": existing.get("total_chunks", 0)
            }

        print(f"\n[Ingest Engine] Extracting text from '{filename}'...")
        pages_data = extract_text_from_file(filepath)
        if not pages_data:
            return {"status": "EMPTY", "message": f"No extractable text found in '{filename}'."}

        sample_text = " ".join([p["text"] for p in pages_data[:5]])
        tradition = custom_tradition or detect_tradition(sample_text, filename)
        author = custom_author or "Classical Authority"
        title = os.path.splitext(filename)[0].replace("_", " ").title()

        from langchain_text_splitters import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=150,
            separators=["\n\n", "\n", "।", ".", ";", " ", ""]
        )

        all_texts = []
        all_metas = []
        all_ids = []

        print(f"[Ingest Engine] Chunking and tagging metadata for {len(pages_data)} pages/sections...")
        for p in pages_data:
            page_num = p.get("page", 1)
            raw_text = p.get("text", "")
            chunks = text_splitter.split_text(raw_text)

            for c in chunks:
                domains = detect_domains(c)
                meta = {
                    "source_id": file_hash[:12],
                    "title": title,
                    "author": author,
                    "tradition": tradition,
                    "domain": ",".join(domains),
                    "page": page_num,
                    "filename": filename,
                    "quality": "PRIMARY_CLASSICAL"
                }
                all_texts.append(c)
                all_metas.append(meta)
                all_ids.append(str(uuid.uuid4()))

        # Batch insert to ChromaDB
        batch_size = 80
        total_chunks = len(all_texts)
        print(f"[Ingest Engine] Inserting {total_chunks} chunks into ChromaDB...")
        
        rag = self.get_rag()
        for i in range(0, total_chunks, batch_size):
            b_texts = all_texts[i:i+batch_size]
            b_metas = all_metas[i:i+batch_size]
            b_ids = all_ids[i:i+batch_size]
            rag.vector_store.add_texts(texts=b_texts, metadatas=b_metas, ids=b_ids)
            print(f"  -> Added {min(i+batch_size, total_chunks)}/{total_chunks} chunks...")

        # Rebuild BM25 Cache Atomically
        print("[Ingest Engine] Refreshing BM25 Keyword Index...")
        rag._initialize_bm25(force_rebuild=True)

        # Update Registry
        from datetime import datetime
        self.registry[file_hash] = {
            "title": title,
            "filename": filename,
            "filepath": os.path.abspath(filepath),
            "tradition": tradition,
            "author": author,
            "total_chunks": total_chunks,
            "ingested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save_registry()

        return {
            "status": "SUCCESS",
            "title": title,
            "tradition": tradition,
            "total_chunks": total_chunks,
            "file_hash": file_hash
        }

    def ingest_directory(self, dir_path: str, force: bool = False) -> List[Dict[str, Any]]:
        results = []
        valid_exts = [".pdf", ".txt", ".md", ".json"]
        for root, _, files in os.walk(dir_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in valid_exts):
                    full_path = os.path.join(root, file)
                    try:
                        res = self.ingest_file(full_path, force=force)
                        results.append(res)
                    except Exception as e:
                        results.append({"status": "ERROR", "file": file, "error": str(e)})
        return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_book.py <path_to_pdf_or_txt_or_folder> [--force]")
        sys.exit(1)

    target_path = sys.argv[1]
    force_flag = "--force" in sys.argv

    engine = BookIngestionEngine()
    if os.path.isdir(target_path):
        print(f"Ingesting all documents from directory: {target_path}")
        res = engine.ingest_directory(target_path, force=force_flag)
        print(f"\nCompleted ingesting directory. Results:\n{json.dumps(res, indent=2)}")
    else:
        res = engine.ingest_file(target_path, force=force_flag)
        print(f"\nIngestion Result:\n{json.dumps(res, indent=2)}")
