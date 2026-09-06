import time

def check(name, fn):
    t0 = time.time()
    print(f"Importing {name}...", end=" ", flush=True)
    fn()
    print(f"Done in {time.time() - t0:.2f}s")

check("fastapi", lambda: __import__("fastapi"))
check("auth", lambda: __import__("auth"))
check("retrieval", lambda: __import__("retrieval"))
check("ai_agent", lambda: __import__("ai_agent"))
check("app", lambda: __import__("app"))
