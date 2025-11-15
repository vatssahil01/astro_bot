"""
Vedic Astrology Calculator using Swiss Ephemeris
Computes planetary positions, ascendant, moon sign, Manglik dosha, and Vimshottari dasha
"""

# Try the common module names for Swiss Ephemeris; prefer `swisseph` but fall back to `pyswisseph`.
# try:
import swisseph as swe
# except Exception:
#     try:
#         import pyswisseph as swe
#     except Exception:
#         raise ImportError(
#             "Swiss Ephemeris Python bindings not found; install with: pip install pyswisseph"
#         )

from datetime import datetime, timedelta
import pytz
import math


# Initialize Swiss Ephemeris
try:
    swe.set_ephe_path('/usr/share/ephe')
except:
    pass  # Path might not exist on all systems


# Constants for planets
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,  # North node
    'Ketu': None  # Calculated as Rahu + 180
}

# Zodiac signs (Rashis) - 12 signs, 30° each
RASHIS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# 27 Nakshatras for Vimshottari dasha
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purvashadha', 'Uttarashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

# Vimshottari dasha sequence (9 lords) and their periods in years
VIMSHOTTARI_SEQUENCE = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

# Manglik rule - houses that trigger Manglik dosha
MANGLIK_HOUSES = [1, 2, 4, 7, 8, 12]


def normalize_angle(angle):
    """Normalize angle to 0-360 range"""
    return angle % 360.0


def to_utc(dt_naive, tz_name):
    """Convert naive datetime in given timezone to UTC datetime"""
    tz = pytz.timezone(tz_name)
    dt_local = tz.localize(dt_naive)
    dt_utc = dt_local.astimezone(pytz.utc)
    return dt_utc.replace(tzinfo=None)


