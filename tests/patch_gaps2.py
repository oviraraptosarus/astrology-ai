import sys, os, re

# 1. Patch advanced_rag.py
rag_path = "E:/ASTROLOGY AI/advanced_rag.py"
with open(rag_path, "r", encoding="utf-8") as f:
    rag_content = f.read()

cleaner_def = """
def clean_ocr_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'(\\w+)-\\s*\\n\\s*(\\w+)', r'\\1\\2', text)
    text = re.sub(r'[ \\t]+', ' ', text)
    text = re.sub(r'\\n{3,}', '\\n\\n', text)
    text = re.sub(r'[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f-\\x9f]', '', text)
    text = re.sub(r'\\s[~|^_°§©®]+\\s', ' ', text)
    return text.strip()
"""

if "def clean_ocr_text" not in rag_content:
    rag_content = rag_content.replace("import uuid", "import uuid\nimport re" + cleaner_def)
    rag_content = rag_content.replace(
        'content = page.get("text", "")',
        'content = clean_ocr_text(page.get("text", ""))'
    )
    with open(rag_path, "w", encoding="utf-8") as f:
        f.write(rag_content)
    print("advanced_rag.py patched with clean_ocr_text.")

# 2. Patch rectification_engine.py with Prashna Horary fallback
rect_path = "E:/ASTROLOGY AI/rectification_engine.py"
with open(rect_path, "r", encoding="utf-8") as f:
    rect_content = f.read()

old_rect_return = """        return {
            "original_birth_time": local_dt.strftime("%Y-%m-%d %H:%M %Z"),
            "rectified_birth_time": rectified_dt.strftime("%Y-%m-%d %H:%M %Z"),
            "shift_minutes": best_shift,
            "confidence": round(confidence, 1),
            "best_score": round(best_score, 4),
            "peak_sharpness": round(sharpness, 4),
            "candidate_count": total_steps,
            "event_scores": best_scores_detail,
            "score_curve": curve,
            "debug_error": diag_error
        }"""

new_rect_return = """        prashna_fallback = None
        if confidence < 50.0:
            prashna_fallback = {
                "recommended": True,
                "reason": f"Rectification confidence is low ({round(confidence, 1)}%).",
                "guidance": "In classical Vedic astrology, when natal birth time cannot be calibrated definitively, Prashna Kundli (Horary chart of the exact moment the query is asked) should be used."
            }

        return {
            "original_birth_time": local_dt.strftime("%Y-%m-%d %H:%M %Z"),
            "rectified_birth_time": rectified_dt.strftime("%Y-%m-%d %H:%M %Z"),
            "shift_minutes": best_shift,
            "confidence": round(confidence, 1),
            "best_score": round(best_score, 4),
            "peak_sharpness": round(sharpness, 4),
            "candidate_count": total_steps,
            "event_scores": best_scores_detail,
            "score_curve": curve,
            "prashna_fallback": prashna_fallback,
            "debug_error": diag_error
        }"""

if "prashna_fallback" not in rect_content:
    rect_content = rect_content.replace(old_rect_return, new_rect_return)
    with open(rect_path, "w", encoding="utf-8") as f:
        f.write(rect_content)
    print("rectification_engine.py patched with Prashna fallback.")
