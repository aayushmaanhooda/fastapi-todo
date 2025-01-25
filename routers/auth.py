from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Annotated
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import sessionLocal
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
 

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

SECRET_KEY = 'd3cc50bc1a64db9397349a31d9535932b7b6d712a9e547108e914b5c0db6f6a8'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# this hold url cleint sent with jwt
oauth2_bearer = OAuth2PasswordBearer(tokenUrl = "auth/token")

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

# dependency injecstion
db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password:str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username:str , user_id: int, expiers_delta: timedelta):
    encode = {
        "sub": username,
        "id": user_id
    }
    expires = datetime.now(timezone.utc) + expiers_delta
    encode.update({
        "exp": expires
    })
    return jwt.encode(encode, SECRET_KEY, algorithm =ALGORITHM)

async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if not username or not user_id:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Could not validate")
        return {
            "username": username,
            "user_id": user_id
        }
    except JWTError:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Could not validate")




class UserRequest(BaseModel):
    email :str
    username :str
    first_name :str
    last_name :str
    password :str
    role :str

class Token(BaseModel):
    access_token :str
    token_type :str


@router.get("", status_code = status.HTTP_200_OK)
async def get_users(db: db_dependency):
    return db.query(Users).all()

@router.post("", status_code = status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserRequest):

    user_model = Users(
        email= user_request.email,
        username= user_request.username,
        first_name= user_request.first_name,
        last_name= user_request.last_name,
        hashed_password= bcrypt_context.hash(user_request.password),
        role= user_request.role,
        is_active= True,
    )

    db.add(user_model)
    db.commit()
    return{
        "Message" : "User created Successfully"
    }


'''
Annotated
Annotated combines both:

The type hint (OAuth2PasswordRequestForm).
The dependency logic (Depends()).

This way, it explicitly declares that:

The form_data parameter must be an instance of OAuth2PasswordRequestForm.
FastAPI should use Depends() to handle how form_data is created.


'''


'''
Authentication: Happens during login. The server verifies the username/password and issues a JWT token.
Authorization: Happens during each request. The server uses the token to decide whether the user can perform the requested action.
'''
@router.post("/token", response_model = Token)
async def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Could not validate")

    token  = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {
        "Message": "Successful Authentication",
        "access_token": token,
        "token_type" : "Bear"
    }

'''
Without the secret key, you cannot verify:

If the token was issued by the server: Anyone could create a fake JWT and send it to the server if the secret key isn't used for signing.

If the token has been tampered with: Since the payload is not encrypted, anyone can modify the data in the token. Without the secret key, the server cannot detect these changes.

JWT IS AUTHROIZATION METHOD
JWT HEADER + JWT PAYLOAD + JWT SIGNATURE = JSON WEB TOKEN
JWT SIGNATURE contains that secret key which we need to verfiy every time when new request comes from frontend for that user
'''