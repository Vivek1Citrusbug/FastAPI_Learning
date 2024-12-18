from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status, responses
from models import UserModel
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, select, orm
from database import engine
from src.auth.schemas import (
    UserPublicModel,
    CreateUserModel,
    UpdateUserModel,
    TokenData,
    Token,
)
from models import UserModel
from database import SessionDep
from passlib.context import CryptContext
from typing import Annotated
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from  config import ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM,SECRET_KEY


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # for loadiing resources that need to be present before the start of the application
    create_db_and_tables()
    yield


def create_db_and_tables():
    """Creating database tables"""
    print("All database model created#######")
    SQLModel.metadata.create_all(engine)


app = FastAPI(lifespan=lifespan)


def verify_password(plain_password, hashed_password):
    ## hasing logic is remaining ###########
    # print("Plain password : ",plain_password,"hashd_ passeword : ",hashed_password)
    return plain_password == hashed_password
    # return pwd_context.verify(plain_password,hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(session: SessionDep, username: str):
    user = session.get(UserModel, username)
    print("############", user, "#############")
    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


def authenticate_user(session, username: str, password: str):
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
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


async def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post(
    "/token",
    tags=["Authentication"],
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get(
    "/users/me/",
    response_model=UserPublicModel,
    tags=["User"],
)
async def read_users_me(
    current_user: Annotated[UserPublicModel, Depends(get_current_active_user)],
):
    return current_user


@app.get(
    "/users/me/items/",
    tags=["User"],
)
async def read_own_items(
    current_user: Annotated[UserPublicModel, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


######################
##### Routes #########
######################


@app.get("/", tags=["Home"])
def index():
    return "Index Page"


@app.get(
    "/users",
    response_model=list[UserPublicModel],
    status_code=status.HTTP_200_OK,
    tags=["User"],
)
def list_users(
    session: SessionDep,
    current_user: Annotated[UserPublicModel, Depends(get_current_active_user)],
):
    users = session.exec(select(UserModel)).all()
    return users


@app.post(
    "/users",
    response_model=UserPublicModel,
    status_code=status.HTTP_201_CREATED,
    tags=["User"],
)
def crate_user(
    user: CreateUserModel,
    session: SessionDep,
    current_user: Annotated[UserPublicModel, Depends(get_current_active_user)],
):
    UserDatabase = UserModel.model_validate(user)
    session.add(UserDatabase)
    session.commit()
    session.refresh(UserDatabase)
    return UserDatabase


@app.get(
    "/users/{username}",
    response_model=UserPublicModel,
    status_code=status.HTTP_200_OK,
    tags=["User"],
)
def show_user_details(
    username: str,
    session: SessionDep,
    current_user: Annotated[UserPublicModel, Depends(get_current_active_user)],
):
    user_detail = session.get(UserModel, username)
    if not user_detail:
        raise HTTPException(status_code=404, detail="User not found")
    return user_detail


@app.patch(
    "/users/{username}",
    response_model=UserPublicModel,
    status_code=status.HTTP_200_OK,
    tags=["User"],
)
def update_user_details(
    username: str,
    user: UpdateUserModel,
    session: SessionDep,
    current_user: Annotated[UserPublicModel, Depends(get_current_active_user)],
):
    user_database_details = session.get(UserModel, username)
    if not user_database_details:
        raise HTTPException(status_code=404, detail="User not found")
    user_entered_data = user.model_dump(exclude_unset=True)
    user_database_details.sqlmodel_update(user_entered_data)
    session.add(user_database_details)
    session.commit()
    session.refresh(user_database_details)
    return user_database_details


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: Annotated[UserPublicModel, Depends(get_current_active_user)],
):
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"User deleted successfully": True}
