
from google.cloud import datastore
from daos.category_dao import CategoryDAO
from daos.question_dao import QuestionsDAO
from dependencies.model import AllRetrieval
from model import QuestionRetrieval
from gcloud_utils.datastore import GcloudMemoryStorage

datastore_client = datastore.Client()
memory_storage = GcloudMemoryStorage(client=datastore_client, kind='game_room')
question_dao = QuestionsDAO(client=datastore_client)
category_dao = CategoryDAO(client=datastore_client)

def getClient():
  return datastore_client

def getMemoryStorage():
  return memory_storage

def questionRetrieval() -> QuestionRetrieval:
  return QuestionRetrieval(
    question_dao=question_dao,
    memory_storage=memory_storage
  )

def allRetrieval() -> AllRetrieval:
  return AllRetrieval(
    question_dao=question_dao,
    category_dao=category_dao,
    memory_storage=memory_storage
  )