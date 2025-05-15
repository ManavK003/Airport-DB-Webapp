from meteostat import Stations, Hourly
from datetime import datetime, timedelta
import pandas as pd
import os

# Load airport list
airport_df = pd.read_csv('real_airports.csv')

# Filter US airports with valid IATA and coordinates
us_airports = airport_df[
    (airport_df['Country'] == 'United States') &
    (airport_df['IATA'].notnull()) &
    (airport_df['Latitude'].notnull()) &
    (airport_df['Longitude'].notnull())
]

# Save the filtered US airports to a new CSV file
output_file = 'us_airports.csv'
us_airports.to_csv(output_file, index=False)
print(f"Saved {len(us_airports)} US airports to {output_file}")