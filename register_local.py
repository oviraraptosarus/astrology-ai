import os, json, hashlib, datetime
from download_manager import DownloadManager

mgr = DownloadManager()
books = [f for f in os.listdir('books') if f.endswith('.pdf')]
print(f'Found {len(books)} books')
cnt = 0
for b in books:
    p = os.path.join('books', b)
    with open(p, 'rb') as f:
        h = hashlib.sha256(f.read()).hexdigest()
    if not mgr._is_duplicate(h):
        mgr.registry.append({
            'title': b.replace('.pdf',''), 
            'author': 'Unknown', 
            'tradition': 'Parashari', 
            'source_type': 'classical_text', 
            'topic': ['A_FOUNDATIONAL_JYOTISHA'], 
            'quality': 'PRIORITY_1', 
            'provenance': 'LOCAL', 
            'document_hash': h, 
            'download_path': p, 
            'document_status': 'DOWNLOADED', 
            'text_extraction_status': 'PENDING', 
            'rag_status': 'PENDING'
        })
        cnt += 1
mgr.save_registry()
print(f'Registered {cnt} existing books.')
