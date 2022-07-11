from typing import Optional
from fastapi import APIRouter, Depends
from game.doas import QuestionData, QuestionsDAO, QuestionUpdateData, AddQuestionData

from pydantic import BaseModel
from ..main import getClient

router = APIRouter()

class GetQuestions(BaseModel):
  categories: list[str]

class DeleteQuestion(BaseModel):
  id: str

@router.post('/get-questions')
async def getQuestions(data: GetQuestions, client = Depends(getClient)):
  question_dao = QuestionsDAO(client=client)
  question_data = question_dao.getQuestionsFromCats(cat_ids=data.categories)
  return [q.__dict__ for q in question_data]

@router.post('/add-question')
async def updateQuestion(data: AddQuestionData, client = Depends(getClient)):
  question_dao = QuestionsDAO(client=client)
  question_dao.addQuestion(question_data=data)


@router.post('/update-question')
async def updateQuestion(data: QuestionUpdateData, client = Depends(getClient)):
  question_dao = QuestionsDAO(client=client)
  question_dao.updateQuestion(question_data=data)

@router.post('/delete-question')
async def deleteQuestion(data: DeleteQuestion, client = Depends(getClient)):
  question_dao = QuestionsDAO(client=client)
  question_dao.deleteQuestion(data.id)
