from fastapi import FastAPI
from routers import auth , todos
import models
from database import engine

app = FastAPI()

'''
Metadata is like a blueprint for your database.
It keeps track of all the tables and columns you’ve defined in your models.
Example: If your Todos model has id, title, description, etc., metadata knows these are the columns for the todos table.
It collects information about all the models (tables) defined with Base.
When you call create_all, metadata tells SQLAlchemy what tables need to be created in the database.

Base: Acts as the starting point for all models.
metadata: Keeps a blueprint of all tables and columns in your models.
create_all: Creates tables in the database based on your models, if they don’t already exist.
bind=engine: Specifies which database to create the tables in. 
'''
models.Base.metadata.create_all(bind= engine)
app.include_router(auth.router)
app.include_router(todos.router)

