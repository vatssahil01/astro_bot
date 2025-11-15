#!/usr/bin/env python
# validate.py
"""
Validation script to verify all components of Astro Bot are working correctly.
"""

import sys
import os
from pathlib import Path


def check_files():
    """Check if all required files exist"""
    print("=" * 70)
    print("FILE STRUCTURE VALIDATION")
    print("=" * 70)
    
    required_files = [
        'app.py',
        'astro_calc.py',
        'rules.json',
        'sample_cases.csv',
        'requirements.txt',
        'README.md',
        'evaluation.md',
        'test_bot.py',
        'QUICKSTART.md',
    ]
    
    all_exist = True
    for filename in required_files:
        exists = Path(filename).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {filename}")
        if not exists:
            all_exist = False
    
    return all_exist


def check_imports():
    """Check if required packages can be imported"""
    print("\n" + "=" * 70)
    print("DEPENDENCY CHECK")
    print("=" * 70)
    
    packages = [
        ('swisseph or pyswisseph', 'swisseph'),
        ('gradio', 'gradio'),
        ('pytz', 'pytz'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
    ]
    
    all_installed = True
    for display_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} (install with: pip install {import_name})")
            all_installed = False
    
    return all_installed


def check_json():
    """Validate JSON files"""
    print("\n" + "=" * 70)
    print("JSON VALIDATION")
    print("=" * 70)
    
    import json
    try:
        with open('rules.json', 'r') as f:
            data = json.load(f)
        print(f"  ✓ rules.json (contains {len(data)} rule sets)")
        return True
    except Exception as e:
        print(f"  ✗ rules.json: {e}")
        return False


def check_csv():
    """Validate CSV file"""
    print("\n" + "=" * 70)
    print("CSV VALIDATION")
    print("=" * 70)
    
    try:
        import pandas as pd
        df = pd.read_csv('sample_cases.csv')
        print(f"  ✓ sample_cases.csv ({len(df)} test cases)")
        print(f"    Columns: {', '.join(df.columns.tolist())}")
        return True
    except Exception as e:
        print(f"  ✗ sample_cases.csv: {e}")
        return False


def check_calculations():
    """Test basic calculations"""
    print("\n" + "=" * 70)
    print("CALCULATION TEST")
    print("=" * 70)
    
    try:
        from astro_calc import compute_chart
        from datetime import datetime
        
        # Test with example data
        dt = datetime(1990, 8, 15, 6, 30, 0)
        chart = compute_chart(dt, 'Asia/Kolkata', 22.5726, 88.3639)
        
        # Verify all keys exist
        required_keys = ['planets', 'ascendant', 'moon_rashi', 'manglik', 'vimshottari']
        all_keys_exist = all(key in chart for key in required_keys)
        
        if all_keys_exist:
            print(f"  ✓ compute_chart() works correctly")
            print(f"    - Planets computed: {len(chart['planets'])}")
            print(f"    - Ascendant: {chart['ascendant']:.2f}°")
            print(f"    - Moon Sign: {chart['moon_rashi']['rashi_name']}")
            print(f"    - Manglik: {chart['manglik']['is_manglik']}")
            print(f"    - Current Dasha: {chart['vimshottari']['current_mahadasha']['lord']}")
            return True
        else:
            missing = [k for k in required_keys if k not in chart]
            print(f"  ✗ Missing keys in chart: {missing}")
            return False
            
    except Exception as e:
        print(f"  ✗ Calculation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_gradio_app():
    """Check if Gradio app structure is correct"""
    print("\n" + "=" * 70)
    print("GRADIO APP VALIDATION")
    print("=" * 70)
    
    try:
        import ast
        with open('app.py', 'r') as f:
            tree = ast.parse(f.read())
        
        # Check for required functions
        functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        required_funcs = ['run_chart', 'load_sample', 'format_chart_data']
        
        has_all = all(func in functions for func in required_funcs)
        if has_all:
            print(f"  ✓ app.py has all required functions: {', '.join(required_funcs)}")
        else:
            missing = [f for f in required_funcs if f not in functions]
            print(f"  ✗ Missing functions: {missing}")
        
        # Check for Gradio components
        with open('app.py', 'r') as f:
            content = f.read()
        
        gradio_present = 'gr.Blocks' in content and 'gr.Textbox' in content
        if gradio_present:
            print(f"  ✓ Gradio UI components found")
        else:
            print(f"  ✗ Gradio UI components missing")
        
        return has_all and gradio_present
        
    except Exception as e:
        print(f"  ✗ Error checking app.py: {e}")
        return False


def main():
    """Run all validations"""
    print("\n")
    print("🌙 ASTRO BOT - VALIDATION SUITE 🌙")
    print()
    
    checks = [
        ("File Structure", check_files),
        ("Dependencies", check_imports),
        ("JSON Files", check_json),
        ("CSV Files", check_csv),
        ("Calculations", check_calculations),
        ("Gradio App", check_gradio_app),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\nERROR in {name} validation: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED - BOT IS READY TO USE! 🎉")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run: python app.py")
        print("  2. Open: http://localhost:7860")
        print("  3. Enter birth details and ask a question!")
        print()
        return 0
    else:
        print("⚠️  SOME VALIDATIONS FAILED")
        print("=" * 70)
        print("\nPlease fix the issues above and try again.")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
