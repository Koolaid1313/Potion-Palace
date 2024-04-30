import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    local = True
    
    dotenv.load_dotenv()
    
    if local:
        return os.environ.get("LOCAL_URI")
    else:
        return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)