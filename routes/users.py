from fastapi import APIRouter
from models.users import User
from config.database import connection
from schemas.users import userEntity, listOfUserEntity
from config.constants import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from middleware.utils import verify_password, get_current_active_user, get_password_hash, authenticate_user,create_access_token
from datetime import datetime, timedelta


user_router = APIRouter()

@user_router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print('login form data', form_data.username, form_data.password)
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    username = user["username"]
    print('access token success', access_token)  
    update_resp = connection.local.user.update_one({"username": username}, {"$set": {"access_token": access_token, "token_type": 'bearer'}})
    print('update token resp', update_resp)
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.post("/signup")
async def signup(user: User):
    users = connection.local.user.find()
    for db_user in users:
        if user.username == db_user["username"]:
            return {"resp": "this user already exist", "username": user.username}
    user.hashed_password = get_password_hash(user.hashed_password)
    connection.local.user.insert_one(user.model_dump())
    return listOfUserEntity(connection.local.user.find())

@user_router.get("/users_test", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    print('user active 1')
    return current_user