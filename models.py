from sqlmodel import SQLModel, Field


# pydantic schemas
class UserBaseModel(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)


class UserPublicModel(UserBaseModel):
    id: int


class CrateUserModel(UserBaseModel):
    sensitive_info: str


class UpdateUserModel(UserBaseModel):
    name: str | None = None
    age: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    sensitive_info: str | None = None


# Database model
class UserModel(UserBaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sensitive_info: str
