import os
import zipfile

def create_nano_zip():
    base_dir = r"e:\ASTROLOGY AI"
    zip_path = r"e:\ASTROLOGY AI\astrology_ai_nano.zip"
    
    # We will ONLY include these extensions
    include_exts = {'.py', '.md', '.json', '.txt'}
    
    # Exclude all huge or irrelevant folders
    exclude_dirs = {
        'venv', '__pycache__', 'chroma_db', 'chroma_db_advanced', 
        'books', 'data', '.vscode', 'cache', 'scratch', 'dependencies', 
        '.git', 'Claude_Skills'
    }
    
    print(f"Creating nano zip at {zip_path}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in include_exts):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_dir)
                    zipf.write(file_path, arcname)
                
    print("Done!")
    size_kb = os.path.getsize(zip_path) / 1024
    print(f"Size: {size_kb:.2f} KB ({size_kb/1024:.2f} MB)")

if __name__ == "__main__":
    create_nano_zip()
