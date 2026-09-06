import os
import fitz  # PyMuPDF
import json
import re

class PDFProcessor:
    def __init__(self, books_dir="books", registry_file="source_registry.json"):
        self.books_dir = books_dir
        self.registry_file = registry_file
        
        if os.path.exists(self.registry_file):
            with open(self.registry_file, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = []

    def extract_text_and_pages(self, filepath):
        """
        Extracts text from a PDF, preserving page numbers.
        Returns a list of dicts: [{"page": int, "text": str}]
        """
        doc = fitz.open(filepath)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            
            # Clean up obvious OCR garbage or excessive newlines without destroying Sanskrit terms
            text = re.sub(r'\n+', '\n', text).strip()
            
            if len(text) > 50: # filter blank or almost blank pages
                pages_data.append({
                    "page": page_num + 1,
                    "text": text
                })
        
        doc.close()
        return pages_data

    def process_all_pending(self):
        for record in self.registry:
            if record.get("text_extraction_status") == "PENDING":
                filepath = record.get("download_path")
                if filepath and os.path.exists(filepath):
                    print(f"Processing {filepath}...")
                    try:
                        pages_data = self.extract_text_and_pages(filepath)
                        
                        # Save extracted text to a JSON file
                        extracted_dir = os.path.join("data", "extracted")
                        os.makedirs(extracted_dir, exist_ok=True)
                        
                        out_filename = os.path.basename(filepath).replace(".pdf", ".json")
                        out_path = os.path.join(extracted_dir, out_filename)
                        
                        with open(out_path, "w") as f:
                            json.dump({
                                "metadata": record,
                                "pages": pages_data
                            }, f, indent=2)
                            
                        record["text_extraction_status"] = "COMPLETED"
                        record["extracted_file"] = out_path
                    except Exception as e:
                        print(f"Failed to process {filepath}: {e}")
                        record["text_extraction_status"] = "FAILED"
                        
        with open(self.registry_file, "w") as f:
            json.dump(self.registry, f, indent=2)
            
if __name__ == '__main__':
    processor = PDFProcessor()
    processor.process_all_pending()
    print("Processing complete.")
