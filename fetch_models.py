import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv()

print("--- Groq Models ---")
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {groq_key}"}
    )
    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read())
        print([m["id"] for m in data["data"] if "llama" in m["id"] or "qwen" in m["id"] or "mixtral" in m["id"]])
    except Exception as e:
        print("Error:", e)

print("\n--- OpenRouter Models ---")
openrouter_key = os.getenv("OPENROUTER_API_KEY")
if openrouter_key:
    req = urllib.request.Request("https://openrouter.ai/api/v1/models")
    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read())
        print([m["id"] for m in data["data"] if "free" in m["id"]][:10])
    except Exception as e:
        print("Error:", e)
