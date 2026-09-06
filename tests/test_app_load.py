import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
print("FastAPI app loaded successfully! Routes count:", len(app.routes))
