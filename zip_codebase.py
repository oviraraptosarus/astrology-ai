import os
import zipfile

def create_small_zip():
    base_dir = r"e:\ASTROLOGY AI"
    zip_path = r"e:\ASTROLOGY AI\astrology_ai_small.zip"
    
    exclude_dirs = {
        'venv', '__pycache__', 'chroma_db', 'chroma_db_advanced', 
        'books', 'data', '.vscode', 'cache', 'scratch', 'dependencies', '.git'
    }
    exclude_exts = {'.zip', '.sqlite', '.sqlite-wal', '.sqlite-shm', '.db'}
    
    print(f"Creating small zip at {zip_path}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in exclude_exts):
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_dir)
                zipf.write(file_path, arcname)
                
    print("Done!")
    print(f"Size: {os.path.getsize(zip_path) / 1024:.2f} KB")

if __name__ == "__main__":
    create_small_zip()
