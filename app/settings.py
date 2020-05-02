from dotenv import load_dotenv
load_dotenv()

import os

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
USER = os.getenv("USER_DB")
PW = os.getenv("PW")
DB = os.getenv("DB")
MAP_TOKEN = os.getenv('MAP_TOKEN')