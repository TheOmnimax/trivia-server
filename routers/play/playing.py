from fastapi import APIRouter, Depends, HTTPException
from domains.trivia_game.services.trivia_game import getQuestion, roundComplete
from domains.trivia_game.model import TriviaGame
from domains.trivia_game.schemas import AdminSchema, AnswerQuestion, AnswerResponse, GameCompleteResponse, PlayerCheckinResponse, PlayerCheckinSchema, PlayerSchema, ResultsResponse, RoomSchema, StillPlaying
from tools.randomization import genCode
from gcloud_utils.datastore import GcloudMemoryStorage
from domains.trivia_game import services as tg_services
from domains.game.model import Game, GameRoom
from domains.game import services as game_services
from threading import Timer

import dependencies

from pydantic import BaseModel
from daos.utils import getClient

router = APIRouter()

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
      tg_services.addRoundTime(game=game, player_id=data.player_id, time=data.time)

      current_question = tg_services.getQuestion(game)
      if tg_services.roundComplete(game):
        # If the round is complete, this creates a function for going to the next question, puts that into a transaction so it is properly saved to the server, puts that into a Timer so there is a delay, and then puts that into the completeRound() function, so it runs after calculating the winner of the round
        def nq(game_room: GameRoom):
          tg_services.nextQuestion(game_room.game)
        tg_services.completeRound(
          game,
          Timer(1.0, mem_store.transaction, (data.room_code, nq)).start # Wait a couple of seconds before starting the next round
          )
        winners = tg_services.getRoundResults(game).winners
        winner_data = [game.players[p] for p in winners]
        winner_names = [p.name for p in winner_data]
        is_winner = data.player_id in [p.id for p in winner_data]

        if game.game_complete:
          return GameCompleteResponse(
            correct=tg_services.getCorrectValue(game),
            winners=winner_names,
            is_winner=is_winner,
          )
        else:
          return StillPlaying(
            question=current_question.label,
            choices=current_question.choices,
            round_complete=True,
            correct=tg_services.getCorrectValue(game),
            winners=winner_names,
            is_winner=is_winner,
          )
          # TODO: Add tg_services.nextQuestion(game)
      else:
        return StillPlaying(
          question=current_question.label,
          choices=current_question.choices,
          round_complete=False
        )
    # End pc
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
    if game_room.host_id == data.host_id:
      game = game_room.game
      if tg_services.roundComplete(game):
        tg_services.nextQuestion(game)
        
      else:
        raise HTTPException(status_code=425, detail='Not yet ready to go to next round.')
    else:
      raise HTTPException(status_code=403, detail='Only the host can go to the next round.')
  return mem_store.transaction(data.room_code, nr)

@router.post('/get-results')
async def getResults(data: RoomSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):
  def gr(game_room: GameRoom):
    game = game_room.game
    scores = game.final_scores
    named_scores = dict()
    for player_id in scores:
      score = scores[player_id]
      player = game.players[player_id].name
      named_scores[player] = score
    return ResultsResponse(
      scores=named_scores,
      winners=tg_services.getWinnerNames(game)
    )
  return mem_store.transaction(data.room_code, gr)
