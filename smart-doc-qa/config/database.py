from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
DATA_DIR = Path("/opt/homebrew/var/postgresql@14")   # your PGDATA
LOG_FILE = DATA_DIR / "server.log"

class Settings:
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:/{DB_NAME}"
    )
    
settings = Settings()
# 2. Database connection parameters
# conn_params = {
#         "host": "localhost",
#         "database": "GenAI-Capstone",
#         "user": "postgres",
#         "password": "Lenovo"
# }

##conn = psycopg2.connect(dbname="postgres", user="karthikkumarthirugnanam", host="localhost")