import os
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid

BOOKS_DIR = os.path.join(os.path.dirname(__file__), 'books')
DB_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db')

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def ingest_books():
    if not os.path.exists(BOOKS_DIR):
        print(f"Books directory {BOOKS_DIR} not found.")
        return

    pdf_files = [f for f in os.listdir(BOOKS_DIR) if f.endswith('.pdf')]
    if not pdf_files:
        print("No PDFs found to ingest.")
        return

    embeddings = get_embedding_model()
    vector_store = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    for filename in pdf_files:
        file_path = os.path.join(BOOKS_DIR, filename)
        print(f"Ingesting {filename}...")
        
        text = extract_text_from_pdf(file_path)
        if not text:
            print(f"Warning: No text extracted from {filename}")
            continue
            
        chunks = text_splitter.create_documents([text], metadatas=[{"source": filename}])
        
        # Add in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            ids = [str(uuid.uuid4()) for _ in batch]
            vector_store.add_documents(documents=batch, ids=ids)
            print(f"  Added {i+len(batch)}/{len(chunks)} chunks...")
            
    print("Ingestion complete.")

if __name__ == '__main__':
    ingest_books()
