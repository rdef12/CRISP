import os
from sqlmodel import SQLModel, create_engine
from src.database.models import *

postgres_url = os.getenv("POSTGRES_URL")

if not postgres_url:
    postgres_url = "postgresql+psycopg2://postgres:password@database:5432/crisp_database" #127.0.0.1 changed to database to match the name of the container # this needed to be localhost:5432


engine = create_engine(postgres_url, echo=True)#, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
