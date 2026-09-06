import sys, os

scanner_path = "E:/ASTROLOGY AI/forward_timing_scanner.py"
with open(scanner_path, "r", encoding="utf-8") as f:
    code = f.read()

old_block = """        end_date = start_date + timedelta(days=months_ahead * 30.5)"""

new_block = """        if start_date.tzinfo is None:
            start_date = pytz.utc.localize(start_date)
        end_date = start_date + timedelta(days=months_ahead * 30.5)"""

code = code.replace(old_block, new_block)

with open(scanner_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Timezone comparison fix applied.")
