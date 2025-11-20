import gradio as gr
from astro_calc import compute_chart, jd_from_datetime, planet_longitude, ascendant, get_house
from datetime import datetime
import swisseph as swe

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
    mars_lon = planet_longitude(jd, swe.MARS)
    asc_lon = ascendant(jd, lat, lon)
    moon_lon = planet_longitude(jd, swe.MOON)

    h1 = get_house(mars_lon, asc_lon)
    h2 = get_house(mars_lon, moon_lon)

    return {
        "is_manglik": h1 in MANGLIK_HOUSES or h2 in MANGLIK_HOUSES,
        "from_lagna": h1,
        "from_moon": h2
    }


def process_query(name, dob, tob, lat, lon, question):
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
            f"Mars in Lagna House: {m['from_lagna']}\n"
            f"Mars in Moon House: {m['from_moon']}"
        )

    # Mahadasha
    if "dasha" in q or "period" in q:
        cur = chart["vimshottari"]["current_mahadasha"]
        if cur:
            lord = cur["lord"]
            hindi = DASHA_NAMES.get(lord, lord)
            output.append(
                f"Current Mahadasha: {lord} ({hindi})\n"
                f"Duration: {cur['duration_years']:.2f} years\n"
                f"Elapsed: {cur['elapsed_in_current_years']:.2f} years\n"
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
