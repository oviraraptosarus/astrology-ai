import os
import json
import uuid
from PyPDF2 import PdfReader
from llm_provider import LLMProvider
from langchain_core.messages import SystemMessage, HumanMessage

RULES_DIR = os.path.join(os.path.dirname(__file__), 'data', 'rules')
CASES_DIR = os.path.join(os.path.dirname(__file__), 'data', 'cases')
os.makedirs(RULES_DIR, exist_ok=True)
os.makedirs(CASES_DIR, exist_ok=True)

llm = LLMProvider.get_llm()

EXTRACTION_PROMPT = """
You are an expert Vedic Astrology knowledge extractor.
Analyze the following text from an astrology book.
Extract any distinct astrological rules, definitions, or principles into a JSON array of objects.

Follow this exact schema for each rule:
{
  "rule_id": "RULE-<generate_a_uuid>",
  "name": "Short descriptive name",
  "tradition": "Parashari|Jaimini|Tajaka|Unknown",
  "domain": ["career", "marriage", "wealth", "etc"],
  "conditions": ["List of requirements for the rule to apply"],
  "exceptions": ["List of things that cancel the rule"],
  "modifiers": ["Factors that alter the result"],
  "timing": ["Dasha/Transit timing indications"],
  "vargas": ["Relevant divisional charts"],
  "rule_category": "FACT|DEFINITION|CALCULATION|CLASSICAL_RULE|PRACTITIONER_METHOD|CASE_OBSERVATION|UNVERIFIED",
  "explanation": "Detailed explanation of what the rule means."
}

Do NOT invent rules. If the text does not contain any concrete rules, return an empty array [].
Return ONLY valid JSON.
"""

def process_pdf(pdf_path: str, source_id: str, tradition: str):
    print(f"Processing {pdf_path}...")
    reader = PdfReader(pdf_path)
    
    # Process page by page, grouping a few pages together for context
    chunk_text = ""
    chunk_pages = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            chunk_text += f"\n--- Page {i+1} ---\n{text}"
            chunk_pages.append(i+1)
            
        # Send chunks of ~3 pages to LLM
        if len(chunk_pages) >= 3 or i == len(reader.pages) - 1:
            if not chunk_text.strip():
                continue
                
            print(f"  Extracting rules from pages {chunk_pages}...")
            
            try:
                messages = [
                    SystemMessage(content=EXTRACTION_PROMPT),
                    HumanMessage(content=f"Source ID: {source_id}\nTradition: {tradition}\nText:\n{chunk_text}")
                ]
                response = llm.invoke(messages).content
                
                # Cleanup markdown formatting if present
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                    
                rules = json.loads(response.strip())
                
                # Save extracted rules
                if rules and isinstance(rules, list):
                    for rule in rules:
                        # Add provenance
                        rule["provenance"] = "AI_EXTRACTED_PENDING_VERIFICATION"
                        rule["source_id"] = source_id
                        rule["pages"] = chunk_pages
                        
                        rule_id = rule.get("rule_id", f"RULE-{uuid.uuid4()}")
                        with open(os.path.join(RULES_DIR, f"{rule_id}.json"), "w") as f:
                            json.dump(rule, f, indent=2)
                            
                    print(f"    -> Extracted {len(rules)} rules.")
            except Exception as e:
                print(f"    -> Failed to extract from chunk: {e}")
                
            # Reset
            chunk_text = ""
            chunk_pages = []

if __name__ == "__main__":
    # Example usage:
    # process_pdf("books/Phaladeepika.pdf", "SRC-PHALADEEPIKA-001", "Parashari")
    print("Knowledge Extractor ready.")
