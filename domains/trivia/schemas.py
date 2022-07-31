import imp
from typing import Optional
from pydantic import BaseModel

from .model import NewQuestionData, QuestionData

class NewQuestionSchema(NewQuestionData):
  pass

class QuestionSchema(QuestionData):
  pass

class QuestionUpdate(BaseModel):
  id: str
  label: Optional[str]
  categories: Optional[list[str]]
  choices: Optional[list[str]]
  shuffle: Optional[bool]
  shuffle_skip: Optional[list[int]]
  correct: Optional[int]