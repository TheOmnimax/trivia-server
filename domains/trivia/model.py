from typing import Optional
from pydantic import BaseModel

class NewQuestionData(BaseModel):
  label: str
  categories: list[str]
  choices: list[str]
  shuffle: bool
  shuffle_skip: Optional[list[int]]
  correct: int

class QuestionData(NewQuestionData):
  id: str

class NewCategory(BaseModel):
  label: str

class CategoryData(NewCategory):
  id: str