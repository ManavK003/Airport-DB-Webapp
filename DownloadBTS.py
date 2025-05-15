import os
import time
import requests

# Change this to your actual folder
DOWNLOAD_DIR = "/Users/manavkanaganapalli/Desktop/Airport Landings Database and Webapp/ML Data/Arrival_Departure"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

iata_codes = [
    "BOS", "OAK", "OGG", "MCI", "PHX", "SFO", "LAX", "CLE", "CVG", "EWR",
    "DAL", "FLL", "SLC", "IAH", "HOU", "PIT", "MIA", "SEA", "IND", "SAT",
    "RDU", "BUR", "DTW", "TPA", "DFW", "AUS", "STL", "ATL", "JAX", "IAD",
    "MKE", "PDX", "HNL", "SAN", "ONT", "MDW", "SJC", "DEN", "PHL", "RSW",
    "JFK", "RNO", "SMF", "ORD", "BWI", "MSP", "SNA", "CLT", "LAS", "MCO"
]

years = list(range(2018, 2026))
BTS_CSV_URL = "https://www.transtats.bts.gov/DownLoad_Table.asp?Table_ID=236"

fields = [
    "Year", "Month", "DayofMonth", "FlightDate", "Carrier", "FlightNum",
    "Origin", "Dest", "DepTime", "DepDelay", "ArrTime", "ArrDelay", "Cancelled",
    "CancellationCode", "CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay",
    "LateAircraftDelay"
]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded"
}

for airport in iata_codes:
    for year in years:
        print(f"📥 Downloading {airport} - {year}...")
        payload = {
            "UserTableName": "On_Time_Performance",
            "DBShortName": "On_Time",
            "RawDataTable": "On_Time_Performance",
            "sqlstr": f"SELECT {','.join(fields)} FROM On_Time_Performance WHERE Origin = '{airport}' AND Year = {year}",
            "varlist": ",".join(fields),
            "grouplist": "",
            "suml": "",
            "sumRegion": "",
            "filter1": "title",
            "filter2": "title",
            "geo": "Origin",
            "time": "Year"
        }

        try:
            response = requests.post(BTS_CSV_URL, headers=headers, data=payload, timeout=60)
            if response.ok and len(response.content) > 1000:  # sanity check
                filename = f"{airport}_{year}.csv"
                filepath = os.path.join(DOWNLOAD_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"✅ Saved: {filename}")
            else:
                print(f"⚠️ Empty or failed data: {airport} - {year}")
        except Exception as e:
            print(f"❌ Error: {airport} - {year} | {str(e)}")

        time.sleep(1)  # gentle on server

print("🎉 Done downloading all requested data.")

