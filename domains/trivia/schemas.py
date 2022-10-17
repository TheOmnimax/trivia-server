import imp
from typing import Optional, List
from pydantic import BaseModel

from .model import NewQuestionData, QuestionData

class NewQuestionSchema(NewQuestionData):
  pass

class QuestionSchema(QuestionData):
  pass

class QuestionUpdate(BaseModel):
  id: str
  label: Optional[str]
  categories: Optional[List[str]]
  choices: Optional[List[str]]
  shuffle: Optional[bool]
  shuffle_skip: Optional[List[int]]
  correct: Optional[int]