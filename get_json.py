from sqlalchemy import create_engine
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from datetime import datetime

from settings import HOST, USER, PW, PORT, DB, MAP_TOKEN

# Get interval time in timestamp
timestamp_min = datetime.timestamp(datetime(2019, 1, 1, 0, 0, 0))
timestamp_max = datetime.timestamp(datetime(2020, 1, 1, 0, 0, 0))

# Connect to db
engine = create_engine(f"mysql+pymysql://{USER}:{PW}@{HOST}:{PORT}/{DB}")

# Get conflicts between 2019 and 2020
SQL_QUERY = """
                SELECT 
                    data_id, country, latitude, longitude, fatalities, timestamp, event_type
                FROM 
                    conflicts
                WHERE 
                    timestamp BETWEEN %s AND %s
                AND
                    fatalities > 15;
            """

# Create dataframme with pandas
df = pd.read_sql_query(SQL_QUERY, engine, params=(timestamp_min, timestamp_max),
                    index_col='data_id')

# print(df.head())

# Create map with folium
m = folium.Map(
    location=[48.8534, 2.3488],
    tiles=MAP_TOKEN,
    attr='My data attr',
    zoom_start=3,
)


# mc = MarkerCluster() #Maybe marker cluster? 

# Add a circle marker for each conflict
for index, row in df.iterrows():
    dt = datetime.fromtimestamp(row['timestamp'])
    dt = dt.date()
    
    popup = folium.Popup(html=f"<b>Country</b><br>{row['country']}<br>\
<b>Event type</b><br>{row['event_type']}<br>\
<b>Fatalities</b><br>{row['fatalities']}<br>\
<b>Date</b><br>{dt}",
                        max_width='200%')

    folium.CircleMarker(
        location=(row['latitude'], row['longitude']),
        radius=row['fatalities'] / 50,
        color="#007849",
        popup=popup,
        fill=True,
    ).add_to(m)

# Save map to html file
m.save('conflict.html')





