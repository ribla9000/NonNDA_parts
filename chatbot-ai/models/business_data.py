from pydantic import BaseModel, field_validator
from typing import Union


class BusinessDataModel(BaseModel):
    external_id: str
    user_id: Union[None, str] = None
    content: str


class ChatModel(BaseModel):
    user_id: Union[None, str] = None
    content: str
    user_name: Union[None, str] = None
