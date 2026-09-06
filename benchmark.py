import json
from advanced_rag import AdvancedRAG

def run_benchmark():
    rag = AdvancedRAG()
    queries = [
        "What does the 10th lord in the 7th house indicate for career?",
        "How is Chara Dasha calculated?",
        "What are the effects of Jupiter transiting the 7th house?"
    ]
    
    print("--- RETRIEVAL BENCHMARK ---\n")
    for q in queries:
        print(f"QUERY: {q}")
        res = rag.retrieve_with_filters(q, num_results=2, use_hybrid=True)
        res_json = json.loads(res)
        results = res_json.get("results", [])
        print(f"Returned {len(results)} chunks.")
        for i, r in enumerate(results):
            source = r.get("metadata", {}).get("source", "Unknown")
            print(f"  Result {i+1}: from '{source}'")
        print("-" * 40)
        
if __name__ == "__main__":
    run_benchmark()
