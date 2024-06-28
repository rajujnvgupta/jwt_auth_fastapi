from pydantic import BaseModel
from fastapi import APIRouter
from config.database import connection
from schemas.users import userEntity, listOfUserEntity
from typing import Optional
from bson import ObjectId

class User(BaseModel):
    username: str
    email: str
    hashed_password: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None


