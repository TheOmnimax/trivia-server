from typing import Optional, List
from fastapi import APIRouter, Depends
from daos import QuestionsDAO
from domains.trivia.schemas import QuestionUpdate, NewQuestionSchema, QuestionSchema
from pydantic import BaseModel
from daos.utils import getClient

router = APIRouter()

class GetQuestions(BaseModel):
  categories: Optional[List[str]]

class DeleteQuestion(BaseModel):
  id: str

@router.post('/get-questions')
async def getQuestions(data: GetQuestions, client = Depends(getClient)):
  question_dao = QuestionsDAO(client=client)
  if data.categories == None:
    question_data = question_dao.getAllQuestions()
  else:
    question_data = question_dao.getQuestionsFromCats(cat_ids=data.categories)
  return [q.__dict__ for q in question_data]

@router.post('/add-question')
async def updateQuestion(data: NewQuestionSchema, client = Depends(getClient)):
  question_dao = QuestionsDAO(client=client)
  question_dao.addQuestion(question_data=data)


@router.post('/update-question')
async def updateQuestion(data: QuestionUpdate, client = Depends(getClient)):
  question_dao = QuestionsDAO(client=client)
  question_dao.updateQuestion(question_data=data)

@router.post('/delete-question')
async def deleteQuestion(data: DeleteQuestion, client = Depends(getClient)):
  question_dao = QuestionsDAO(client=client)
  question_dao.deleteQuestion(data.id)
