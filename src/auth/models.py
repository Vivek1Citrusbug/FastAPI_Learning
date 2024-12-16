from src.auth.schemas import UserBaseModel
from sqlmodel import Field

#############################
##### Database model ######
#############################


class UserModel(UserBaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sensitive_info: str
