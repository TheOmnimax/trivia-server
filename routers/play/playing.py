from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from domains.trivia_game.services.trivia_game import getQuestion, roundComplete
from domains.trivia_game.model import TriviaGame, TriviaPlayer
from domains.trivia_game.schemas import AdminResponse, AdminSchema, AnswerQuestion, AnswerResponse, GameCompleteResponse, PlayerCheckinResponse, PlayerCheckinSchema, ResultsResponse, RoomSchema, StillPlaying
from tools.randomization import genCode
from gcloud_utils.datastore import GcloudMemoryStorage
from domains.trivia_game import services as tg_services
from threading import Timer

import dependencies

router = APIRouter()

def _getGameId(room_code: str, mem_store: GcloudMemoryStorage) -> str:
  game_room = mem_store.get(kind='game_room', id=room_code)
  game_id = game_room.game_id
  return game_id

def _getGame(room_code: str, mem_store: GcloudMemoryStorage) -> tuple[str, TriviaGame]:
  game_id = _getGameId(room_code=room_code, mem_store=mem_store)
  game = mem_store.get(kind='trivia_game', id=game_id, data_type=TriviaGame)
  return (game_id, game)

def completionCheck(room_code: str, player_id: str, mem_store: GcloudMemoryStorage):
  game_id, game = _getGame(room_code=room_code, mem_store=mem_store)
  def nr():
    tg_services.nextRound(game_id=game_id, player_ids=players.keys(), transaction=mem_store.transaction)
  
  def completeRound(game: TriviaGame):
    game.round_complete = True
    tg_services.completeRound(
        game,
        player_data=players,
        # completionFunction=Timer(1.0, nr).start # Wait a couple of seconds before starting the next round
        )
  
  def predicate(game: TriviaGame): # True if ready to begin calculations for the next round. Using "round_complete" to make sure they do not happen multiple times
    # print('Predicate')
    # print('Round complete:', game.round_complete)
    # print('From function:', tg_services.roundComplete(player_data=players, winning_time=game.winning_time))
    return (not game.round_complete) and tg_services.roundComplete(player_data=players, winning_time=game.winning_time)
  players = mem_store.getMulti(
    kind='player',
    ids=game.players,
    data_type=TriviaPlayer
    )
  mem_store.transaction(kind='trivia_game', id=game_id, new_val_func=completeRound, predicate=predicate)

  current_question = tg_services.getQuestion(game)
  print('Compl statuses:')
  print([players[p].completed_round for p in players])
  print('Ready statuses:')
  print([players[p].ready for p in players])
  if game.round_complete:
    winners_ids = tg_services.getRoundResults(game).winners
    winner_names = [players[p].name for p in winners_ids]
    is_winner = player_id in winners_ids

    print('Ready statuses:')
    print([players[p].ready for p in players])

    if all([players[p].ready for p in players]):
      tg_services.nextRound(game_id=game_id, player_ids=players.keys(), transaction=mem_store.transaction)

    if game.game_complete: # TODO: Add delay before completing game
      return GameCompleteResponse(
        correct=tg_services.getCorrectValue(game),
        winners=winner_names,
        is_winner=is_winner,
      )
    else: # The round is complete, but not the game, so can display info about the round, including who won
      return StillPlaying(
        question=current_question.label,
        choices=current_question.choices,
        player_complete=True,
        round_complete=True,
        game_complete=False,
        correct=tg_services.getCorrectValue(game),
        winners=winner_names,
        is_winner=is_winner,
      )
  elif players[player_id].selected_choice > -1:
    return StillPlaying(
      question=current_question.label,
      choices=current_question.choices,
      player_complete=True,
      round_complete=False,
      game_complete=False
    )
  else:
    return StillPlaying(
      question=current_question.label,
      choices=current_question.choices,
      player_complete=False,
      round_complete=False,
      game_complete=False
    )

# ROUTERS

@router.post('/start-game')
async def startGame(data: AdminSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):

  game_room = mem_store.get(kind='game_room', id=data.room_code)

  if game_room.host_id != data.host_id:
    return AdminResponse(
      successful=False,
      message='Only the host can start the game.'
    )
  game_id = game_room.game_id
  
  def sg(game: TriviaGame):
    game_started = tg_services.startGame(game)
    if game_started: # TODO: Add this as a predicate instead
      return AdminResponse(
        successful=True,
        message='Game started!'
      )
    else:
      return AdminResponse(
        successful=False,
        message='The game has already started.'
      )
      
  return mem_store.transaction(kind='trivia_game', id=game_id, new_val_func=sg)

@router.post('/player-checkin')
async def playerCheckin(data: PlayerCheckinSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)) -> PlayerCheckinResponse:

  game_id, game = _getGame(room_code=data.room_code, mem_store=mem_store)
  

  if game.question_index == -1:
    return {'started': False}
  
  def pc(player: TriviaPlayer):
    if (player.selected_choice == -1) and (data.time > player.time_used):
      print(f'Setting time for {data.player_id} to {data.time}')
      player.time_used = data.time
    if (game.winning_time != None) and (player.time_used > game.winning_time):
      player.completed_round = True
    player.ready = data.ready
    # TODO: IMPORTANT: Update to go to next round only when every player is ready, then reset their "ready" values once each player checks in as "playing".
  player = mem_store.get(kind='player', id=data.player_id, data_type=TriviaPlayer)
  players = mem_store.getMulti(
    kind='player',
    ids=game.players,
    data_type=TriviaPlayer
    )

  # if not (player.completed_round or tg_services.roundComplete(player_data=players, winning_time=game.winning_time)): # Only add time if player is not done
  mem_store.transaction(id=data.player_id, kind='player', new_val_func=pc)

  return completionCheck(room_code=data.room_code, player_id=data.player_id, mem_store=mem_store)


@router.post('/answer-question')
async def answerQuestion(data: AnswerQuestion, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):

  game_id, game = _getGame(room_code=data.room_code, mem_store=mem_store)
  current_question = tg_services.getQuestion(game)
  correct_answer = current_question.correct

  def pCorrect(game: TriviaGame, player: TriviaPlayer):
    tg_services.makePlayerCorrect(game=game, player=player, selected_choice=data.answer, time=data.time)
    return AnswerResponse(player_correct=True)
    pass

  def pWrong(player: TriviaPlayer):
    tg_services.makePlayerWrong(player=player, selected_choice=data.answer)
    return AnswerResponse(player_correct=False)


  if data.answer == correct_answer:
    return mem_store.transactionMulti(
      pairs=[
        ('trivia_game', game_id),
        ('player', data.player_id)
        ],
      new_val_func=pCorrect
    )
  else:
    return mem_store.transaction(kind='player', id=data.player_id, new_val_func=pWrong)


@router.post('/get-results')
async def getResults(data: RoomSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):

  game_id, game = _getGame(room_code=data.room_code, mem_store=mem_store)
  player_data = mem_store.getMulti(kind='player', ids=game.players, data_type=TriviaPlayer)
  named_scores, winner_names = tg_services.getResultsWithNames(game=game, player_data=player_data)
  return ResultsResponse(
      scores=named_scores,
      winners=winner_names
  )
