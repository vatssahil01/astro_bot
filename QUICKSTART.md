# QUICKSTART.md - Get Started in 5 Minutes

## Installation

### Step 1: Install Python Packages
```bash
pip install -r requirements.txt
```

**What this installs:**
- `pyswisseph` - Planetary calculations
- `gradio` - Web interface
- `pytz` - Timezone handling
- `pandas` - Data processing
- `numpy` - Numerical math

### Step 2: Run the Bot

**Option A - Web Interface (Recommended)**
```bash
python app.py
```
- Opens at: http://localhost:7860
- Beautiful Gradio UI
- Best for exploration

**Option B - Quick Test**
```bash
python test_bot.py
```
- Tests all functions
- Verifies calculations
- Useful for debugging

**Option C - Python API**
```python
from astro_calc import compute_chart
from datetime import datetime

dt = datetime(1990, 8, 15, 6, 30, 0)
chart = compute_chart(dt, 'Asia/Kolkata', 22.5726, 88.3639)
print(f"Manglik: {chart['manglik']['is_manglik']}")
print(f"Moon Sign: {chart['moon_rashi']['rashi_name']}")
```

## Quick Examples

### Ask "Am I Manglik?"
- Birth Date: 1990-08-15
- Birth Time: 06:30:00
- Timezone: Asia/Kolkata
- Location: 22.5726°N, 88.3639°E
- Expected: YES (Mars in 7th house)

### Ask "What is my Moon sign?"
- Birth Date: 1995-02-10
- Birth Time: 14:45:00
- Timezone: Asia/Kolkata
- Location: 19.0760°N, 72.8777°E (Mumbai)
- Expected: Libra

### Ask "Which Mahadasha am I in?"
- Birth Date: 2000-12-25
- Birth Time: 21:10:00
- Timezone: Asia/Kolkata
- Location: 28.6139°N, 77.2090°E (Delhi)
- Expected: Saturn (as of Nov 2025)

## Using the Gradio Interface

1. Enter birth date (YYYY-MM-DD format)
2. Enter birth time (HH:MM:SS format)
3. Enter timezone (e.g., Asia/Kolkata)
4. Enter latitude and longitude
5. Ask your question
6. Click "🔮 Get Answer"
7. View results and computed data

**Pro Tip**: Use "📋 Load Example" button to test with sample data!

## Understanding Your Birth Chart

### Manglik Dosha
- Shows if Mars is in problematic house
- Houses 1, 2, 4, 7, 8, 12 trigger dosha
- Affects marriage compatibility

### Moon Sign
- Your emotional nature
- Different from Sun sign
- 12 zodiac signs possible
- Each spans 30° of sky

### Mahadasha
- Current life period (120-year cycle)
- 9 planetary lords
- Predicts major themes
- Year-by-year timeline shown

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| Import Error | `pip install pyswisseph` |
| Port 7860 in use | Modify port in app.py |
| Wrong timezone | Use `pytz.all_timezones` to find correct name |
| Accuracy concerns | See evaluation.md for verification |

## Next Steps

- Explore sample cases in `sample_cases.csv`
- Read `README.md` for detailed documentation
- Check `evaluation.md` for accuracy verification
- Review `rules.json` for rule definitions

## Project Files

| File | Purpose |
|------|---------|
| `app.py` | Web interface |
| `astro_calc.py` | Calculations engine |
| `rules.json` | Rule definitions |
| `sample_cases.csv` | Test data |
| `test_bot.py` | Automated tests |
| `README.md` | Full documentation |
| `evaluation.md` | Accuracy report |

## Have Fun! 🌙

The bot is ready to use. Start exploring your astrological chart!

---

**Questions?** Check README.md or run test_bot.py for verification.
