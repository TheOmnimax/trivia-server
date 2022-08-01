import json
from dependencies.dependencies import allRetrieval
from tools.json_tools import JsonConverter
from daos import CategoryDAO, QuestionsDAO
from domains.trivia.schemas import QuestionUpdate, NewQuestionSchema, QuestionSchema
from gcloud_utils.datastore import GcloudMemoryStorage

from google.cloud import datastore
from os import environ


environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\max-trivia-5a46a7a8eb28.json' # TESTING ONLY

def getQuestion():
  question_dao = QuestionsDAO(client=datastore.Client())
  question_data = question_dao.getQuestion('6681294850532578')
  print(question_data)
  # question_data.label = 'Which of these is NOT an Eeveelution?'
  # question_dao.updateQuestion(question_data)
#   json_converter = JsonConverter()

#   test_data = QuestionUpdateData(
#     id=1,
#     label='Hi'
#   )
#   json_data = json_converter.baseModelToJson(test_data)

def addQuestion():
  question_dao = QuestionsDAO(client=datastore.Client())
  question_dao.addQuestion(NewQuestionSchema(
    label='Hi',
    categories=[1,2],
    choices=['One', 'Two'],
    shuffle=True,
    correct=0
  ))

def getQuestionsFromCats():
  question_dao = QuestionsDAO(client=datastore.Client())
  question_data = question_dao.getQuestionsFromCats(['1', '2', 'Video games'])
  print(question_data)

def gcloudCreate():
  gcloud_ms = GcloudMemoryStorage(
    client=datastore.Client(),
    kind='test'
  )
  gcloud_ms.create({'test': True})

def gcloudUpdate():
  gcloud_ms = GcloudMemoryStorage(
    client=datastore.Client(),
    kind='test'
  )
  def func(data):
    data['test'] = 'Changed!'
  gcloud_ms.transaction(
    id='t288rl',
    new_val_func=func
  )

def jsonTest():
  json_converter = JsonConverter()
  from domains.trivia_game import model as tg_model
  from domains.game import model as game_model
  room = game_model.GameRoom(
    host_id='1',
    members={
      '1': game_model.Player(
        id='1',
        name='Max'
      )
    }
  )
  json_data = json_converter.baseModelToJson(room)
  print(json_data)
  reconverted = json_converter.jsonToBaseModel(json_data)
  print(type(reconverted))
  print(reconverted)

def allRetrievalTest():
  return allRetrieval()

if __name__ == '__main__':
  print(allRetrievalTest().__dict__)
