from pydantic import BaseModel
from dependencies.websocket import ConnectionManager
from gcloud_utils.datastore import GcloudMemoryStorage
from daos import QuestionsDAO, CategoryDAO

class QuestionRetrieval(BaseModel, arbitrary_types_allowed=True): # TODO: Question: Is it okay to allow arbitrary types like this?
  question_dao: QuestionsDAO
  memory_storage: GcloudMemoryStorage

class WebSocketHelpers(BaseModel, arbitrary_types_allowed=True):
  memory_storage: GcloudMemoryStorage
  connection_manager: ConnectionManager


class AllRetrieval(QuestionRetrieval, arbitrary_types_allowed=True):
  category_dao: CategoryDAO
  connection_manager: ConnectionManager