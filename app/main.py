from fastapi import FastAPI
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from api.routes import api_router
from websocket.handlers import web_router

app = FastAPI()

app.include_router(api_router)
app.include_router(web_router)