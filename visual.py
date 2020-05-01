from sqlalchemy import create_engine
import pandas as pd
import folium
import json
from folium.plugins import MarkerCluster
from datetime import datetime

from settings import HOST, USER, PW, PORT, DB, MAP_TOKEN

# Get interval time in timestamp
date_min = datetime(2019, 1, 1, 0, 0, 0)
date_max = datetime(2020, 1, 1, 0, 0, 0)

# Connect to db
engine = create_engine(f"mysql+pymysql://{USER}:{PW}@{HOST}:{PORT}/{DB}")

# Get conflicts between 2019 and 2020
SQL_QUERY = """
                SELECT 
                    data_id, country, latitude, longitude, fatalities, event_date, event_type
                FROM 
                    conflicts
                WHERE 
                    event_date BETWEEN %s AND %s
                AND
                    fatalities > 15;
            """

# Create dataframme with pandas
df = pd.read_sql_query(SQL_QUERY, engine, params=(date_min, date_max))

df_choropleth = {'country':[], 'fatal_tot': []}
fatal_tot = 0

# Create DataFrame with total fatalities per country
for _, row in df.iterrows():
    if row['country'] not in df_choropleth['country']:
        df_choropleth['country'].append(row['country'])
        df_choropleth['fatal_tot'].append(row['fatalities'])
    else:
        index = df_choropleth['country'].index(row['country'])
        df_choropleth['fatal_tot'][index] += row['fatalities']



df_choropleth = pd.DataFrame(data=df_choropleth)

# Create map with folium
m = folium.Map(
    location=[48.8534, 2.3488],
    tiles=MAP_TOKEN,
    attr='My data attr',
    zoom_start=3,
)


# Create choropleth map depending on fatalities per country
countries_geo = "countries.geo.json"
choropleth = folium.Choropleth(
    geo_data=countries_geo,
    name='choropleth',
    data=df_choropleth,
    columns=['country', 'fatal_tot'],
    key_on='feature.properties.country',
    fill_color='OrRd',
    fill_opacity=0.4,
    nan_fill_color='white',
    line_opacity=0.2,
    highlight=True,
    line_color='black',
    legend_name='Fatalities in 2019'
).add_to(m)

folium.LayerControl(collapsed=True).add_to(m)


# Add a circle marker for each conflict
for index, row in df.iterrows():
    
    popup = folium.Popup(html=f"<b>Country</b><br>{row['country']}<br>\
<b>Event type</b><br>{row['event_type']}<br>\
<b>Fatalities</b><br>{row['fatalities']}<br>\
<b>Date</b><br>{row['event_date']}",
                        max_width='200%')

    folium.CircleMarker(
        location=(row['latitude'], row['longitude']),
        radius=row['fatalities']/30,
        color="#007849",
        popup=popup,
        fill=True,
    ).add_to(m)

# Save map to html file
m.save('conflict.html')





