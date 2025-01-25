from database import Base
from sqlalchemy import Column, Integer, String, Boolean


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
class Todos(Base):
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key = True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)



