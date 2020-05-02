import folium
import branca
import pandas as pd
from app.fetch import FetcherConflicts
from app.settings import MAP_TOKEN

class CreateMap():
    """
        Create map
    """

    def __init__(self):
        self.fetcher = FetcherConflicts(2015, 2020)
        self.m = None
        self.choropleth = None
        self.init_map()
        self.choropleth_map()
        self.marker()
        self.save_map()

    def init_map(self):
        """ Initialize map to work on """
        self.m = folium.Map(
                location=[48.8534, 2.3488],
                tiles=MAP_TOKEN,
                attr='My data attr',
                zoom_start=3,
            )

    def choropleth_map(self):
        """ Create interactive map with different color given fatalities in a country """
        countries_geo = "/home/aamsi/Documents/data_aggreg_map/app/static/countries.geo.json"
        self.choropleth = folium.Choropleth(
            geo_data=countries_geo,
            name='choropleth',
            data=self.fetcher.df_choropleth,
            columns=['country', 'fatal_tot'],
            key_on='feature.properties.country',
            fill_color='OrRd',
            fill_opacity=0.4,
            nan_fill_color='white',
            line_opacity=0.2,
            highlight=True,
            line_color='black',
            legend_name='Total number of death from 2015 to 2020'
        ).add_to(self.m)

    def marker(self):
        """ Create marker for each row in dataframe"""
        for index, row in self.fetcher.df.iterrows():

            html = f"<b>Country</b><br>{row['country']}<br><br>\
<b>Event type</b><br>{row['event_type']}<br><br>\
<b>Fatalities</b><br>{row['fatalities']}<br><br>\
<b>Date</b><br>{row['event_date']}"

            iframe = branca.element.IFrame(html=html, width=400, height=200)
            popup = folium.Popup(iframe, max_width=2000)

            folium.CircleMarker(
                location=(row['latitude'], row['longitude']),
                radius=row['fatalities']/30,
                color="#007849",
                popup=popup,
                fill=True,
            ).add_to(self.m)

    def save_map(self):
        """ Save map into html file """
        self.m.save('/home/aamsi/Documents/data_aggreg_map/app/templates/map_conflict.html')


mapping = CreateMap()