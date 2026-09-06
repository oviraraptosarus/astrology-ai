from astrology_engine import calculate_full_chart
import json

def run_verification():
    # Test Data: August 15, 1947, 00:00 AM, New Delhi (India Independence)
    # Lat: 28.6139, Lon: 77.2090
    print("Testing Core Calculations for August 15, 1947, 00:00, New Delhi...")
    try:
        chart_data = calculate_full_chart(
            year=1947,
            month=8,
            day=15,
            hour=0,
            minute=0,
            lat=28.6139,
            lon=77.2090,
            name="India Independence"
        )
        
        # Verify Ascendant
        asc_sign = chart_data["Basic_Chart"]["Ascendant"]["sign"]
        asc_deg = chart_data["Basic_Chart"]["Ascendant"]["degree"]
        print(f"Ascendant: {asc_sign} at {asc_deg:.2f} degrees")
        
        # Verify Moon
        moon_sign = chart_data["Basic_Chart"]["Moon"]["sign"]
        moon_deg = chart_data["Basic_Chart"]["Moon"]["degree"]
        print(f"Moon: {moon_sign} at {moon_deg:.2f} degrees")
        
        # Verify D9 (Navamsha)
        d9_asc = chart_data["Navamsha_D9"]["Ascendant"]
        print(f"D9 Ascendant: {d9_asc}")
        
        # Verify D10 (Dasamsha)
        d10_asc = chart_data["Dasamsha_D10"]["Ascendant"]
        print(f"D10 Ascendant: {d10_asc}")
        
        # Verify Panchanga
        panchanga = chart_data["Panchanga"]
        print(f"Panchanga: {json.dumps(panchanga, indent=2)}")
        
        # Verify Current Dasha structure exists
        dasha = chart_data["Current_Dasha"]
        print(f"Current Dasha Calculation Exists: {dasha is not None}")
        
        print("\nAll core calculation checks passed!")
    except Exception as e:
        print(f"Error during calculation verification: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_verification()
