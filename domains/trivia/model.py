from typing import Optional, List
from pydantic import BaseModel

class NewQuestionData(BaseModel):
  label: str
  categories: List[str]
  choices: List[str]
  shuffle: bool
  shuffle_skip: Optional[List[int]]
  correct: int

class QuestionData(NewQuestionData):
  id: str

class NewCategory(BaseModel):
  label: str

class CategoryData(NewCategory):
  id: str