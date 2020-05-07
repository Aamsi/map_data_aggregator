import folium
import branca
import json
import pandas as pd
from app.fetch import FetcherConflicts
from app.settings import MAP_TOKEN

class CreateMap():
    """
        Create map
    """

    def __init__(self):
        self.m = None
        self.m1 = None
        self.choropleth = None
        self.running()

    def init_map(self):
        """ Initialize map to work on """
        self.m = folium.Map(location=[3.042048, 36.752887],
                            zoom_start=3,
                            tiles=None)
        folium.TileLayer(
                name='Choose a year',
                location=[3.042048, 36.752887],
                tiles=MAP_TOKEN,
                zoom_start=2,
                overlay=True,
                show=True,
                control=False,
                attr="<a href='https://www.mapbox.com/about/maps/'>© Mapbox</a> | \
<a href='https://www.openstreetmap.org/copyright'>© OpenStreetMap</a>"
            ).add_to(self.m)

    def choropleth_map(self, data, year):
        """ Create interactive map with different color given fatalities in a country """
        countries_geo = "/home/aamsi/Documents/data_aggreg_map/app/static/countries.geo.json"
        self.choropleth = folium.Choropleth(
            geo_data=data.geojson,
            name=f"{year}",
            data=data.df_choropleth,
            columns=['country', 'fatal_tot'],
            key_on='feature.properties.country',
            fill_color='OrRd',
            fill_opacity=0.4,
            nan_fill_color='white',
            line_opacity=0.2,
            highlight=True,
            line_color='black',
            legend_name=f"Total number of death in {year}",
            overlay=False,
            show=False,
            smooth_factor=0
        ).add_to(self.m)

        folium.GeoJsonTooltip(
            fields=['country', 'fatal_tot'],
            aliases=['Country:', f"Fatalities in {year}:"],
            localize=True
        ).add_to(self.choropleth.geojson)
       

    def marker(self, data, choropleth):
        """ Create marker for each row in dataframe"""
        for index, row in data.df.iterrows():

            html = f"<b>Country</b><br>{row['country']}<br><br>\
<b>Event type</b><br>{row['event_type']}<br><br>\
<b>Fatalities</b><br>{row['fatalities']}<br><br>\
<b>Date</b><br>{row['event_date']}<br><br>\
<b>Source(s)</b><br>{row['source']}<br><br>\
<b>Note</b><br>{row['notes']}"

            iframe = branca.element.IFrame(html=html, width=500, height=300)
            popup = folium.Popup(iframe, max_width=2000)

            folium.CircleMarker(
                location=(row['latitude'], row['longitude']),
                radius=row['fatalities']/30,
                color="#007849",
                popup=popup,
                fill=True,
            ).add_to(self.choropleth)

        self.choropleth.add_to(self.m)

    def save_map(self):
        """ Save map into html file """
        folium.LayerControl(position='bottomleft', collapsed=False).add_to(self.m)
        self.m.save('/home/aamsi/Documents/data_aggreg_map/app/templates/map_conflict.html')

    def folium_del_legend(self, choropleth):
        """
            Remove choropleth legends.
        """
        del_list = []
        for child in choropleth._children:
            if child.startswith('color_map'):
                del_list.append(child)

        for del_item in del_list:
            choropleth._children.pop(del_item)

        return choropleth

    def running(self):
        self.init_map()
        years = [year for year in range(2010, 2021)]
        for year in years:
            data = FetcherConflicts(year, year+1)
            self.choropleth_map(data, year)
            self.folium_del_legend(self.choropleth)
            self.marker(data, self.choropleth)
            print(f"{year} done")

        self.save_map()


mapping = CreateMap()