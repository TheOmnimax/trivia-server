from pydantic import BaseModel
from google.cloud import datastore
from gcloud_utils.datastore import GcloudMemoryStorage
from daos import QuestionsDAO, CategoryDAO

class QuestionRetrieval:
  question_dao: QuestionsDAO
  memory_storage: GcloudMemoryStorage

class AllRetrieval(QuestionRetrieval):
  category_dao: CategoryDAO