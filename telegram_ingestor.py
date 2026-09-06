import os
import docx
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid

# Re-use DB_DIR from rag_ingestor but maybe a different persist dir for telegram, or the same.
# Let's use the advanced DB for telegram files as well to synthesize everything together.
DB_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db_advanced')
TELEGRAM_DIR = os.path.join(os.path.dirname(__file__), 'data', 'telegram_dump')

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def extract_text(file_path):
    text = ""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            
    elif ext == '.docx':
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
            
    elif ext == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading TXT {file_path}: {e}")
            
    return text

def ingest_telegram_files():
    if not os.path.exists(TELEGRAM_DIR):
        print(f"Telegram directory {TELEGRAM_DIR} not found. Run download_telegram_files.py first.")
        return

    files_to_ingest = [f for f in os.listdir(TELEGRAM_DIR) if f.endswith(('.pdf', '.docx', '.txt'))]
    if not files_to_ingest:
        print("No valid files (PDF/DOCX/TXT) found to ingest in Telegram dump.")
        return

    embeddings = get_embedding_model()
    # We use chroma_db_advanced so it merges with existing knowledge if needed, or keeps it isolated based on collection
    vector_store = Chroma(persist_directory=DB_DIR, embedding_function=embeddings, collection_name="astrology_knowledge")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    for filename in files_to_ingest:
        file_path = os.path.join(TELEGRAM_DIR, filename)
        print(f"Ingesting {filename}...")
        
        text = extract_text(file_path)
        if not text.strip():
            print(f"Warning: No text extracted from {filename}")
            continue
            
        chunks = text_splitter.create_documents(
            [text], 
            metadatas=[{"source": filename, "origin": "telegram_dump"}]
        )
        
        # Add in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            ids = [str(uuid.uuid4()) for _ in batch]
            vector_store.add_documents(documents=batch, ids=ids)
            print(f"  Added {i+len(batch)}/{len(chunks)} chunks for {filename}...")
            
    print("Telegram ingestion complete.")

if __name__ == '__main__':
    ingest_telegram_files()
