'''
This will help us to create a URL string
which will connect our fats api to our new database 
'''

'''
Your database.py file sets up the database connection and the tools 
needed for interacting with it in your FastAPI application.
'''
# Importing create_engine to establish a connection to the database
from sqlalchemy import create_engine

# Importing sessionmaker to create session objects for database interactions
from sqlalchemy.orm import sessionmaker

# Importing declarative_base to define database models (tables)
from sqlalchemy.ext.declarative import declarative_base

# Defining the database URL to connect to
# 'sqlite://': Specifies the database type (SQLite in this case)
# './todos.db': Relative path to the SQLite database file
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todoapp.db'

# Creating a database engine that manages the connection to the database
# connect_args={'check_same_thread': False}: Specific to SQLite, allows multiple threads to access the database
'''
When querying what engine exactly do:

Your Python code sends a query.
The engine translates it to SQL and sends it to the database.
The database processes the query and returns raw results.
The engine converts the raw results back into Python objects.
You get Python-friendly results to work with in your code.
Let me know if you’d like further details or examples!

'''
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# Creating a session factory to generate session objects
# autocommit=False: Disables automatic transaction commit, giving better control over transactions
# autoflush=False: Prevents the session from automatically flushing changes to the database
# bind=engine: Links the session to the database engine created above
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creating a base class for defining ORM models (database tables)
# All database models will inherit from this base class
Base = declarative_base()
