import swisseph as swe
from datetime import datetime

# Zodiac Signs (Tropical)
RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Vimshottari Dasha sequence (tropical Moon version)
VIMSHOTTARI_SEQUENCE = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
]

# Dasha durations in years
VIMSHOTTARI_SEQUENCE_DURATIONS = {
    'Ketu': 7,
    'Venus': 20,
    'Sun': 6,
    'Moon': 10,
    'Mars': 7,
    'Rahu': 18,
    'Jupiter': 16,
    'Saturn': 19,
    'Mercury': 17
}


def normalize_angle(a):
    return a % 360


def planet_longitude(jd, planet):
    """Swiss Ephemeris safe longitude extraction."""
    try:
        res = swe.calc_ut(jd, planet)

        # New format: (xx, flags)
        if isinstance(res, tuple) and len(res) == 2:
            xx, _ = res
            lon = xx[0] if isinstance(xx, (list, tuple)) else float(xx)

        # Old format
        else:
            lon = float(res[0])

        return normalize_angle(lon)

    except Exception as e:
        print("Planet error:", e)
        return 0.0


def ascendant(jd, lat, lon):
    """
    Swiss Ephemeris uses WEST POSITIVE.
    Indian longitude (east) must be NEGATED.
    """
    try:
        casas, ascmc = swe.houses_ex(jd, lat, -lon)
        return normalize_angle(ascmc[0])
    except Exception as e:
        print("Ascendant error:", e)
        return 0.0


def get_house(longitude, asc_longitude):
    """Equal 30° houses system (your original logic)."""
    diff = normalize_angle(longitude - asc_longitude)
    house = int(diff // 30) + 1
    return min(max(house, 1), 12)


def moon_sign(moon_lon):
    idx = int(moon_lon // 30)
    idx = min(idx, 11)
    name = RASHIS[idx]
    degree = moon_lon - idx * 30
    return {"rashi_name": name, "degree_in_rashi": round(degree, 3)}


def nakshatra_from_longitude(moon_lon):
    NAMES = [
        "Ashwini","Bharani","Krittika","Rohini","Mrigashirsha",
        "Ardra","Punarvasu","Pushya","Ashlesha","Magha",
        "Purva Phalguni","Uttara Phalguni","Hasta","Chitra",
        "Swati","Vishakha","Anuradha","Jyeshtha","Mula",
        "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta",
        "Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
    ]
    idx = int(moon_lon // (360/27))
    idx = min(idx, 26)
    return NAMES[idx], idx


def jd_from_datetime(dt):
    return swe.utc_to_jd(dt.year, dt.month, dt.day,
                         dt.hour, dt.minute, dt.second,
                         swe.GREG_CAL)[1]


def compute_vimshottari_for_birth(jd_birth, now_dt=None):
    if now_dt is None:
        now_dt = datetime.utcnow()

    now_jd = jd_from_datetime(now_dt)
    elapsed_years = (now_jd - jd_birth) / 365.25

    moon_lon = planet_longitude(jd_birth, swe.MOON)
    nak_name, nak_idx = nakshatra_from_longitude(moon_lon)

    deg_in_nak = moon_lon % (360/27)
    fraction_done = deg_in_nak / (360/27)

    start_lord = (nak_idx // 3) % 9

    full_period = VIMSHOTTARI_SEQUENCE_DURATIONS[VIMSHOTTARI_SEQUENCE[start_lord]]
    remaining = (1 - fraction_done) * full_period

    timeline = []
    t = remaining

    # Current dasha
    timeline.append({
        "lord": VIMSHOTTARI_SEQUENCE[start_lord],
        "duration_years": remaining,
        "start_year": 0.0,
        "end_year": remaining
    })

    # Next dashas
    i = (start_lord + 1) % 9
    while len(timeline) < 9:
        lord = VIMSHOTTARI_SEQUENCE[i]
        dur = VIMSHOTTARI_SEQUENCE_DURATIONS[lord]
        timeline.append({
            "lord": lord,
            "duration_years": dur,
            "start_year": t,
            "end_year": t + dur
        })
        t += dur
        i = (i + 1) % 9

    current_md = None
    for p in timeline:
        if p["start_year"] <= elapsed_years < p["end_year"]:
            current_md = {
                "lord": p["lord"],
                "duration_years": p["duration_years"],
                "elapsed_in_current_years": elapsed_years - p["start_year"],
                "remaining_years": p["end_year"] - elapsed_years
            }
            break

    return {
        "starting_nakshatra": nak_name,
        "timeline": timeline,
        "current_mahadasha": current_md,
        "elapsed_years": elapsed_years
    }


def compute_chart(jd, lat, lon):
    asc = ascendant(jd, lat, lon)

    planets = {
        "Sun": planet_longitude(jd, swe.SUN),
        "Moon": planet_longitude(jd, swe.MOON),
        "Mars": planet_longitude(jd, swe.MARS),
        "Mercury": planet_longitude(jd, swe.MERCURY),
        "Jupiter": planet_longitude(jd, swe.JUPITER),
        "Venus": planet_longitude(jd, swe.VENUS),
        "Saturn": planet_longitude(jd, swe.SATURN),
        "Rahu": planet_longitude(jd, swe.MEAN_NODE),
        "Ketu": normalize_angle(planet_longitude(jd, swe.MEAN_NODE) + 180),
    }

    houses = {p: get_house(lon, asc) for p, lon in planets.items()}

    md = compute_vimshottari_for_birth(jd)
    ms = moon_sign(planets["Moon"])

    return {
        "planet_positions": planets,
        "ascendant": asc,
        "houses": houses,
        "moon_sign": ms,
        "vimshottari": md
    }
