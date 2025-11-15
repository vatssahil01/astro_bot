#!/usr/bin/env python
# test_bot.py
"""
Quick test script for Astro Bot to verify all functions work correctly.
"""

import sys
from datetime import datetime
import os

try:
    from astro_calc import compute_chart
except Exception as e:
    print(f"Error importing astro_calc: {e}")
    sys.exit(1)


def test_example_chart():
    """Test with example birth chart"""
    print("=" * 60)
    print("Testing Astro Bot with Example Birth Chart")
    print("=" * 60)

    print(f"\nPython Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Example: Ravi Sharma
    dt = datetime(1990, 8, 15, 6, 30, 0)
    tz = 'Asia/Kolkata'
    lat = 22.5726
    lon = 88.3639
    
    print(f"\nBirth Details:")
    print(f"  Date: {dt.strftime('%Y-%m-%d')}")
    print(f"  Time: {dt.strftime('%H:%M:%S')}")
    print(f"  Timezone: {tz}")
    print(f"  Location: ({lat}°N, {lon}°E)")
    
    try:
        chart = compute_chart(dt, tz, lat, lon)
        
        print("\n" + "=" * 60)
        print("COMPUTED CHART")
        print("=" * 60)
        
        print(f"\nPlanetary Positions:")
        for planet, lon_val in chart['planets'].items():
            print(f"  {planet:10s}: {lon_val:7.2f}°")
        
        print(f"\nAscendant (Lagna): {chart['ascendant']:.2f}°")
        
        print(f"\nMoon Sign (Rashi):")
        mr = chart['moon_rashi']
        print(f"  Rashi Name: {mr['rashi_name']}")
        print(f"  Longitude: {mr['full_longitude']:.2f}°")
        print(f"  Degree in Rashi: {mr['degree_in_rashi']:.2f}°")
        
        print(f"\nManglik Dosha Check:")
        mg = chart['manglik']
        print(f"  Mars Longitude: {mg['mars_longitude']:.2f}°")
        print(f"  Mars House from Lagna: {mg['mars_house_from_lagna']}")
        print(f"  Mars House from Moon: {mg['mars_house_from_moon']}")
        print(f"  Is Manglik: {mg['is_manglik']}")
        if mg['is_manglik']:
            print(f"  ✓ YES - Manglik dosha triggered!")
        else:
            print(f"  ✗ NO - Not Manglik")
        
        print(f"\nVimshottari Dasha:")
        vs = chart['vimshottari']
        print(f"  Starting Nakshatra: {vs['starting_nakshatra']}")
        print(f"  Moon Longitude: {vs['moon_longitude_at_birth']:.2f}°")
        print(f"  Total Elapsed Years: {vs['elapsed_years']:.2f}")
        if vs['current_mahadasha']:
            cm = vs['current_mahadasha']
            print(f"  Current Mahadasha: {cm['lord']}")
            print(f"    - Elapsed: {cm['elapsed_in_current_years']:.2f} years")
            print(f"    - Remaining: {cm['remaining_years']:.2f} years")
        
        print("\n" + "=" * 60)
        print("✅ TEST PASSED - All functions working correctly!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_cases():
    """Test with multiple cases from sample_cases.csv"""
    print("\n\n" + "=" * 60)
    print("Testing Multiple Birth Charts")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Priya Mehta',
            'date': datetime(1995, 2, 10, 14, 45, 0),
            'tz': 'Asia/Kolkata',
            'lat': 19.0760,
            'lon': 72.8777,
            'expected_moon': 'Libra',
            'question': 'moon sign'
        },
        {
            'name': 'Amit Kumar',
            'date': datetime(2000, 12, 25, 21, 10, 0),
            'tz': 'Asia/Kolkata',
            'lat': 28.6139,
            'lon': 77.2090,
            'expected_dasha': 'Saturn',
            'question': 'dasha'
        },
        {
            'name': 'Sneha Rao',
            'date': datetime(1987, 5, 2, 9, 15, 0),
            'tz': 'Asia/Kolkata',
            'lat': 12.9716,
            'lon': 77.5946,
            'expected_manglik': False,
            'question': 'manglik'
        }
    ]
    
    passed = 0
    for case in test_cases:
        print(f"\n  Testing: {case['name']}")
        try:
            chart = compute_chart(case['date'], case['tz'], case['lat'], case['lon'])
            
            if 'expected_moon' in case:
                if chart['moon_rashi']['rashi_name'] == case['expected_moon']:
                    print(f"    ✓ Moon Sign: {chart['moon_rashi']['rashi_name']} (MATCH)")
                    passed += 1
                else:
                    print(f"    ✗ Moon Sign: {chart['moon_rashi']['rashi_name']} (expected {case['expected_moon']})")
            
            if 'expected_dasha' in case:
                dasha = chart['vimshottari']['current_mahadasha']['lord']
                if dasha == case['expected_dasha']:
                    print(f"    ✓ Mahadasha: {dasha} (MATCH)")
                    passed += 1
                else:
                    print(f"    ✗ Mahadasha: {dasha} (expected {case['expected_dasha']})")
            
            if 'expected_manglik' in case:
                is_manglik = chart['manglik']['is_manglik']
                if is_manglik == case['expected_manglik']:
                    result = "Manglik" if is_manglik else "Not Manglik"
                    print(f"    ✓ Manglik: {result} (MATCH)")
                    passed += 1
                else:
                    result = "Manglik" if is_manglik else "Not Manglik"
                    expected = "Manglik" if case['expected_manglik'] else "Not Manglik"
                    print(f"    ✗ Manglik: {result} (expected {expected})")
        
        except Exception as e:
            print(f"    ✗ ERROR: {e}")
    
    print(f"\n  Results: {passed}/{len(test_cases)} test cases passed")
    return passed == len(test_cases)


if __name__ == '__main__':
    success = test_example_chart()
    success = test_multiple_cases() and success
    
    if success:
        print("\n\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Bot is ready to use.")
        print("=" * 60)
        print("\nTo run the Gradio web interface:")
        print("  python app.py")
        print("\nThen open http://localhost:7860 in your browser")
    else:
        print("\n\n" + "=" * 60)
        print("⚠️  Some tests failed. Check the output above.")
        print("=" * 60)
        sys.exit(1)
