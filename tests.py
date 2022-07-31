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
  gcloud_ms.getAndSet(
    id='t288rl',
    new_val_func=func
  )

if __name__ == '__main__':
  gcloudUpdate()