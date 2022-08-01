import logging
logging.getLogger().addHandler(logging.StreamHandler()) # For testing

from os import environ

environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\max-trivia-5a46a7a8eb28.json' # TESTING ONLY

import google.cloud.logging
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import datastore

from fastapi import FastAPI, APIRouter
from routers.manage import category, question
from routers.play import creation, playing
from gcloud_utils.datastore import GcloudMemoryStorage
from dependencies import dependencies

client = google.cloud.logging.Client()
client.setup_logging()



# TODO: Set categories as labels
app = FastAPI()

router = APIRouter()

origins = [
    'http://localhost',
    'http://localhost:8080',
    'http://localhost:50497',
    'https://localhost:50497',
    'https://max-trivia.web.app',
    'http://max-trivia.web.app',
    'https://trivia-question-manager.web.app',
    'http://trivia-question-manager.web.app',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.middleware('http')
# async def mw(request: Request, call_next):
#   logging.info('In middleware')
#   getHeapSize('Middleware')
#   return await call_next(request)


app.include_router(creation.router)
app.include_router(playing.router)
app.include_router(category.router)
app.include_router(question.router)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
