from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path("/opt/homebrew/var/postgresql@18")   # your PGDATA
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

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "documents")
    
    # API (TO ADD)
    API_PORT = int(os.getenv("API_PORT", 8888))
    API_HOST = os.getenv("API_HOST", "localhost")

settings = Settings()
# 2. Database connection parameters
# conn_params = {
#         "host": "localhost",
#         "database": "GenAI-Capstone",
#         "user": "postgres",
#         "password": "Lenovo"
# }

##conn = psycopg2.connect(dbname="postgres", user="karthikkumarthirugnanam", host="localhost")

