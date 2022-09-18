
from google.cloud import datastore
from pydantic import validate_arguments
from daos.category_dao import CategoryDAO
from daos.question_dao import QuestionsDAO
from dependencies.model import AllRetrieval, WebSocketHelpers
from dependencies.model import QuestionRetrieval
from dependencies.websocket import ConnectionManager
from domains.game.model import Game, GameRoom, Player
from domains.trivia_game.model import RoundData, TriviaGame, TriviaPlayer
from gcloud_utils.datastore import GcloudMemoryStorage

datastore_client = datastore.Client()
memory_storage = GcloudMemoryStorage(
  client=datastore_client,
  pre_accepted=[Player, GameRoom, Game, TriviaGame, TriviaPlayer, RoundData,]
  )
question_dao = QuestionsDAO(client=datastore_client)
category_dao = CategoryDAO(client=datastore_client)
connection_manager = ConnectionManager()

def getClient():
  return datastore_client

def getMemoryStorage():
  return memory_storage

def questionRetrieval() -> QuestionRetrieval:
  return QuestionRetrieval(
    question_dao=question_dao,
    memory_storage=memory_storage
  )

def getConnectionManager() -> ConnectionManager:
  return connection_manager

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def getWebSocketHelpers() -> WebSocketHelpers:
  return WebSocketHelpers(
    memory_storage=memory_storage,
    connection_manager=connection_manager
  )

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def allRetrieval() -> AllRetrieval:
  return AllRetrieval(
    question_dao=question_dao,
    category_dao=category_dao,
    memory_storage=memory_storage,
    connection_manager=connection_manager
  )