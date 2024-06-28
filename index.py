###import statement

from fastapi import FastAPI
from routes.users import user_router

##Create app
app = FastAPI()

##Register your router
app.include_router(user_router)



