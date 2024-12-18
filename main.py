from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.auth.dependencies import create_db_and_tables
# from src.auth.domain.services import get_password_hash,get_user
from src.auth.interface import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # for loadiing resources that need to be present before the start of the application
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(auth_router.router, prefix="/auth", tags=["Users"])



