import gradio as gr
from astro_calc import compute_chart, jd_from_datetime, planet_longitude, ascendant, get_house
from datetime import datetime
# import swisseph as swe  # ❌ REMOVE THIS

# Hindi names for dashas
DASHA_NAMES = {
    'Sun': 'Surya',
    'Moon': 'Chandra',
    'Mars': 'Mangal',
    'Rahu': 'Rahu',
    'Jupiter': 'Guru',
    'Saturn': 'Shani',
    'Mercury': 'Budh',
    'Ketu': 'Ketu',
    'Venus': 'Shukra'
}

MANGLIK_HOUSES = [1, 2, 4, 7, 8, 12]


def check_manglik(jd, lat, lon):
    # ✅ Use planet names instead of swe.MARS / swe.MOON
    mars_lon = planet_longitude(jd, "Mars")
    asc_lon = ascendant(jd, lat, lon)
    moon_lon = planet_longitude(jd, "Moon")

    h1 = get_house(mars_lon, asc_lon)
    h2 = get_house(mars_lon, moon_lon)

    return {
        "is_manglik": h1 in MANGLIK_HOUSES or h2 in MANGLIK_HOUSES,
        "from_lagna": h1,
        "from_moon": h2
    }


def process_query(name, dob, tob, lat, lon, question):
    # 🔹 1) Basic empty check
    if not dob or not tob:
        return "Please enter both Date of Birth (YYYY-MM-DD) and Time of Birth (HH:MM)."

    if str(lat).strip() == "" or str(lon).strip() == "":
        return "Please enter Latitude and Longitude, e.g. 28.6139 and 77.2090."

    # 🔹 2) Try to parse lat/lon safely
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return "Latitude and Longitude must be numbers, e.g. 28.6139 and 77.2090."

    # 🔹 3) Parse datetime safely
    try:
        dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    except ValueError:
        return "DOB or Time is in wrong format. Use YYYY-MM-DD and HH:MM (24-hour)."

    jd = jd_from_datetime(dt)

    chart = compute_chart(jd, lat, lon)
    q = question.lower()
    output = []

    # Moon sign
    if "moon" in q and "sign" in q:
        ms = chart["moon_sign"]
        output.append(f"Moon Sign: {ms['rashi_name']} ({ms['degree_in_rashi']}°)")

    # Manglik
    if "manglik" in q:
        m = check_manglik(jd, lat, lon)
        output.append(
            f"Manglik: {m['is_manglik']}\n"
            f"Mars from Lagna: House {m['from_lagna']}\n"
            f"Mars from Moon : House {m['from_moon']}"
        )

    # Mahadasha
    if "dasha" in q or "period" in q:
        cur = chart["vimshottari"]["current_mahadasha"]
        if cur:
            lord = cur["lord"]
            hindi = DASHA_NAMES.get(lord, lord)
            output.append(
                f"Current Mahadasha: {lord} ({hindi})\n"
                f"Duration : {cur['duration_years']:.2f} years\n"
                f"Elapsed  : {cur['elapsed_in_current_years']:.2f} years\n"
                f"Remaining: {cur['remaining_years']:.2f} years"
            )
        else:
            output.append("Unable to determine Mahadasha.")

    if not output:
        output.append("I couldn't understand the question. Try asking about 'Moon sign', 'Manglik', or 'Mahadasha'.")

    return "\n\n".join(output)

    dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    jd = jd_from_datetime(dt)

    chart = compute_chart(jd, float(lat), float(lon))
    q = question.lower()
    output = []

    # Moon sign
    if "moon" in q and "sign" in q:
        ms = chart["moon_sign"]
        output.append(f"Moon Sign: {ms['rashi_name']} ({ms['degree_in_rashi']}°)")

    # Manglik
    if "manglik" in q:
        m = check_manglik(jd, float(lat), float(lon))
        output.append(
            f"Manglik: {m['is_manglik']}\n"
            f"Mars from Lagna: House {m['from_lagna']}\n"
            f"Mars from Moon : House {m['from_moon']}"
        )

    # Mahadasha
    if "dasha" in q or "period" in q:
        cur = chart["vimshottari"]["current_mahadasha"]
        if cur:
            lord = cur["lord"]
            hindi = DASHA_NAMES.get(lord, lord)
            output.append(
                f"Current Mahadasha: {lord} ({hindi})\n"
                f"Duration : {cur['duration_years']:.2f} years\n"
                f"Elapsed  : {cur['elapsed_in_current_years']:.2f} years\n"
                f"Remaining: {cur['remaining_years']:.2f} years"
            )
        else:
            output.append("Unable to determine Mahadasha.")

    return "\n\n".join(output)


ui = gr.Interface(
    fn=process_query,
    inputs=[
        gr.Text(label="Name"),
        gr.Text(label="DOB (YYYY-MM-DD)"),
        gr.Text(label="Time of Birth (HH:MM)"),
        gr.Text(label="Latitude"),
        gr.Text(label="Longitude"),
        gr.Text(label="Question")
    ],
    outputs="text",
    title="Astro Bot"
)

if __name__ == "__main__":
    ui.launch()
