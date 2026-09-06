import os
import json
import requests
import hashlib
from datetime import datetime

class DownloadManager:
    def __init__(self, books_dir="books", registry_file="source_registry.json"):
        self.books_dir = books_dir
        self.registry_file = registry_file
        os.makedirs(self.books_dir, exist_ok=True)
        
        if os.path.exists(self.registry_file):
            with open(self.registry_file, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = []

    def _get_hash(self, content):
        return hashlib.sha256(content).hexdigest()
        
    def _is_duplicate(self, file_hash):
        return any(r.get("document_hash") == file_hash for r in self.registry)
        
    def save_registry(self):
        with open(self.registry_file, "w") as f:
            json.dump(self.registry, f, indent=2)

    def download_pdf(self, url, metadata):
        """
        Downloads a PDF and registers it.
        metadata should be a dict with keys:
        title, author, tradition, language, source_type, topic (list), quality, provenance, copyright_status
        """
        print(f"Downloading {url}...")
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            content = response.content
            
            if not content.startswith(b'%PDF'):
                print("Error: Not a valid PDF file.")
                return False
                
            file_hash = self._get_hash(content)
            if self._is_duplicate(file_hash):
                print(f"Duplicate detected via hash {file_hash}. Skipping.")
                return False
                
            # Clean filename
            clean_title = "".join(c for c in metadata.get('title', 'Unknown') if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{clean_title.replace(' ', '_')}_{file_hash[:8]}.pdf"
            filepath = os.path.join(self.books_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(content)
                
            # Add to registry
            record = metadata.copy()
            record.update({
                "url": url,
                "download_path": filepath,
                "document_hash": file_hash,
                "download_timestamp": datetime.now().isoformat(),
                "document_status": "DOWNLOADED",
                "text_extraction_status": "PENDING",
                "rag_status": "PENDING"
            })
            self.registry.append(record)
            self.save_registry()
            print(f"Successfully downloaded {filename}")
            return True
            
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return False

if __name__ == '__main__':
    # Test
    mgr = DownloadManager()
    print(f"Registry has {len(mgr.registry)} entries.")
