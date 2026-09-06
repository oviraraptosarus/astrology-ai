
import os, glob, re

base_dir = "E:/ASTROLOGY AI"
files = glob.glob(os.path.join(base_dir, "*.py"))

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "Config.ayanamsha_swe_id()" in content and "config.py" not in file:
        
        # Insert import Config if not already present
        if "from config import Config" not in content and "import Config" not in content:
            # Find a place to insert it (after imports)
            # Find the line with `import swisseph`
            if "import swisseph" in content:
                content = content.replace("import swisseph as swe", "import swisseph as swe\nfrom config import Config")
            else:
                pass # Will require manual or better regex
                
        # In kp_engine.py, it stores SIDM_LAHIRI as the restore mode. Let's change it to Config.ayanamsha_swe_id()
        if "kp_engine.py" in file:
            content = content.replace('getattr(swe, "SIDM_LAHIRI")', 'Config.ayanamsha_swe_id()')
            pass # Handle kp_engine specifics
            
        else:
            content = content.replace("Config.ayanamsha_swe_id()", "Config.ayanamsha_swe_id()")
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {file}")
