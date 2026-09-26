from datetime import datetime, timedelta

def test_dasha_precision():
    birth_time = datetime(2000, 1, 1, 0, 0, 0)
    year_length = 365.2422
    md_years = 20 # Venus
    
    # DashaEngine method
    duration_days = md_years * year_length
    end_date = birth_time + timedelta(days=duration_days)
    
    print(f"Birth: {birth_time}")
    print(f"End Date (timedelta): {end_date}")
    
    # Are we accumulating errors across 120 years?
    total_years = 120
    accumulated_end = birth_time
    for y in [7, 20, 6, 10, 7, 18, 16, 19, 17]:
        accumulated_end += timedelta(days=y * year_length)
        
    direct_120_end = birth_time + timedelta(days=120 * year_length)
    print(f"Accumulated 120y end: {accumulated_end}")
    print(f"Direct 120y end: {direct_120_end}")
    print(f"Difference: {accumulated_end - direct_120_end}")
    
    # Julian calendar test (pre 1582)
    try:
        old_date = datetime(1500, 1, 1)
        old_end = old_date + timedelta(days=365.25 * 100)
        print(f"Old date + 100 Julian years: {old_end} (Note: Python datetime is Proleptic Gregorian!)")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    test_dasha_precision()
