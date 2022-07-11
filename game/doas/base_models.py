from typing import Optional
from pydantic import BaseModel

class AddQuestionData(BaseModel):
  label: str
  categories: list[str]
  choices: list[str]
  shuffle: bool
  shuffle_skip: Optional[list[int]]
  correct: int

class QuestionData(AddQuestionData):
  id: str

class QuestionUpdateData(BaseModel):
  id: str
  label: Optional[str]
  categories: Optional[list[str]]
  choices: Optional[list[str]]
  shuffle: Optional[bool]
  shuffle_skip: Optional[list[int]]
  correct: Optional[int]