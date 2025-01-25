from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Annotated
from sqlalchemy.orm import Session
from database import sessionLocal
from models import Todos
from starlette import status
from pydantic import BaseModel, Field

router = APIRouter(
    prefix='/todo',
    tags=['Todo']
)

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


@router.get("", status_code = status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@router.get("/{todo_id}", status_code = status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if todo_model:
        return {
            "Message": f"Fetched successfully todo with id {todo_id}",
            "todo": todo_model
        }
    raise HTTPException(status_code= 404, detail = 'Todo not found')


@router.post("",  status_code = status.HTTP_201_CREATED)
async def create_todo(db :db_dependency, todo_request : TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()
    return {
        "Message" :"Todo created successfully",
        "Todo": todo_request
    }


@router.put("/{todo_id}", status_code = status.HTTP_204_NO_CONTENT)
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

@router.delete("/{todo_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_todo(db : db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model:
        db.delete(todo_model)
        db.commit()
        return 
    raise HTTPException(status_code =404, detail = "Todo not found")
    
