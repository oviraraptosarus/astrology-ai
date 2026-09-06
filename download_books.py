import os
from internetarchive import search_items, download

# Target directory
BOOKS_DIR = os.path.join(os.path.dirname(__file__), 'books')
os.makedirs(BOOKS_DIR, exist_ok=True)

# Classical Texts Identifiers or Search Queries on Archive.org
# Note: Archive.org has millions of texts, we rely on specific known identifiers or strong queries.
target_books = [
    {"query": 'title:("Brihat Parasara Hora Sastra") AND mediatype:texts', "filename": "bphs.pdf"},
    {"query": 'title:("Jataka Parijata") AND mediatype:texts', "filename": "jataka_parijata.pdf"},
    {"query": 'title:("Phaladeepika") AND mediatype:texts', "filename": "phaladeepika.pdf"},
    {"query": 'title:("Saravali") AND mediatype:texts', "filename": "saravali.pdf"},
    {"query": 'title:("Jaimini Sutras") AND mediatype:texts', "filename": "jaimini_sutras.pdf"},
    {"query": 'title:("Uttara Kalamrita") AND mediatype:texts', "filename": "uttara_kalamrita.pdf"}
]

def download_library():
    print(f"Downloading classical library to {BOOKS_DIR}...")
    
    for book in target_books:
        print(f"\nSearching for: {book['query']}")
        search = search_items(book['query'])
        
        # Take the first result
        result = None
        for item in search:
            result = item
            break
            
        if not result:
            print(f"-> No results found for query.")
            continue
            
        identifier = result['identifier']
        print(f"-> Found identifier: {identifier}. Downloading PDF...")
        
        # Download only PDF formats to save bandwidth
        download(identifier, formats=['Text PDF', 'Image PDF', 'Additional Text PDF', 'PDF'], destdir=BOOKS_DIR, verbose=True, no_directory=True)
        print(f"-> Successfully downloaded {identifier}.")
        
if __name__ == '__main__':
    download_library()
