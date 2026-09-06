import os
import json
from internetarchive import search_items, get_item
from download_manager import DownloadManager
import time

TARGETS = [
    {"query": "Muhurta Chintamani astrology", "topic": "U_MUHURTA"},
    {"query": "Kalaprakasika astrology", "topic": "U_MUHURTA"},
    {"query": "Prashna Marga astrology", "topic": "T_PRASHNA"},
    {"query": "Shatpanchasika astrology", "topic": "T_PRASHNA"},
    {"query": "Sarvartha Chintamani astrology", "topic": "A_FOUNDATIONAL_JYOTISHA"},
    {"query": "Jataka Tattva astrology", "topic": "A_FOUNDATIONAL_JYOTISHA"},
    {"query": "Bhavartha Ratnakara astrology", "topic": "D_YOGAS"},
    {"query": "Bhrigu Sutras astrology", "topic": "A_FOUNDATIONAL_JYOTISHA"},
    {"query": "Daivajna Vallabha astrology", "topic": "T_PRASHNA"},
    {"query": "Sanketa Nidhi astrology", "topic": "A_FOUNDATIONAL_JYOTISHA"}
]

def run_acquisition():
    mgr = DownloadManager()
    
    for target in TARGETS:
        query = target["query"]
        topic = target["topic"]
        print(f"\n--- Searching for: {query} ---")
        
        try:
            search = search_items(query)
            results = list(search)[:3]  # Top 3 results
            
            found = False
            for result in results:
                item = get_item(result['identifier'])
                
                for file in item.files:
                    if file['name'].endswith('.pdf'):
                        url = f"https://archive.org/download/{item.identifier}/{file['name']}"
                        
                        metadata = {
                            "title": item.metadata.get('title', file['name']),
                            "author": item.metadata.get('creator', 'Unknown'),
                            "tradition": "Parashari", # Defaulting to Parashari for these texts
                            "language": item.metadata.get('language', 'Unknown'),
                            "source_type": "classical_text",
                            "topic": [topic],
                            "quality": "PRIORITY_2", # assuming translation
                            "provenance": "VERIFIED_IA",
                            "copyright_status": "PUBLIC_DOMAIN"
                        }
                        
                        success = mgr.download_pdf(url, metadata)
                        if success:
                            found = True
                            break # move to next target once one valid PDF is found
                            
                if found:
                    break
            
            if not found:
                print(f"Could not find a valid PDF for {query}")
                
            time.sleep(2) # rate limit
            
        except Exception as e:
            print(f"Error searching {query}: {e}")

if __name__ == '__main__':
    run_acquisition()
