"""
LOCAL UNCONSTRAINED LAUNCHER (Raw Grandmaster Mode)
===================================================
100% Raw, Uncensored, Unmoderated Local Execution.
Zero disclaimers, zero tone-policing, full mathematical Maraka/Ayurdaya payloads,
and direct authoritative Grandmaster synthesis.
"""

import os
import sys

# Force local unconstrained mode
os.environ["ASTRO_MODE"] = "unconstrained"

from modes import set_active_mode, get_active_mode
set_active_mode("unconstrained")

if __name__ == "__main__":
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "cli"
    
    print("\n" + "="*70)
    print(" ⚡ ASTROLOGY AI — LOCAL UNCONSTRAINED GRANDMASTER ENGINE ⚡")
    print(f" Mode: {get_active_mode().upper()} | Zero Disclaimers | Raw Precision")
    print("="*70 + "\n")
    
    if mode_arg == "server":
        import uvicorn
        uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
    else:
        from cli_chatbot import AstrologyCLIChatbot
        bot = AstrologyCLIChatbot()
        bot.active_mode = "grandmaster"
        bot.run()
