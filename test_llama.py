import os
from llm_provider import LLMProvider
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def check_horoscope(sign: str) -> str:
    """Returns the daily horoscope for a given sign."""
    return f"{sign} will have a great day!"

def test_models():
    tools = [check_horoscope]
    
    print("--- Testing Groq LLaMA 3.3 ---")
    try:
        os.environ['GROQ_MODEL'] = 'llama3-70b-8192'
        groq_llm = LLMProvider._get_groq()
        groq_agent = create_react_agent(groq_llm, tools)
        res = groq_agent.invoke({"messages": [("user", "What is the horoscope for Aries?")]})
        print("Groq Response:", res["messages"][-1].content)
    except Exception as e:
        print("Groq Error:", e)

    print("\n--- Testing OpenRouter LLaMA 3.3 ---")
    try:
        os.environ['OPENROUTER_MODEL'] = 'meta-llama/llama-3.3-70b-instruct'
        or_llm = LLMProvider._get_openrouter(model=os.environ['OPENROUTER_MODEL'])
        or_agent = create_react_agent(or_llm, tools)
        res = or_agent.invoke({"messages": [("user", "What is the horoscope for Taurus?")]})
        print("OpenRouter Response:", res["messages"][-1].content)
    except Exception as e:
        print("OpenRouter Error:", e)

if __name__ == "__main__":
    test_models()
