# import json
# from dependencies.dependencies import allRetrieval
# from domains.game.model import GameRoom, Player
# from domains.trivia.model import CategoryData, QuestionData
# from domains.trivia_game.model import TriviaGame
# from tools.json_tools import JsonConverter
# from daos import CategoryDAO, QuestionsDAO
# from domains.trivia.schemas import QuestionUpdate, NewQuestionSchema, QuestionSchema
from domains.trivia.model import QuestionData
# from .domains.trivia.schemas import QuestionSchema
from gcloud_utils.datastore import GcloudMemoryStorage

from google.cloud import datastore
from os import environ


environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\max-trivia-5a46a7a8eb28.json' # TESTING ONLY

# def getQuestion():
#   question_dao = QuestionsDAO(client=datastore.Client())
#   question_data = question_dao.getQuestion('6681294850532578')
#   # question_data.label = 'Which of these is NOT an Eeveelution?'
#   # question_dao.updateQuestion(question_data)
# #   json_converter = JsonConverter()

# #   test_data = QuestionUpdateData(
# #     id=1,
# #     label='Hi'
# #   )
# #   json_data = json_converter.baseModelToJson(test_data)

# def addQuestion():
#   question_dao = QuestionsDAO(client=datastore.Client())
#   question_dao.addQuestion(NewQuestionSchema(
#     label='Hi',
#     categories=[1,2],
#     choices=['One', 'Two'],
#     shuffle=True,
#     correct=0
#   ))

# def getQuestionsFromCats():
#   question_dao = QuestionsDAO(client=datastore.Client())
#   question_data = question_dao.getQuestionsFromCats(['1', '2', 'Video games'])

# def gcloudCreate():
#   gcloud_ms = GcloudMemoryStorage(
#     client=datastore.Client(),
#     kind='test'
#   )
#   gcloud_ms.create({'test': True})

# def gcloudUpdate():
#   gcloud_ms = GcloudMemoryStorage(
#     client=datastore.Client(),
#     kind='test'
#   )
#   def func(data):
#     data['test'] = 'Changed!'
#   gcloud_ms.transaction(
#     id='t288rl',
#     new_val_func=func
#   )

# def jsonTest():
#   json_converter = JsonConverter()
#   from domains.trivia_game import model as tg_model
#   from domains.game import model as game_model
#   room = game_model.GameRoom(
#     host_id='1',
#     members={
#       '1': game_model.Player(
#         id='1',
#         name='Max'
#       )
#     }
#   )
#   json_data = json_converter.baseModelToJson(room)
#   print(json_data)
#   reconverted = json_converter.jsonToBaseModel(json_data)
#   print(type(reconverted))
#   print(reconverted)

# # def allRetrievalTest():
# #   return allRetrieval()

# def getTestData():
#   return GameRoom(
#     host_id='3p3hw1',
#     members={'3p3hw1': Player(id='3p3hw1', name='', score=0)},
#     game=TriviaGame(
#       players={'3p3hw1': Player(id='3p3hw1', name='', score=0)},
#       categories=[
#         CategoryData(label='Pop culture',
#         id='19g8pnv6jujxzli9')],
#         questions=[
#           QuestionData(
#             label='Which of these is NOT an Eeveelution?',
#             categories=['19g8pnv6jujxzli9', '5eexrj686avgpwvu', 'y1bbpmvitch2kkvk'], choices=['Jolteon', 'Draceon', 'Sylveon', 'Espeon'],
#             shuffle=True,
#             shuffle_skip=None,
#             correct=1,
#             id='6681294850532578')],
#             num_rounds=10,
#             question_index=-1,
#             round_winners=[],
#             winning_time=None,
#             complete_players=[],
#             current_round_times=[])
#   )

# def conversionTest():
#   data = getTestData()
#   json_converter = JsonConverter()
#   json_data = json_converter.baseModelToJson(data)
#   print(json_data)
#   reconverted = json_converter.jsonToBaseModel(json_data)
#   print(reconverted)

# def memStoreTest():
#   data = getTestData()
#   mem_store = GcloudMemoryStorage(client=datastore.Client(), kind='test1')
#   id = mem_store.create(data)

#   def func(game_room: GameRoom):
#     pass

#   mem_store.transaction(id, func)

# def queryTest():
#   mem_store = GcloudMemoryStorage(client=datastore.Client())
#   filters = [
#     ('categories', '=', '19g8pnv6jujxzli9')
#   ]
#   results = mem_store.query(kind='question', filters=filters, data_type=QuestionData)
#   print(results)

# def createEntity():
#   mem_store = GcloudMemoryStorage(client=datastore.Client())
#   id = mem_store.holdId(kind='test')
#   mem_store.addDataObject(kind='test', id=id, data={'data': 'This is a test'})
#   print(id)

def getMulti():
  mem_store = GcloudMemoryStorage(client=datastore.Client())
  data = mem_store.getMulti(kind='question', ids=['6681294850532578', 'ig8bqievgfoa3tp0'], data_type=QuestionData)
  print(data)

if __name__ == '__main__':
  getMulti()
