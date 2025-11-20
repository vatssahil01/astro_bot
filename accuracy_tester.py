import pandas as pd
from datetime import datetime
from astro_calc import compute_chart, jd_from_datetime, planet_longitude, ascendant, get_house
import swisseph as swe

# Your Manglik rule
MANGLIK_HOUSES = [1, 2, 4, 7, 8, 12]

# Dasha names for labeling
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

def check_manglik(jd, lat, lon):
    mars_lon = planet_longitude(jd, swe.MARS)
    asc_lon = ascendant(jd, lat, lon)
    moon_lon = planet_longitude(jd, swe.MOON)

    h1 = get_house(mars_lon, asc_lon)
    h2 = get_house(mars_lon, moon_lon)

    result = h1 in MANGLIK_HOUSES or h2 in MANGLIK_HOUSES

    if result:
        return f"Yes (Mars in {h1}th House, Manglik rule triggered)"
    else:
        return f"No (Mars in {h1}th House)"

def compute_moon_sign(chart):
    return f"Moon in {chart['moon_sign']['rashi_name']}"

def compute_dasha(chart):
    current = chart["vimshottari"]["current_mahadasha"]
    if current:
        lord = current["lord"]
        return f"Currently under {lord} ({DASHA_NAMES.get(lord, lord)}) Mahadasha"
    return "Unknown"

def evaluate_row(row):
    name = row["Name"]
    date = row["Date"]
    time = row["Time"]
    lat = float(row["Latitude"])
    lon = float(row["Longitude"])
    question = row["Question"]
    expected = row["Expected_Result"].strip()

    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    jd = jd_from_datetime(dt)
    chart = compute_chart(jd, lat, lon)

    # Determine result
    question_lower = question.lower()
    
    if "manglik" in question_lower:
        result = check_manglik(jd, lat, lon)
    elif "moon" in question_lower:
        result = compute_moon_sign(chart)
    elif "dasha" in question_lower or "period" in question_lower:
        result = compute_dasha(chart)
    else:
        result = "Unknown"

    # Check PASS/FAIL
    passed = expected.lower().split()[0] in result.lower()

    return {
        "Name": name,
        "Question": question,
        "Expected": expected,
        "Got": result,
        "Result": "PASS" if passed else "FAIL"
    }

def run_accuracy_test(csv_path="sample_cases.csv"):
    df = pd.read_csv(csv_path)
    results = []
    passed_count = 0

    print("\n=========== ASTRO BOT ACCURACY REPORT ===========\n")

    for i, row in df.iterrows():
        r = evaluate_row(row)
        results.append(r)

        print(f"{i+1}. {r['Name']} — {r['Question']}")
        print(f"   Expected: {r['Expected']}")
        print(f"   Got     : {r['Got']}")
        print(f"   Result  : {r['Result']}")
        print("--------------------------------------------------")

        if r["Result"] == "PASS":
            passed_count += 1

    total = len(results)
    accuracy = (passed_count / total) * 100

    print("\n================ SUMMARY ================\n")
    print(f"Total Cases: {total}")
    print(f"Passed     : {passed_count}")
    print(f"Failed     : {total - passed_count}")
    print(f"Accuracy   : {accuracy:.2f}%")

    print("\n==========================================\n")

    # Save results
    out_df = pd.DataFrame(results)
    out_df.to_csv("accuracy_results.csv", index=False)
    print("Detailed report saved to accuracy_results.csv")

    return results


if __name__ == "__main__":
    run_accuracy_test()
