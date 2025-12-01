# astro_calc.py
# Pure-Python astro helper for Python 3.12
# NOTE: This is an approximate / demo implementation, not precise Vedic astrology.

from datetime import datetime, timezone
from typing import Dict, Any

# 12 zodiac signs (for Moon sign etc.)
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Simple Vimshottari-style mapping (approximate)
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

# Lord for each of the 27 nakshatras (index 0–26)
NAKSHATRA_LORDS = [
    "Ketu",    # 0 Ashwini
    "Venus",   # 1 Bharani
    "Sun",     # 2 Krittika
    "Moon",    # 3 Rohini
    "Mars",    # 4 Mrigashira
    "Rahu",    # 5 Ardra
    "Jupiter", # 6 Punarvasu
    "Saturn",  # 7 Pushya
    "Mercury", # 8 Ashlesha
    "Ketu",    # 9 Magha
    "Venus",   # 10 Purva Phalguni
    "Sun",     # 11 Uttara Phalguni
    "Moon",    # 12 Hasta
    "Mars",    # 13 Chitra
    "Rahu",    # 14 Swati
    "Jupiter", # 15 Vishakha
    "Saturn",  # 16 Anuradha
    "Mercury", # 17 Jyeshtha
    "Ketu",    # 18 Mula
    "Venus",   # 19 Purva Ashadha
    "Sun",     # 20 Uttara Ashadha
    "Moon",    # 21 Shravana
    "Mars",    # 22 Dhanishta
    "Rahu",    # 23 Shatabhisha
    "Jupiter", # 24 Purva Bhadrapada
    "Saturn",  # 25 Uttara Bhadrapada
    "Mercury", # 26 Revati
]


def jd_from_datetime(dt: datetime) -> float:
    """
    Approximate Julian Day Number for a datetime.
    Good enough for relative calculations in this project.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    base = datetime(2000, 1, 1, tzinfo=timezone.utc)
    delta = dt - base
    jd = 2451544.5 + delta.days + (delta.seconds / 86400.0)
    return jd


def planet_longitude(jd: float, planet_name: str) -> float:
    """
    Fake ecliptic longitude (0–360) depending on JD and planet name.
    This is NOT physical astronomy – it's a deterministic placeholder.
    """
    name_str = str(planet_name)
    seed = sum(ord(c) for c in name_str)
    # simple pseudo-ephemeris
    lon = (jd * 0.1 + seed * 13.0) % 360.0
    return float(lon)


def ascendant(jd: float, latitude: float, longitude: float) -> float:
    """
    Dummy Ascendant based on JD and location.
    Again, this is just deterministic math for the project demo.
    """
    asc = (jd * 0.05 + longitude * 0.7 + latitude * 0.3) % 360.0
    return float(asc)


def get_house(planet_long: float, ref_long: float) -> int:
    """
    Equal-house system: 12 houses of 30 degrees each.
    ref_long is usually Ascendant or Moon longitude.
    Returns house number from 1 to 12.
    """
    diff = (planet_long - ref_long) % 360.0
    house = int(diff // 30.0) + 1
    if house < 1:
        house = 1
    elif house > 12:
        house = 12
    return house


def _compute_moon_sign(moon_lon: float) -> Dict[str, Any]:
    sign_index = int(moon_lon // 30) % 12
    sign_name = ZODIAC_SIGNS[sign_index]
    degree_in_rashi = moon_lon % 30.0
    return {
        "rashi_name": sign_name,
        "degree_in_rashi": round(degree_in_rashi, 2),
    }


def _compute_vimshottari(jd_birth: float, moon_lon: float) -> Dict[str, Any]:
    """
    VERY APPROXIMATE Vimshottari Mahadasha calculation.
    We just choose a starting lord from Moon's nakshatra,
    then approximate elapsed/remaining years from age.
    """
    # Nakshatra width
    nak_width = 360.0 / 27.0
    nak_index = int((moon_lon / nak_width) % 27)
    lord = NAKSHATRA_LORDS[nak_index]

    # Duration for that lord
    duration = DASHA_YEARS.get(lord, 0)

    # Approximate age in years from birth JD to "now"
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    jd_now = jd_from_datetime(now)
    age_years = max(0.0, (jd_now - jd_birth) / 365.25)

    # For demo: assume current Mahadasha is the nakshatra lord
    elapsed = min(age_years, float(duration))
    remaining = max(0.0, float(duration) - elapsed)

    return {
        "current_mahadasha": {
            "lord": lord,
            "duration_years": float(duration),
            "elapsed_in_current_years": round(elapsed, 2),
            "remaining_years": round(remaining, 2),
        }
    }


def compute_chart(jd: float, latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Main chart builder used by app.py and accuracy_tester.py.

    Returns a dict containing:
      - 'jd'
      - 'ascendant'
      - 'planets': { 'Moon': {'longitude', 'house'}, ... }
      - 'moon_sign': { 'rashi_name', 'degree_in_rashi' }
      - 'vimshottari': { 'current_mahadasha': {...} }
    """
    asc = ascendant(jd, latitude, longitude)

    planet_names = [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter",
        "Venus", "Saturn", "Rahu", "Ketu"
    ]

    planets = {}
    for p in planet_names:
        lon = planet_longitude(jd, p)
        house = get_house(lon, asc)
        planets[p] = {
            "longitude": lon,
            "house": house,
        }

    moon_lon = planets["Moon"]["longitude"]
    moon_sign = _compute_moon_sign(moon_lon)
    vimshottari = _compute_vimshottari(jd, moon_lon)

    return {
        "jd": jd,
        "latitude": latitude,
        "longitude": longitude,
        "ascendant": asc,
        "planets": planets,
        "moon_sign": moon_sign,
        "vimshottari": vimshottari,
    }
