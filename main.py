import logging
logging.getLogger().addHandler(logging.StreamHandler()) # For testing

from os import environ

# environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\max-trivia-5a46a7a8eb28.json' # TESTING ONLY

import google.cloud.logging
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from routers.manage import category, question
from routers.play import creation, playing
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

from constants.constants import origins
from dependencies.sio import socket_app
from routers.play.creation import *
from routers.play.playing import *

client = google.cloud.logging.Client()
client.setup_logging()

# TODO: Set categories as labels
app = FastAPI()

app.mount('/', socket_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)

# @app.middleware('http')
# async def mw(request: Request, call_next):
#   logging.info('In middleware')
#   getHeapSize('Middleware')
#   return await call_next(request)

app.include_router(category.router)
app.include_router(question.router)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
