from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from src.auth.domain.models import UserModel
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, or_, select, orm
from database import engine
from typing import Annotated
from src.auth.application.schemas import (
    UserPublicModel,
    CreateUserModel,
    UpdateUserModel,
    Token,
)
from database import SessionDep
from fastapi.security import OAuth2PasswordRequestForm
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.auth.dependencies import (
    create_db_and_tables,
)
# from src.auth.domain.services import get_password_hash,get_user
from src.auth.interface import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # for loadiing resources that need to be present before the start of the application
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(auth_router.router, prefix="/auth", tags=["Users"])



