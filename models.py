from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey 


'''
When you inherit Base, you tell SQLAlchemy that this class (Todos) is a database table.
It automatically connects your Python class to the database table.
It ensures that SQLAlchemy knows how to generate SQL commands for this class.

Without inheriting Base, SQLAlchemy won’t recognize the class as a database model.
'''

# Defining the Todos model, which represents the 'todos' table in the database
'''
An index in a database is a data structure (usually a B-tree or hash table) that allows the database to quickly 
locate rows without having to scan every single row in the table.
'''
class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key = True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)


class Todos(Base):
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key = True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(String, ForeignKey("users.id"))



