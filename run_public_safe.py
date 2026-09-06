"""
PUBLIC CLIENT-SAFE LAUNCHER (Guardrailed & Legally Shielded Mode)
================================================================
Simulates the public published web service.
Includes ironclad legal disclaimer, anti-jailbreak immunity,
and ethical sattvic guidance.
"""

import os
import sys

# Force client_safe mode
os.environ["ASTRO_MODE"] = "client_safe"

from modes import set_active_mode, get_active_mode
set_active_mode("client_safe")

if __name__ == "__main__":
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "server"
    
    print("\n" + "="*70)
    print(" 🛡️ ASTROLOGY AI — PUBLIC CLIENT-SAFE SERVICE (BOUNDED) 🛡️")
    print(f" Mode: {get_active_mode().upper()} | Legal Shield Active | Guardrails Active")
    print("="*70 + "\n")
    
    if mode_arg == "server":
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
    else:
        from cli_chatbot import AstrologyCLIChatbot
        bot = AstrologyCLIChatbot()
        bot.active_mode = "client_safe"
        bot.run()
