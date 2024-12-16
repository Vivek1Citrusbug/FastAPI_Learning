from fastapi import FastAPI, HTTPException, status, responses
from src.auth.models import UserModel
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, select,orm
from database import engine
from src.auth.schemas import (
    UserPublicModel,
    CrateUserModel,
    UpdateUserModel,
)
from src.auth.models import UserBaseModel, UserModel
from database import SessionDep


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
def list_users(session: SessionDep):
    users = session.exec(select(UserModel)).all()
    return users


@app.post(
    "/users",
    response_model=UserPublicModel,
    status_code=status.HTTP_201_CREATED,
    tags=["User"],
)
def crate_user(user: CrateUserModel, session: SessionDep):
    UserDatabase = UserModel.model_validate(user)
    session.add(UserDatabase)
    session.commit()
    session.refresh(UserDatabase)
    return UserDatabase


@app.get(
    "/users/{user_id}",
    response_model=UserPublicModel,
    status_code=status.HTTP_200_OK,
    tags=["User"],
)
def show_user_details(user_id: int, session: SessionDep):
    user_detail = session.get(UserModel, user_id)
    if not user_detail:
        raise HTTPException(status_code=404, detail="User not found")
    return user_detail


@app.patch(
    "/users/{user_id}",
    response_model=UserPublicModel,
    status_code=status.HTTP_200_OK,
    tags=["User"],
)
def update_user_details(user_id: int, user: UpdateUserModel, session: SessionDep):
    user_database_details = session.get(UserModel, user_id)
    if not user_database_details:
        raise HTTPException(status_code=404, detail="User not found")
    user_entered_data = user.model_dump(exclude_unset=True)
    user_database_details.sqlmodel_update(user_entered_data)
    session.add(user_database_details)
    session.commit()
    session.refresh(user_database_details)
    return user_database_details


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def delete_user(user_id: int, session: SessionDep):
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"User deleted successfully": True}
