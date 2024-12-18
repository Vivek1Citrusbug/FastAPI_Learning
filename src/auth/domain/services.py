# authentication/services.py
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from passlib.context import CryptContext
from .models import UserModel
from src.auth.application.schemas import Token
from config import ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM,SECRET_KEY
import jwt
from database import SessionDep

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    ## hasing logic is remaining ###########
    # print("Plain password : ",plain_password,"hashd_ passeword : ",hashed_password)
    # return plain_password == hashed_password
    return pwd_context.verify(plain_password,hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(session, username: str, password: str):
    user = get_user(session, username)
    print("########", user)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def get_user(session: SessionDep, username: str):
    user = session.get(UserModel, username)
    print("############", user, "#############")
    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user

