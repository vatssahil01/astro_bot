from astro_calc import compute_chart, jd_from_datetime
from datetime import datetime

print("\n--- Testing Astro Bot ---\n")

dt = datetime(1995, 2, 10, 14, 45)
jd = jd_from_datetime(dt)

chart = compute_chart(jd, 19.0760, 72.8777)

print("Moon Sign:", chart["moon_sign"])
print("\nAscendant:", chart["ascendant"])
print("\nHouses:", chart["houses"])
print("\nCurrent Mahadasha:", chart["vimshottari"]["current_mahadasha"])
