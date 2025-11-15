# app.py
"""
Astro Bot - Vedic Astrology Assistant
Gradio interface for answering astrology questions based on birth chart calculations
"""

import gradio as gr
from datetime import datetime
from astro_calc import compute_chart, jd_from_datetime
import pandas as pd
import pytz
import traceback


EXAMPLE = {
    'date': '1990-08-15',
    'time': '06:30:00',
    'tz': 'Asia/Kolkata',
    'lat': 22.5726,
    'lon': 88.3639
}


def format_chart_data(chart):
    """Format chart data for display"""
    planets_str = "**Planetary Positions:**\n"
    for planet, lon in chart['planets'].items():
        planets_str += f"  {planet}: {lon:.2f}°\n"
    
    computed_data = f"""
**COMPUTED DATA:**
{planets_str}
**Ascendant (Lagna):** {chart['ascendant']:.2f}°
**Moon Sign:** {chart['moon_rashi']['rashi_name']} ({chart['moon_rashi']['full_longitude']:.2f}°)
**Moon Nakshatra:** {chart['vimshottari']['starting_nakshatra']}
**Mars Position:** {chart['manglik']['mars_longitude']:.2f}° (House {chart['manglik']['mars_house_from_lagna']} from Lagna)
"""
    return computed_data


def run_chart(date, time, tz, lat, lon, question):
    """
    Main function to compute chart and answer questions.
    """
    try:
        # Parse input
        if not date or not time or not tz or not question:
            return "Error: Please fill in all fields including the question.", ""
        
        dt = datetime.fromisoformat(f"{date}T{time}")
        chart = compute_chart(dt, tz, float(lat), float(lon))
        
        answers = []
        q = question.strip().lower()
        
        # Question handling - Manglik Dosha
        if 'manglik' in q or 'dosha' in q:
            if chart['manglik']['is_manglik_by_lagna'] or chart['manglik']['is_manglik_by_moon']:
                ans = f"""
✓ **YES, you are Manglik**

**Rule Applied:** Mars Dosha (Classical Vedic Rule)

**Explanation:**
Mars is located at {chart['manglik']['mars_longitude']:.2f}°
- House from Ascendant: **{chart['manglik']['mars_house_from_lagna']}** (Manglik house)
- House from Moon: **{chart['manglik']['mars_house_from_moon']}**

According to Vedic astrology, Mars in houses 1, 2, 4, 7, 8, or 12 triggers the Manglik dosha.
This is traditionally believed to affect marriage compatibility.
"""
            else:
                ans = f"""
✗ **NO, you are NOT Manglik**

**Rule Applied:** Mars Dosha (Classical Vedic Rule)

**Explanation:**
Mars is located at {chart['manglik']['mars_longitude']:.2f}°
- House from Ascendant: **{chart['manglik']['mars_house_from_lagna']}** (Non-Manglik house)
- House from Moon: **{chart['manglik']['mars_house_from_moon']}**

Mars in houses 3, 5, 6, 9, 10, 11 does not trigger Manglik dosha.
"""
            answers.append(ans)
        
        # Question handling - Moon Sign
        if 'moon sign' in q or (q == 'moon' and len(q) == 4) or 'moon rashi' in q:
            ans = f"""
**Your Moon Sign (Rashi):** {chart['moon_rashi']['rashi_name']}

**Details:**
- Moon Longitude: {chart['moon_rashi']['full_longitude']:.2f}°
- Degree in Rashi: {chart['moon_rashi']['degree_in_rashi']:.2f}°
- Nakshatra: {chart['vimshottari']['starting_nakshatra']}

The Moon sign represents your emotional nature and inner self in Vedic astrology.
"""
            answers.append(ans)
        
        # Question handling - Mahadasha / Dasha
        if 'dasha' in q or 'mahadasha' in q or 'period' in q:
            cur = chart['vimshottari']['current_mahadasha']
            if cur:
                ans = f"""
**Current Mahadasha:** {cur['lord']} (शनि / Shani)

**Timeline:**
- Elapsed: {cur['elapsed_in_current_years']:.2f} years
- Remaining: {cur['remaining_years']:.2f} years
- Total Duration: {cur['duration_years']} years

**Vimshottari Dasha System:**
This is based on the Vimshottari dasha system, which divides a 120-year life cycle 
into 9 periods ruled by different planetary lords.
Your birth Moon was in {chart['vimshottari']['starting_nakshatra']} Nakshatra.

**Full Timeline (next 30 periods):**
"""
                for i, period in enumerate(chart['vimshottari']['timeline'][:10]):
                    marker = "→ CURRENT" if i == 0 else ""
                    ans += f"\n  {i+1}. {period['lord']}: {period['start_year']:.1f} - {period['end_year']:.1f} yrs {marker}"
            else:
                ans = "Could not determine current Mahadasha."
            answers.append(ans)
        
        # If no specific question matched, provide general reading
        if not answers:
            ans = f"""
**General Chart Reading:**

No specific question matched. Here's your chart summary:

**Ascendant (Lagna):** {chart['ascendant']:.2f}°
**Moon Sign:** {chart['moon_rashi']['rashi_name']} ({chart['moon_rashi']['full_longitude']:.2f}°)
**Nakshatra:** {chart['vimshottari']['starting_nakshatra']}

**Manglik Status:** {"YES" if chart['manglik']['is_manglik'] else "NO"}
- Mars at {chart['manglik']['mars_longitude']:.2f}° in house {chart['manglik']['mars_house_from_lagna']} from Ascendant

You can ask:
- "Am I Manglik?"
- "What is my Moon sign?"
- "Which Mahadasha am I in?"
"""
            answers.append(ans)
        
        # Format computed data
        computed_data = format_chart_data(chart)
        
        # Combine answers
        final_answer = "\n".join(answers)
        return final_answer, computed_data
        
    except ValueError as e:
        return f"Date/Time Error: Please use format YYYY-MM-DD for date and HH:MM:SS for time.\nError: {str(e)}", ""
    except Exception as e:
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return error_msg, ""


