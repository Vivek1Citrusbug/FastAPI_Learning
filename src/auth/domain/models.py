from src.auth.application.schemas import UserBaseModel
from sqlmodel import Field,SQLModel

#############################
##### Database model ######
#############################


class UserModel(UserBaseModel, table=True):
    username: str | None = Field(default=None, primary_key=True)    
    password: str

class AccessToken(SQLModel, table=True):  
    id: int = Field(default=None, primary_key=True)
    access_token: str
    token_type: str