def jd_from_datetime(dt_utc):
    """Convert UTC datetime to Julian Day number"""
    # Julian Day for 2000-01-01 12:00:00 UT is 2451545.0
    y = dt_utc.year
    m = dt_utc.month
    d = dt_utc.day
    h = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    
    # Adjust for months < 3
    if m <= 2:
        y -= 1
        m += 12
    
    A = y // 100
    B = 2 - A + (A // 4)
    
    JD = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + (h / 24.0) + B - 1524.5
    return JD


def planet_longitude(jd, planet_const):
    """Get planet longitude in zodiacal degrees (0-360) for given Julian Day"""
    try:
        result = swe.calc_ut(jd, planet_const)
        lon = result[0]  # longitude
        return normalize_angle(lon)
    except Exception as e:
        print(f"Error calculating planet longitude: {e}")
        return 0.0


def ascendant(jd, lat_deg, lon_deg):
    """Calculate Ascendant (Lagna) for given JD and location"""
    try:
        # Swiss Ephemeris houses_ex for Placidus houses
        cusps, ascmc = swe.houses_ex(jd, lat_deg, lon_deg, b'P')  # Placidus
        asc = ascmc[0]  # Ascendant is first element
        return normalize_angle(asc)
    except Exception as e:
        print(f"Error calculating ascendant: {e}")
        return 0.0


def moon_sign(moon_longitude):
    """
    Determine Moon Rashi (sign) from Moon longitude.
    Each rashi spans 30 degrees.
    """
    sign_index = int(moon_longitude / 30)
    sign_index = min(sign_index, 11)  # ensure 0-11
    
    rashi_name = RASHIS[sign_index]
    rashi_start = sign_index * 30
    rashi_end = rashi_start + 30
    degree_in_rashi = moon_longitude - rashi_start
    
    return {
        'rashi_name': rashi_name,
        'rashi_index': sign_index,
        'degree_in_rashi': round(degree_in_rashi, 3),
        'full_longitude': round(moon_longitude, 3)
    }


def get_house(longitude, ascendant_deg):
    """
    Calculate house number (1-12) from longitude and ascendant.
    Uses simple 30-degree house system (each house = 30°).
    """
    # Normalize both to 0-360
    lon = normalize_angle(longitude)
    asc = normalize_angle(ascendant_deg)
    
    # Calculate house position
    diff = normalize_angle(lon - asc)
    house = int(diff / 30) + 1
    
    if house == 0:
        house = 12
    elif house > 12:
        house = house % 12
        if house == 0:
            house = 12
    
    return house


def get_nakshatra(moon_longitude):
    """
    Determine Nakshatra from Moon longitude.
    Each nakshatra spans 13°20' (13.333...)
    """
    nak_size = 360.0 / 27  # 13.333...
    nak_index = int(moon_longitude / nak_size)
    nak_index = min(nak_index, 26)
    
    nakshatra_name = NAKSHATRAS[nak_index]
    nak_start = nak_index * nak_size
    degree_in_nak = moon_longitude - nak_start
    
    return {
        'nakshatra_name': nakshatra_name,
        'nakshatra_index': nak_index,
        'degree_in_nakshatra': round(degree_in_nak, 3)
    }


def is_manglik(jd, lat_deg, lon_deg):
    """
    Check if native is Manglik (Mars dosha).
    Mars in houses 1, 2, 4, 7, 8, or 12 from Ascendant or Moon => Manglik
    """
    # Get positions
    mars_lon = planet_longitude(jd, swe.MARS)
    asc_lon = ascendant(jd, lat_deg, lon_deg)
    moon_lon = planet_longitude(jd, swe.MOON)
    
    # Determine Mars house from Ascendant
    mars_house_from_asc = get_house(mars_lon, asc_lon)
    
    # Determine Mars house from Moon
    mars_house_from_moon = get_house(mars_lon, moon_lon)
    
    # Check trigger
    is_manglik_by_lagna = mars_house_from_asc in MANGLIK_HOUSES
    is_manglik_by_moon = mars_house_from_moon in MANGLIK_HOUSES
    
    return {
        'mars_longitude': round(mars_lon, 3),
        'mars_house_from_lagna': mars_house_from_asc,
        'mars_house_from_moon': mars_house_from_moon,
        'is_manglik_by_lagna': is_manglik_by_lagna,
        'is_manglik_by_moon': is_manglik_by_moon,
        'is_manglik': is_manglik_by_lagna or is_manglik_by_moon
    }


def compute_vimshottari_for_birth(jd, birth_jd=None):
    """
    Compute Vimshottari dasha from birth.
    Uses Moon nakshatra to determine starting point.
    Computes current dasha from current date.
    """
    # Get Moon position at birth
    moon_lon_birth = planet_longitude(jd, swe.MOON)
    
    # Determine starting nakshatra
    nak_info = get_nakshatra(moon_lon_birth)
    start_nak_idx = nak_info['nakshatra_index']
    
    # In Vimshottari, the lord of the birth nakshatra determines the starting dasha
    # Each nakshatra is ruled by a dasha lord in sequence
    # Nakshatras 0-2: Ketu, 3-5: Venus, 6-8: Sun, etc.
    dasha_lord_idx = (start_nak_idx // 3) % 9
    
    # Remaining years in starting dasha (based on degree in nakshatra)
    degree_in_nak = nak_info['degree_in_nakshatra']
    nak_size = 360.0 / 27
    fraction_complete = degree_in_nak / nak_size
    
    start_lord_period = VIMSHOTTARI_YEARS[dasha_lord_idx]
    elapsed_in_current = fraction_complete * start_lord_period
    remaining_in_current = start_lord_period - elapsed_in_current
    
    # Build timeline from birth
    timeline = []
    t = 0.0
    i = dasha_lord_idx
    
    # First dasha (partial)
    timeline.append({
        'lord': VIMSHOTTARI_SEQUENCE[i],
        'duration_years': start_lord_period,
        'start_year': 0.0,
        'end_year': remaining_in_current
    })
    t = remaining_in_current
    i = (i + 1) % 9
    
    # Add subsequent dashas
    while len(timeline) < 30:
        dur = VIMSHOTTARI_YEARS[i]
        timeline.append({
            'lord': VIMSHOTTARI_SEQUENCE[i],
            'duration_years': dur,
            'start_year': t,
            'end_year': t + dur
        })
        t += dur
        i = (i + 1) % 9
    
    # Calculate elapsed years from birth to now
    now_jd = jd_from_datetime(datetime.utcnow())
    elapsed_years = (now_jd - jd) / 365.25
    
    # Find current dasha
    current = None
    for seg in timeline:
        if seg['start_year'] <= elapsed_years < seg['end_year']:
            current = seg.copy()
            current['elapsed_in_current_years'] = round(elapsed_years - seg['start_year'], 3)
            current['remaining_years'] = round(seg['end_year'] - elapsed_years, 3)
            break
    
    return {
        'moon_longitude_at_birth': round(moon_lon_birth, 3),
        'starting_nakshatra': nak_info['nakshatra_name'],
        'starting_nakshatra_index': start_nak_idx,
        'timeline': timeline,
        'elapsed_years': round(elapsed_years, 3),
        'current_mahadasha': current
    }


def compute_chart(dt_naive, tz_name, lat_deg, lon_deg):
    """
    Compute complete astrological chart for given birth details.
    
    Args:
        dt_naive: datetime object (naive, without timezone)
        tz_name: timezone name (e.g., 'Asia/Kolkata')
        lat_deg: latitude in decimal degrees
        lon_deg: longitude in decimal degrees
    
    Returns:
        Dictionary with all computed astrological data
    """
    # Convert to UTC and get Julian Day
    dt_utc = to_utc(dt_naive, tz_name)
    jd = jd_from_datetime(dt_utc)
    
    # Calculate all planets
    planets = {}
    for name, pconst in PLANETS.items():
        if pconst is None:
            # Ketu = Rahu + 180
            rahu_lon = planet_longitude(jd, swe.MEAN_NODE)
            ketu_lon = normalize_angle(rahu_lon + 180.0)
            planets['Ketu'] = ketu_lon
        else:
            planets[name] = planet_longitude(jd, pconst)
    
    # Calculate Ascendant
    asc = ascendant(jd, lat_deg, lon_deg)
    
    # Calculate Moon sign
    moon_lon = planets['Moon']
    moon_rashi = moon_sign(moon_lon)
    
    # Calculate Manglik dosha
    manglik = is_manglik(jd, lat_deg, lon_deg)
    
    # Calculate Vimshottari dasha
    dasha = compute_vimshottari_for_birth(jd)
    
    return {
        'jd': jd,
        'planets': planets,
        'ascendant': asc,
        'moon_rashi': moon_rashi,
        'manglik': manglik,
        'vimshottari': dasha,
        'timestamp': {
            'birth_datetime_utc': dt_utc.isoformat(),
            'birth_datetime_local': dt_naive.isoformat()
        }
    }


if __name__ == '__main__':
    # Quick test with example birth chart
    dt = datetime(1990, 8, 15, 6, 30, 0)
    try:
        out = compute_chart(dt, 'Asia/Kolkata', 22.5726, 88.3639)
        import pprint
        pprint.pprint(out)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()