def load_sample():
    """Load example birth details"""
    return EXAMPLE['date'], EXAMPLE['time'], EXAMPLE['tz'], EXAMPLE['lat'], EXAMPLE['lon'], "Am I Manglik?"


# Build Gradio interface
if __name__ == "__main__":
    with gr.Blocks(title="Astro Bot - Vedic Astrology", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🌙 Astro Bot — Vedic Astrology Assistant
            
            Answer your astrology questions using real planetary calculations!
            Enter your birth details and ask a question.
            
            **Supported Questions:**
            - Am I Manglik?
            - What is my Moon sign?
            - Which Mahadasha am I in?
            """
        )
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Birth Details")
                date_input = gr.Textbox(
                    label="Birth Date",
                    placeholder="YYYY-MM-DD",
                    value=EXAMPLE['date']
                )
                time_input = gr.Textbox(
                    label="Birth Time",
                    placeholder="HH:MM:SS",
                    value=EXAMPLE['time']
                )
                tz_input = gr.Textbox(
                    label="Timezone",
                    placeholder="e.g., Asia/Kolkata",
                    value=EXAMPLE['tz']
                )
                
                gr.Markdown("### Location")
                lat_input = gr.Number(
                    label="Latitude",
                    value=EXAMPLE['lat']
                )
                lon_input = gr.Number(
                    label="Longitude",
                    value=EXAMPLE['lon']
                )
                
                question_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., Am I Manglik?",
                    value="Am I Manglik?"
                )
                
                with gr.Row():
                    submit_btn = gr.Button("🔮 Get Answer", variant="primary")
                    sample_btn = gr.Button("📋 Load Example")
            
            with gr.Column():
                answer_output = gr.Markdown(label="Answer")
                computed_output = gr.Markdown(label="Computed Data")
        
        # Button actions
        submit_btn.click(
            fn=run_chart,
            inputs=[date_input, time_input, tz_input, lat_input, lon_input, question_input],
            outputs=[answer_output, computed_output]
        )
        
        sample_btn.click(
            fn=load_sample,
            outputs=[date_input, time_input, tz_input, lat_input, lon_input, question_input]
        )
        
        gr.Markdown(
            """
            ---
            ### About This Bot
            This bot computes real astrological data using Swiss Ephemeris (pyswisseph).
            
            **Rules Implemented:**
            1. **Manglik Dosha** - Mars in houses 1, 2, 4, 7, 8, or 12 triggers Manglik
            2. **Moon Sign (Rashi)** - Determined from Moon longitude (12 signs, 30° each)
            3. **Vimshottari Dasha** - Current mahadasha based on birth nakshatra and age
            
            **Note:** This is for educational purposes. Always consult a qualified astrologer for important decisions.
            """
        )
    
    demo.launch(server_name="0.0.0.0", server_port=7860)