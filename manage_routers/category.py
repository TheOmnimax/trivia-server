from typing import Optional
from fastapi import APIRouter, Depends
from game.doas import QuestionData, QuestionsDAO, QuestionUpdateData, AddQuestionData, CategoryDAO

from pydantic import BaseModel
from ..main import getClient

router = APIRouter()

@router.post('/get-categories')
async def getQuestions(data: BaseModel, client = Depends(getClient)):
  category_dao = CategoryDAO(client=client)
  categories = category_dao.getCategories()
  return [c.__dict__ for c in categories]

class CategoryLabel(BaseModel):
  label: str

@router.post('/add-category')
async def addCategory(data: CategoryLabel, client = Depends(getClient)):
  category_dao = CategoryDAO(client=client)
  # TODO: Add parents and children
  category_dao.addCat(data.label)

class CategoryId(BaseModel):
  id: str

@router.post('/delete-category')
async def deleteCategory(data: CategoryId, client = Depends(getClient)):
  category_dao = CategoryDAO(client=client)
  category_dao.deleteCat(data.id)

