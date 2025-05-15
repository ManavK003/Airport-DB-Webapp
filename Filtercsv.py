import pandas as pd
import os

# IATA codes to filter by
iata_codes = [
    "BOS", "OAK", "OGG", "MCI", "PHX", "SFO", "LAX", "CLE", "CVG", "EWR",
    "DAL", "FLL", "SLC", "IAH", "HOU", "PIT", "MIA", "SEA", "IND", "SAT",
    "RDU", "BUR", "DTW", "TPA", "DFW", "AUS", "STL", "ATL", "JAX", "IAD",
    "MKE", "PDX", "HNL", "SAN", "ONT", "MDW", "SJC", "DEN", "PHL", "RSW",
    "JFK", "RNO", "SMF", "ORD", "BWI", "MSP", "SNA", "CLT", "LAS", "MCO"
]

# Ensure output directory exists
output_dir = "ML Data/Arrival_Departure"
os.makedirs(output_dir, exist_ok=True)

# Load CSV
input_file = "T_ONTIME_REPORTINGJan2018.csv"
df = pd.read_csv(input_file)

# Filter by ORIGIN airport codes
filtered_df = df[df["ORIGIN"].isin(iata_codes)]

# Save filtered data
output_file = os.path.join(output_dir, "jan2018.csv")
filtered_df.to_csv(output_file, index=False)

print(f"✅ Filtered CSV saved to: {output_file}")
