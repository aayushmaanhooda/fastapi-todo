from fastapi import FastAPI, Depends, HTTPException, Path, Query
from typing import Annotated
from sqlalchemy.orm import Session
from database import engine, sessionLocal
import models
from models import Todos
from starlette import status
from pydantic import BaseModel, Field


app = FastAPI()

'''
Metadata is like a blueprint for your database.
It keeps track of all the tables and columns you’ve defined in your models.
Example: If your Todos model has id, title, description, etc., metadata knows these are the columns for the todos table.
It collects information about all the models (tables) defined with Base.
When you call create_all, metadata tells SQLAlchemy what tables need to be created in the database.

'''

"""
Base: Acts as the starting point for all models.
metadata: Keeps a blueprint of all tables and columns in your models.
create_all: Creates tables in the database based on your models, if they don’t already exist.
bind=engine: Specifies which database to create the tables in.

"""
models.Base.metadata.create_all(bind= engine)

def get_db():
    '''
    A session is like a temporary workspace for interacting with the database. It allows you to:
    Query data.
    Add, update, or delete records.
    Commit or rollback transactions.

    Why is it needed?

    A session ensures that each request gets its own isolated connection to the database.
    This prevents issues like data conflicts or shared states between requests.
    '''
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


'''
In FastAPI, yield allows you to cleanly manage resources like database sessions.
For example:
An endpoint (like /todos) gets the database session using get_db.
The endpoint performs its operations (e.g., querying or updating the database).
Once the endpoint finishes, the session is automatically closed, ensuring no leftover connections.
'''
'''
You write Session in Annotated[Session, Depends(get_db)] because the get_db function returns a SQLAlchemy Session object. This explicitly informs FastAPI (and other developers) about the type of object being injected.
'''

# dependency injecstion
db_dependency = Annotated[Session, Depends(get_db)]
'''
Role of TodoRequest
In this example:

Structure:

The API expects data in the form of a JSON object with fields:
title (string with a minimum length of 3).
description (string with 3–100 characters).
priority (integer between 1 and 5).
complete (boolean).
Validation:

If a client sends invalid data (e.g., a priority of -1 or a description that’s too long), FastAPI automatically rejects the request and returns a 422 Unprocessable Entity error with details about what went wrong.
Serialization:

TodoRequest also converts JSON data from the client into a Python object (todo_request) that you can work with in your endpoint.
Why Use It?

It ensures the data sent to your API meets the required format and constraints before your endpoint logic runs.
Without this, you would need to manually validate the input data in your code, which is error-prone and repetitive.
'''
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@app.get("/todo", status_code = status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code = status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if todo_model:
        return {
            "Message": f"Fetched successfully todo with id {todo_id}",
            "todo": todo_model
        }
    raise HTTPException(status_code= 404, detail = 'Todo not found')


@app.post("/todo",  status_code = status.HTTP_201_CREATED)
async def create_todo(db :db_dependency, todo_request : TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()
    return {
        "Message" :"Todo created successfully",
        "Todo": todo_request
    }


@app.put("/todo/{todo_id}", status_code = status.HTTP_204_NO_CONTENT)
async def update_todo(db : db_dependency, todo_request:TodoRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete
        db.add(todo_model)
        db.commit()
        return {
            "Message": f"Todo with id {todo_id} updated Successfully"
        }

    raise HTTPException(status_code =404, detail = "Todo not found")

@app.delete("/todo/{todo_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_todo(db : db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model:
        db.delete(todo_model)
        db.commit()
        return 
    raise HTTPException(status_code =404, detail = "Todo not found")
    
