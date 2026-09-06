
import sys, os
sys.path.insert(0, "E:/ASTROLOGY AI")
from retrieval import consult_astrology_books

print("Testing Classical Text Retrieval...")
try:
    res = consult_astrology_books("Gajakesari Yoga Jupiter Moon in Kendra", num_results=2)
    print("SUCCESS")
    print(res[:300])
except Exception as e:
    print("RAG query:", e)
