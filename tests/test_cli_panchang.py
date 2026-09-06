import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cli_chatbot import AstrologyCLI, PRESETS

cli = AstrologyCLI()
print("Default Active Profile:", cli.active_profile["name"], "| City:", cli.active_profile["city"])
print("Coordinates:", cli.active_profile["lat"], cli.active_profile["lon"], cli.active_profile["tz"])

print("\nTesting dynamic Panchang for Mumbai:")
cli.show_drik_panchang("Mumbai")
