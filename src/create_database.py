import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

def init_database():
    engine = create_engine(os.environ.get('DB_CONNECTION_STRING'))
    if not database_exists(engine.url):
        create_database(engine.url)
        