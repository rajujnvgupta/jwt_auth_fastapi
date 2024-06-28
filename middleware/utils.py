
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.database import connection 
from models.users import User
from schemas.users import userEntity, listOfUserEntity
from config.constants import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    print('get password hash', password)
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    print('print 1')
    to_encode = data.copy()
    print('print 2', to_encode)

    if expires_delta:
        print('print 3', expires_delta)
        expire = datetime.utcnow() + expires_delta
        print('print 4', expire )

    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(username: str):
    # user = User.model_dump()
    user_obj = connection.local.user.find()
    # data = userEntity(user_obj.collection.find())
    # print('user dara', data)
    print('retrived user', user_obj.retrieved)
    for user in list(user_obj):
        print('user data', user)
        # user = json.dumps(user)
        if user["username"] == username:
            return user
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        print('passwrod verification failed')
        return False
    print('passwrod verification success')
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    print('user active 6')
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print('user active 7')

    try:
        print('token gen', token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print('raju payload', payload)
        username: str = payload.get("sub")
        print('rajus decode user', username)
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    
    user = get_user(username=username)
    print('after decoded', user)
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    print('user active 2', current_user)
    if current_user['access_token'] is None:
        print('user active 4')
        raise HTTPException(status_code=400, detail="Inactive user")
    print('user active 5')
    return current_user