from dataclasses import dataclass
from pydantic import BaseModel
from google.cloud import datastore
from dependencies.websocket import ConnectionManager
from gcloud_utils.datastore import GcloudMemoryStorage
from daos import QuestionsDAO, CategoryDAO

class QuestionRetrieval(BaseModel, arbitrary_types_allowed=True): # TODO: Question: Is it okay to allow arbitrary types like this?
  question_dao: QuestionsDAO
  memory_storage: GcloudMemoryStorage

class WebSocketHelpers(BaseModel):
  memory_storage: GcloudMemoryStorage
  connection_manager: ConnectionManager


class AllRetrieval(QuestionRetrieval):
  category_dao: CategoryDAO
  connection_manager: ConnectionManager