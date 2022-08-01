from fastapi import APIRouter, Depends, HTTPException
from domains.trivia_game.services.trivia_game import getQuestion, roundComplete
from domains.trivia_game.model import TriviaGame
from domains.trivia_game.schemas import AdminSchema, AnswerQuestion, AnswerResponse, PlayerCheckinResponse, PlayerCheckinSchema, PlayerSchema, RoomSchema
from tools.randomization import genCode
from gcloud_utils.datastore import GcloudMemoryStorage
from domains.trivia_game import services as tg_services
from domains.game.model import Game, GameRoom
from domains.game import services as game_services

import dependencies

from pydantic import BaseModel
from daos.utils import getClient

router = APIRouter()

# class NoData(BaseModel):
#   pass

# # Creates a new game, sends back the room code
# @router.post('/create-room')
# async def createRoom(data: NoData):
#   room_code = genCode(6)
#   game_room = GameRoom(room_code)
#   room_storage.set(game_room)
#   return {
#     'room_code': room_code,
#     }

def _roundReturn(game: TriviaGame, player_id: str) -> PlayerCheckinResponse:
  current_question = tg_services.getQuestion(game)
  if tg_services.roundComplete(game):
    tg_services.completeRound(game)
    winners = tg_services.getRoundResults(game).winners
    winner_names = [p.name for p in winners]
    is_winner = player_id in [p.id for p in winners]
    return PlayerCheckinResponse(
      question=current_question.label,
      choices=current_question.choices,
      round_complete=True,
      correct=tg_services.getCorrectValue(game),
      winners=winner_names,
      is_winner=is_winner
    )
    # TODO: Add tg_services.nextQuestion(game)
  else:
    return PlayerCheckinResponse(
      question=current_question.label,
      choices=current_question.choices,
      round_complete=False
    )

@router.post('/start-game')
async def startGame(data: AdminSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):

  def sg(game_room: GameRoom):
    game = game_room.game
    host_id = game_room.host_id
    if host_id == data.host_id:
      if game.question_index > -1:
        return {
          'successful': False,
          'message': 'Only the host can start the game.'
        }
      else:
        tg_services.nextQuestion(game)
        return {
          'successful': True,
          'message': 'Game started.'
        }
    else:
      return {
        'successful': False,
        'message': 'Only the host can start the game.'
      }
  return mem_store.transaction(data.room_code, sg)

# @router.post('/get-question')
# async def getQuestion(data: RoomSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):
  
#   def gq(game_room: GameRoom):
#     game = game_room.game
#     current_question = tg_services.getQuestion(game)

#   return {
#     'question': 'Question from server',
#     'choices': [
#       'Choice 1',
#       'Choice 2',
#       'Choice 3',
#       'Choice 4'
#     ]
#   }



@router.post('/player-checkin')
async def playerCheckin(data: PlayerCheckinSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)) -> PlayerCheckinResponse:
  
  
  def pc(game_room: GameRoom):
    game = game_room.game
    if game.question_index == -1:
      return {'started': False}
    else:
      # current_question = tg_services.getQuestion(game)
      # return PlayerCheckinResponse(
      #   question=current_question.label,
      #   choices=current_question.choices
      # )
      tg_services.addRoundTime(game=game, player_id=data.player_id, time=data.time)
      return _roundReturn(game, player_id=data.player_id)
  return mem_store.transaction(data.room_code, pc)

@router.post('/answer-question')
async def answerQuestion(data: AnswerQuestion, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):

  # Handler steps:
  # 1. Input verification: Make sure the body has all of the correct data
  # 2. Data transformations and retrieval outside of transaction
  # 3. Transaction

  error = None

  def aq(game_room: GameRoom):
    game = game_room.game
    player_id = data.player_id
    if data.player_id in game.complete_players: # TODO: QUESTION: Is there a good way to make "game" of type "TriviaGame" so the hints work better?
      error = 1
      raise HTTPException(status_code=428, detail='Player already answered question.')
    else:
      current_question = tg_services.getQuestion(game)
      correct_answer = current_question.correct
      if data.answer == correct_answer:
        tg_services.makePlayerCorrect(game, player_id, data.time)
        return AnswerResponse(player_correct=True)
      else:
        tg_services.playerWrong(game, player_id)
        return AnswerResponse(player_correct=False)
  return mem_store.transaction(id=data.room_code, new_val_func=aq)
  


@router.post('/next-round')
async def nextRound(data: AdminSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):
  def nr(game_room: GameRoom):
    host_id = game_room.host_id
    if game_room.host_id == data.host_id:
      game = game_room.game
      if tg_services.roundComplete(game):
        tg_services.nextQuestion(game)
        
      else:
        raise HTTPException(status_code=425, detail='Not yet ready to go to next round.')
    else:
      raise HTTPException(status_code=403, detail='Only the host can go to the next round.')
  pass