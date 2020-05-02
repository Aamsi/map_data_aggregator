from sqlalchemy import create_engine
import pandas as pd
import folium
# from folium.plugins import MarkerCluster
from datetime import datetime

from settings import HOST, USER, PW, PORT, DB


class FetcherConflicts():
    """
        Fetch data used to create conflict map
    """

    SQL_QUERY_CONFLICTS = """
                        SELECT 
                            data_id, country, latitude, longitude, fatalities, event_date, event_type
                        FROM 
                            conflicts
                        WHERE 
                            event_date BETWEEN %s AND %s
                        AND
                            fatalities > 15;
                        """

    def __init__(self, year):
        self.year = year
        self.engine = None
        self.df = None
        self.df = None
        self.connect()
        self.create_df()
        self.create_df_choropleth()

    def connect(self):
        """ Connect to database """
        self.engine = create_engine(f"mysql+pymysql://{USER}:{PW}@{HOST}:{PORT}/{DB}")
    
    def create_df(self):
        """ Create dataframe to use on the map """
        date_min = datetime(self.year, 1, 1, 0, 0, 0)
        date_max = datetime(self.year + 1, 1, 1, 0, 0, 0)
        self.df = pd.read_sql_query(self.SQL_QUERY_CONFLICTS, self.engine,
                               params=(date_min, date_max))

    def create_df_choropleth(self):
        """ Create df to use on choropleth """
        self.df_choropleth = {'country':[], 'fatal_tot': []}
        fatal_tot = 0

        # Create DataFrame with total fatalities per country
        for _, row in self.df.iterrows():
            if row['country'] not in self.df_choropleth['country']:
                self.df_choropleth['country'].append(row['country'])
                self.df_choropleth['fatal_tot'].append(row['fatalities'])
            else:
                index = self.df_choropleth['country'].index(row['country'])
                self.df_choropleth['fatal_tot'][index] += row['fatalities']

        self.df_choropleth = pd.DataFrame(data=self.df_choropleth)
