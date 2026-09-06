import json
from llm_provider import LLMProvider
from ai_agent import agent_executor

class LLMEvaluator:
    def __init__(self):
        self.llm = LLMProvider.get_llm()
        
    def run_agent_test(self, session_id: str, birth_data: str, question: str) -> str:
        # First, run the initialization command
        print(f"\n[System] Initializing Chart for {birth_data}")
        init_msg = f"My birth details are {birth_data}. Please calculate my chart."
        agent_executor.invoke(
            {"messages": [("user", init_msg)]},
            config={"configurable": {"thread_id": session_id}}
        )
        
        # Now, ask the question
        print(f"[System] Asking: {question}")
        response = agent_executor.invoke(
            {"messages": [("user", question)]},
            config={"configurable": {"thread_id": session_id}}
        )
        
        return response["messages"][-1].content

if __name__ == '__main__':
    evaluator = LLMEvaluator()
    
    # Steve Jobs
    birth_data = "Feb 24, 1955 at 19:15 in San Francisco, CA"
    question = "Will I have a successful career? Explain why."
    
    try:
        output = evaluator.run_agent_test("test_eval_1", birth_data, question)
        print("\n--- AGENT RESPONSE ---")
        print(output)
        
        # Quality Checks
        forbidden_words = ["Shadbala", "evidence", "JSON", "modifier", "SynthesisResult", "reasoning_trace"]
        leaks = [w for w in forbidden_words if w.lower() in output.lower()]
        
        print("\n--- EVALUATION ---")
        if leaks:
            print(f"[FAIL] Machinery leaked! Found: {leaks}")
        else:
            print("[PASS] Response is natural and hides machinery.")
            
        if "upaya" in output.lower() or "remedy" in output.lower() or "mantra" in output.lower():
            print("[PASS] Output contains a remedy/upaya.")
        else:
            print("[FAIL] Output missing a remedy.")
            
    except Exception as e:
        print("Test failed with error:", e)
