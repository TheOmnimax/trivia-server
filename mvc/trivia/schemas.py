import imp
from typing import Optional
from pydantic import BaseModel
from daos.base_models import QuestionData

from model import NewQuestionData, QuestionData

class NewQuestionSchema(NewQuestionData):
  pass

class QuestionSchema(QuestionData):
  pass

