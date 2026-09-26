import threading
import time
import swisseph as swe

# swe is a global C extension. We simulate concurrent access.

def thread_lahiri():
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    time.sleep(0.5) # Simulate calculation time
    # Check what mode is currently set by computing Ascendant
    jd = swe.julday(2000, 1, 1, 12.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    res, _ = swe.calc_ut(jd, swe.SUN, flags)
    print(f"Lahiri Thread Got Sun Longitude: {res[0]:.6f}")

def thread_kp():
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    time.sleep(0.5)
    jd = swe.julday(2000, 1, 1, 12.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    res, _ = swe.calc_ut(jd, swe.SUN, flags)
    print(f"KP Thread Got Sun Longitude: {res[0]:.6f}")

print("Sequential Test:")
thread_lahiri()
thread_kp()

print("\nConcurrent Test:")
t1 = threading.Thread(target=thread_lahiri)
t2 = threading.Thread(target=thread_kp)
t1.start()
# Wait a tiny bit to ensure t1 sets mode before t2 starts, but t2 sets mode before t1 calculates
time.sleep(0.1)
t2.start()

t1.join()
t2.join()
