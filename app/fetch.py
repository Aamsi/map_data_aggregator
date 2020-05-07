from sqlalchemy import create_engine
import pandas as pd
import folium
import json
from datetime import datetime

from app.settings import HOST, USER, PW, PORT, DB


class FetcherConflicts():
    """
        Fetch data used to create conflict map
    """

    SQL_QUERY_CONFLICTS = """
                        SELECT 
                            data_id, country, iso3, latitude, longitude, fatalities,
                            event_date, event_type, source, notes
                        FROM 
                            conflicts
                        WHERE 
                            event_date BETWEEN %s AND %s
                        AND
                            fatalities > 15;
                        """

    def __init__(self, year_min, year_max):
        self.year_min = year_min
        self.year_max = year_max
        self.engine = None
        self.df = None
        self.df_choropleth = None
        self.geojson = None
        self.connect()
        self.create_df()
        self.create_df_choropleth()
        self.create_geojson()

    def connect(self):
        """ Connect to database """
        self.engine = create_engine(f"mysql+pymysql://{USER}:{PW}@{HOST}:{PORT}/{DB}")
    
    def create_df(self):
        """ Create dataframe to use on the map """
        date_min = datetime(self.year_min, 1, 1, 0, 0, 0)
        date_max = datetime(self.year_max, 1, 1, 0, 0, 0)
        self.df = pd.read_sql_query(self.SQL_QUERY_CONFLICTS, self.engine,
                               params=(date_min, date_max))

    def create_df_choropleth(self):
        """ Create df to use on choropleth (maybe useless)"""
        self.df_choropleth = {'country':[], 'iso3': [], 'fatal_tot': []}
        fatal_tot = 0

        # Create DataFrame with total fatalities per country for choropleth
        for _, row in self.df.iterrows():
            if row['iso3'] not in self.df_choropleth['iso3']:
                self.df_choropleth['country'].append(row['country'])
                self.df_choropleth['iso3'].append(row['iso3'])
                self.df_choropleth['fatal_tot'].append(row['fatalities'])
            else:
                index = self.df_choropleth['iso3'].index(row['iso3'])
                self.df_choropleth['fatal_tot'][index] += row['fatalities']

        self.df_choropleth = pd.DataFrame(data=self.df_choropleth)

    def create_geojson(self):
        """ Create geojson for choropleth map """
        countries_geo = "/home/aamsi/Documents/data_aggreg_map/app/static/countries.geo.json"
        r_file = open(countries_geo, "r")
        json_obj = json.load(r_file)
        r_file.close()
        self.geojson = {'type':'FeatureCollection', 'features':[]}
        for _, row in self.df_choropleth.iterrows():
            for prop in json_obj['features']:
                if prop['id'] == row['iso3']:
                    feature = {'type': 'Feature',
                            'properties': {'iso3': row['iso3'],
                                           'country': row['country'],
                                           'fatal_tot': row['fatal_tot']},
                            'geometry': {'type': prop['geometry']['type'],
                                         'coordinates': prop['geometry']['coordinates']}}
                    self.geojson['features'].append(feature)



# Wanted to add total fatalities to countries.geo.json but ended doing the opposite
# def update_json(json_file):
#     r_file = open(json_file, "r")
#     json_object = json.load(r_file)
#     r_file.close()
#     years = [year for year in range(1999, 2021)]
#     for year in years:
#         fetcher = FetcherConflicts(year, year+1)
#         for _, row in fetcher.df_choropleth.iterrows():
#             for prop in json_object['features']:
#                 if row['country'] == prop['properties']['country']:
#                     prop['properties'][f"fatal_{year}"] = row['fatal_tot']
    
#     o_file = open(json_file, "w")
#     json.dump(json_object, o_file)
#     o_file.close()

# update_json("/home/aamsi/Documents/data_aggreg_map/app/static/countries.geo.json")


