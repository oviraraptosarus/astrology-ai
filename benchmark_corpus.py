"""
benchmark_corpus.py -- Documented birth data + dated life events for blind testing.

Birth data leans on Rodden-rated public records (AA = birth certificate, A = from
the person/family). Times for a few figures are disputed; those are flagged in
"quality" and should be read as lower-confidence. Events are widely documented
public milestones with known dates.

This corpus exists to be tested AGAINST, including with negative controls and
permutation tests. It is not curated to make the astrology look good.

Domains: CAREER, WEALTH, MARRIAGE, HEALTH_ACCIDENT, CHILDREN, FAME.
"""

CORPUS = {
    "STEVE_JOBS": {
        "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15,
                  "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
        "quality": "AA",
        "events": [
            {"date": "1976-04-01", "domain": "CAREER", "type": "Apple founded"},
            {"date": "1980-12-12", "domain": "WEALTH", "type": "Apple IPO"},
            {"date": "1985-09-16", "domain": "CAREER", "type": "Ousted from Apple / NeXT"},
            {"date": "1991-03-18", "domain": "MARRIAGE", "type": "Married Laurene Powell"},
            {"date": "1997-07-04", "domain": "CAREER", "type": "Returns to Apple (interim CEO)"},
            {"date": "2004-07-31", "domain": "HEALTH_ACCIDENT", "type": "Pancreatic tumor surgery"},
            {"date": "2011-10-05", "domain": "HEALTH_ACCIDENT", "type": "Death"},
        ],
    },
    "BARACK_OBAMA": {
        "birth": {"year": 1961, "month": 8, "day": 4, "hour": 19, "minute": 24,
                  "lat": 21.3069, "lon": -157.8583, "tz": "Pacific/Honolulu"},
        "quality": "AA",
        "events": [
            {"date": "1992-10-03", "domain": "MARRIAGE", "type": "Married Michelle"},
            {"date": "2004-11-02", "domain": "CAREER", "type": "Elected US Senator"},
            {"date": "2008-11-04", "domain": "FAME", "type": "Elected President"},
            {"date": "2009-10-09", "domain": "FAME", "type": "Nobel Peace Prize"},
            {"date": "2012-11-06", "domain": "CAREER", "type": "Re-elected President"},
        ],
    },
    "ALBERT_EINSTEIN": {
        "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30,
                  "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
        "quality": "AA",
        "events": [
            {"date": "1903-01-06", "domain": "MARRIAGE", "type": "Married Mileva Maric"},
            {"date": "1905-09-26", "domain": "CAREER", "type": "Special relativity published"},
            {"date": "1919-11-06", "domain": "FAME", "type": "Eclipse confirms GR / global fame"},
            {"date": "1922-11-09", "domain": "FAME", "type": "Nobel Prize in Physics"},
            {"date": "1955-04-18", "domain": "HEALTH_ACCIDENT", "type": "Death (aortic aneurysm)"},
        ],
    },
    "ELON_MUSK": {
        "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30,
                  "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
        "quality": "B",
        "events": [
            {"date": "1999-02-01", "domain": "WEALTH", "type": "Zip2 sold ($307M)"},
            {"date": "2000-12-15", "domain": "HEALTH_ACCIDENT", "type": "Near-fatal malaria"},
            {"date": "2002-10-03", "domain": "WEALTH", "type": "PayPal sold to eBay"},
            {"date": "2008-09-28", "domain": "CAREER", "type": "Falcon 1 first success"},
            {"date": "2021-01-07", "domain": "WEALTH", "type": "World's richest person"},
        ],
    },
    "PRINCESS_DIANA": {
        "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45,
                  "lat": 52.8300, "lon": 0.5000, "tz": "Europe/London"},
        "quality": "A",
        "events": [
            {"date": "1981-07-29", "domain": "MARRIAGE", "type": "Wedding to Charles"},
            {"date": "1982-06-21", "domain": "CHILDREN", "type": "Prince William born"},
            {"date": "1992-12-09", "domain": "MARRIAGE", "type": "Separation announced"},
            {"date": "1996-08-28", "domain": "MARRIAGE", "type": "Divorce finalized"},
            {"date": "1997-08-31", "domain": "HEALTH_ACCIDENT", "type": "Fatal car crash"},
        ],
    },
    "OPRAH_WINFREY": {
        "birth": {"year": 1954, "month": 1, "day": 29, "hour": 4, "minute": 30,
                  "lat": 33.4735, "lon": -89.0776, "tz": "America/Chicago"},
        "quality": "A",
        "events": [
            {"date": "1986-09-08", "domain": "CAREER", "type": "Oprah Show nationally syndicated"},
            {"date": "1993-02-10", "domain": "FAME", "type": "Michael Jackson interview (record ratings)"},
            {"date": "2003-02-27", "domain": "WEALTH", "type": "First billion (Forbes billionaire)"},
            {"date": "2011-05-25", "domain": "CAREER", "type": "Oprah Show ends"},
        ],
    },
    "MARILYN_MONROE": {
        "birth": {"year": 1926, "month": 6, "day": 1, "hour": 9, "minute": 30,
                  "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "quality": "AA",
        "events": [
            {"date": "1954-01-14", "domain": "MARRIAGE", "type": "Married Joe DiMaggio"},
            {"date": "1956-06-29", "domain": "MARRIAGE", "type": "Married Arthur Miller"},
            {"date": "1962-08-05", "domain": "HEALTH_ACCIDENT", "type": "Death"},
        ],
    },
    "JOHN_LENNON": {
        "birth": {"year": 1940, "month": 10, "day": 9, "hour": 18, "minute": 30,
                  "lat": 53.4084, "lon": -2.9916, "tz": "Europe/London"},
        "quality": "A",
        "events": [
            {"date": "1962-08-23", "domain": "MARRIAGE", "type": "Married Cynthia"},
            {"date": "1969-03-20", "domain": "MARRIAGE", "type": "Married Yoko Ono"},
            {"date": "1964-02-07", "domain": "FAME", "type": "Beatles arrive in US"},
            {"date": "1980-12-08", "domain": "HEALTH_ACCIDENT", "type": "Assassinated"},
        ],
    },
    "MUHAMMAD_ALI": {
        "birth": {"year": 1942, "month": 1, "day": 17, "hour": 18, "minute": 35,
                  "lat": 38.2527, "lon": -85.7585, "tz": "America/Kentucky/Louisville"},
        "quality": "A",
        "events": [
            {"date": "1964-02-25", "domain": "CAREER", "type": "Beats Liston, world champion"},
            {"date": "1967-04-28", "domain": "CAREER", "type": "Stripped of title (draft refusal)"},
            {"date": "1974-10-30", "domain": "CAREER", "type": "Rumble in the Jungle win"},
            {"date": "1984-09-01", "domain": "HEALTH_ACCIDENT", "type": "Parkinson's diagnosis"},
        ],
    },
    "PRINCESS_GRACE_KELLY": {
        "birth": {"year": 1929, "month": 11, "day": 12, "hour": 5, "minute": 31,
                  "lat": 39.9526, "lon": -75.1652, "tz": "America/New_York"},
        "quality": "AA",
        "events": [
            {"date": "1955-03-30", "domain": "FAME", "type": "Wins Academy Award"},
            {"date": "1956-04-19", "domain": "MARRIAGE", "type": "Marries Prince Rainier"},
            {"date": "1982-09-14", "domain": "HEALTH_ACCIDENT", "type": "Fatal car crash"},
        ],
    },
    "WALT_DISNEY": {
        "birth": {"year": 1901, "month": 12, "day": 5, "hour": 0, "minute": 35,
                  "lat": 41.8781, "lon": -87.6298, "tz": "America/Chicago"},
        "quality": "AA",
        "events": [
            {"date": "1928-11-18", "domain": "CAREER", "type": "Steamboat Willie / Mickey debut"},
            {"date": "1937-12-21", "domain": "CAREER", "type": "Snow White premiere"},
            {"date": "1955-07-17", "domain": "CAREER", "type": "Disneyland opens"},
            {"date": "1966-12-15", "domain": "HEALTH_ACCIDENT", "type": "Death (lung cancer)"},
        ],
    },
    "PRINCE_CHARLES": {
        "birth": {"year": 1948, "month": 11, "day": 14, "hour": 21, "minute": 14,
                  "lat": 51.5014, "lon": -0.1419, "tz": "Europe/London"},
        "quality": "AA",
        "events": [
            {"date": "1981-07-29", "domain": "MARRIAGE", "type": "Marries Diana"},
            {"date": "1982-06-21", "domain": "CHILDREN", "type": "Prince William born"},
            {"date": "1996-08-28", "domain": "MARRIAGE", "type": "Divorce from Diana"},
            {"date": "2005-04-09", "domain": "MARRIAGE", "type": "Marries Camilla"},
            {"date": "2022-09-08", "domain": "CAREER", "type": "Becomes King"},
        ],
    },
    "AMITABH_BACHCHAN": {
        "birth": {"year": 1942, "month": 10, "day": 11, "hour": 16, "minute": 0,
                  "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "quality": "A",
        "events": [
            {"date": "1973-06-03", "domain": "MARRIAGE", "type": "Marries Jaya Bhaduri"},
            {"date": "1982-07-26", "domain": "HEALTH_ACCIDENT", "type": "Coolie near-fatal injury"},
            {"date": "2000-07-03", "domain": "CAREER", "type": "KBC premiere / comeback"},
        ],
    },
    "ANGELINA_JOLIE": {
        "birth": {"year": 1975, "month": 6, "day": 4, "hour": 9, "minute": 9,
                  "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "quality": "AA",
        "events": [
            {"date": "2000-06-05", "domain": "FAME", "type": "Wins Academy Award"},
            {"date": "2006-05-27", "domain": "CHILDREN", "type": "Shiloh born"},
            {"date": "2014-08-23", "domain": "MARRIAGE", "type": "Marries Brad Pitt"},
            {"date": "2016-09-19", "domain": "MARRIAGE", "type": "Files for divorce"},
        ],
    },
    "TIGER_WOODS": {
        "birth": {"year": 1975, "month": 12, "day": 30, "hour": 22, "minute": 50,
                  "lat": 33.7879, "lon": -117.8531, "tz": "America/Los_Angeles"},
        "quality": "A",
        "events": [
            {"date": "1997-04-13", "domain": "CAREER", "type": "First Masters win"},
            {"date": "2004-10-05", "domain": "MARRIAGE", "type": "Marries Elin Nordegren"},
            {"date": "2009-11-27", "domain": "HEALTH_ACCIDENT", "type": "Car crash / scandal"},
            {"date": "2019-04-14", "domain": "CAREER", "type": "Masters comeback win"},
            {"date": "2021-02-23", "domain": "HEALTH_ACCIDENT", "type": "Severe leg-crushing car crash"},
        ],
    },
}
