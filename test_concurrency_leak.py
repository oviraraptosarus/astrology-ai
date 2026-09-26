import threading
import time
import swisseph as swe
from panchangam_engine import PanchangamEngine
from transit_engine import TransitEngine
from datetime import datetime
import pytz

results = []

def thread1_func():
    # Thread 1 tries to calculate something with Lahiri (usually set in Config)
    # Simulate another thread setting a different sidereal mode during execution
    pass

# We will just write a simpler reproduction using direct SWISSEPH calls simulating the lock gap
def thread_lahiri():
    for _ in range(500):
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        time.sleep(0.0001)
        jd = swe.julday(2000, 1, 1, 12.0)
        res, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        results.append(("Lahiri", res[0]))

def thread_raman():
    for _ in range(500):
        swe.set_sid_mode(swe.SIDM_RAMAN)
        time.sleep(0.0001)
        jd = swe.julday(2000, 1, 1, 12.0)
        res, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        results.append(("Raman", res[0]))

t1 = threading.Thread(target=thread_lahiri)
t2 = threading.Thread(target=thread_raman)

t1.start()
t2.start()
t1.join()
t2.join()

# Now check for cross-contamination
lahiri_values = set(val for mode, val in results if mode == "Lahiri")
raman_values = set(val for mode, val in results if mode == "Raman")

print(f"Lahiri thread produced {len(lahiri_values)} unique positions: {list(lahiri_values)}")
print(f"Raman thread produced {len(raman_values)} unique positions: {list(raman_values)}")

if len(lahiri_values) > 1 or len(raman_values) > 1:
    print("CRITICAL: Concurrency state bleed detected without ephemeris_lock!")
