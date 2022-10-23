from typing import Dict, List, Tuple
from domains.game.model import GameRoom
from domains.trivia_game.services import trivia_game
from domains.trivia_game.services.trivia_game import getPlayerNames
from domains.trivia_game.model import TriviaGame, TriviaPlayer
from domains.trivia_game.schemas import AdminSchema, AnswerQuestion, AnswerResponse, GameResponse,  NextRoundSchema, PlayerSchema, ResultsResponse, RoomSchema, RoundComplete, StartGame
from gcloud_utils.datastore import GcloudMemoryStorage
from domains.trivia_game import services as tg_services
from asyncio import sleep

import dependencies

from dependencies.sio import sio

# async def _sendSidsMulti(game: Game, mem_store: GcloudMemoryStorage, event: str, data):
#   sids = _getSids(game, mem_store)
#   return await socket_manager.sendDataMulti(ids=sids, event=event, data=data)

def _getGameId(room_code: str, mem_store: GcloudMemoryStorage) -> str:
  game_room = mem_store.get(kind='game_room', id=room_code)
  game_id = game_room.game_id
  return game_id

def _getGame(room_code: str, mem_store: GcloudMemoryStorage) -> Tuple[str, TriviaGame]:
  game_id = _getGameId(room_code=room_code, mem_store=mem_store)
  game = mem_store.get(kind='trivia_game', id=game_id, data_type=TriviaGame)
  return (game_id, game)

def _getPlayerDict(player_ids: List[str], mem_store: GcloudMemoryStorage) -> Dict[str, TriviaPlayer]:
  return mem_store.getMulti(kind='player', ids=player_ids, data_type=TriviaPlayer)

def _getPlayerDictFromRoomCode(room_code: str, mem_store: GcloudMemoryStorage) -> Dict[str, TriviaPlayer]:
  game_id, game = _getGame(room_code=room_code, mem_store=mem_store)
  player_ids = game.players
  player_data = _getPlayerDict(player_ids=player_ids, mem_store=mem_store)
  return player_data

def _getSocketIds(player_data: Dict[str, TriviaPlayer]) -> List[str]:
  socket_ids = [player_data[p].socket for p in player_data]
  return socket_ids

async def _nextRound(game: TriviaGame, player_data: Dict[str, TriviaPlayer]):
  question = game.questions[game.question_index]
  for player_id in player_data:
    player = player_data[player_id]
    sid = player.socket
    await sio.emit('next-round',
      dict(NextRoundSchema(
        question=question.label,
        choices=question.choices
        )),
      to=sid
      )


# def completionCheck(room_code: str, player_id: str, mem_store: GcloudMemoryStorage):
#   game_id, game = _getGame(room_code=room_code, mem_store=mem_store)
#   def nr():
#     tg_services.nextRound(game_id=game_id, player_ids=players.keys(), transaction=mem_store.transaction)
  
#   def completeRound(game: TriviaGame):
#     game.round_complete = True
#     tg_services.completeRound(
#         game,
#         player_data=players,
#         # completionFunction=Timer(1.0, nr).start # Wait a couple of seconds before starting the next round
#         )
  
#   def predicate(game: TriviaGame): # True if ready to begin calculations for the next round. Using "round_complete" to make sure they do not happen multiple times
#     return (not game.round_complete) and tg_services.roundComplete(player_data=players, winning_time=game.winning_time)
#   players = mem_store.getMulti(
#     kind='player',
#     ids=game.players,
#     data_type=TriviaPlayer
#     )
#   mem_store.transaction(kind='trivia_game', id=game_id, new_val_func=completeRound, predicate=predicate)

#   player_names = getPlayerNames(player_ids=game.players, player_data=players)
#   named_scores = tg_services.getNamedScores(scores=game.scores, player_data=players)
#   current_question = tg_services.getQuestion(game)
#   if game.round_complete:
#     winners_ids = tg_services.getRoundResults(game).winners
#     winner_names = [players[p].name for p in winners_ids]
#     is_winner = player_id in winners_ids

#     if all([players[p].ready for p in players]):
#       tg_services.nextRound(game_id=game_id, player_ids=players.keys(), transaction=mem_store.transaction)
    
#     if game.game_complete: # TODO: Add delay before completing game
#       return PlayerCheckinResponse(
#         player_names=player_names,
#         scores=named_scores,
#         question=current_question.label,
#         choices=current_question.choices,
#         correct=tg_services.getCorrectValue(game),
#         player_complete=True,
#         round_complete=True,
#         game_complete=True,
#         winners=winner_names,
#         is_winner=is_winner,
#       )
#     else: # The round is complete, but not the game, so can display info about the round, including who won
#       return PlayerCheckinResponse(
#         player_names=player_names,
#         scores=named_scores,
#         question=current_question.label,
#         choices=current_question.choices,
#         player_complete=True,
#         round_complete=True,
#         correct=tg_services.getCorrectValue(game),
#         winners=winner_names,
#         is_winner=is_winner,
#       )
#   elif players[player_id].selected_choice > -1: # Player has already selected a choice
#     return PlayerCheckinResponse(
#       player_names=player_names,
#       scores=named_scores,
#       question=current_question.label,
#       choices=current_question.choices,
#       player_complete=True,
#     )
#   else: # Active round
#     return PlayerCheckinResponse(
#       player_names=player_names,
#       scores=named_scores,
#       question=current_question.label,
#       choices=current_question.choices,
#     )

# ROUTERS

@sio.on('pregame-status')
async def pregameStatus(sid, data):
  print('Event: Pregame')
  data = PlayerSchema(**data)
  mem_store = dependencies.getMemoryStorage()
  player_data = _getPlayerDictFromRoomCode(room_code=data.room_code, mem_store=mem_store)
  socket_ids = _getSocketIds(player_data=player_data)
  player_names = [player_data[p].name for p in player_data]
  for sid in socket_ids:
    await sio.emit('game-status', dict(GameResponse(player_names=player_names)), to=sid)


@sio.on('start-game')
async def startGame(sid, data):
  print('Event: Start game')
  data = AdminSchema(**data)
  mem_store = dependencies.getMemoryStorage()
  game_room = mem_store.get(kind='game_room', id=data.room_code, data_type=GameRoom)
  game_id = game_room.game_id

  def sg(game: TriviaGame):
    if game.question_index == -1:
      game.question_index = 0
      return True
    else:
      return False

  if game_room.host_id == data.host_id:
    started = mem_store.transaction(kind='trivia_game', id=game_id, new_val_func=sg)
    if started:
      response = StartGame(
        allowed=True,
        started=True
      )
    else:
      response = StartGame(
        allowed=True,
        started=False
      )
  else:
    started = False
    response = StartGame(
      allowed=False,
      started=False
    )
  
  await sio.emit('start-game', dict(response))

  if started:
    game_id, game = _getGame(data.room_code, mem_store)
    player_data = _getPlayerDict(game.players, mem_store)
    await _nextRound(game, player_data)


@sio.on('answer-question')
async def answerQuestion(sid, data):
  print('Event: Answer question')
  data = AnswerQuestion(**data)
  mem_store = dependencies.getMemoryStorage()
  game_id, game = _getGame(room_code=data.room_code, mem_store=mem_store)
  current_question = tg_services.getQuestion(game)
  correct_answer = current_question.correct

  def pCorrect(game: TriviaGame, player: TriviaPlayer) -> bool:
    tg_services.makePlayerCorrect(game=game,
      player=player,
      player_id=data.player_id,
      selected_choice=data.answer)
    
    return game.round_complete


  def pWrong(game: TriviaGame, player: TriviaPlayer) -> bool:
    tg_services.makePlayerWrong(game=game, player=player,
      selected_choice=data.answer,
      player_id=data.player_id,
      )
    return game.round_complete

  def completeRound(game: TriviaGame) -> TriviaGame:
    trivia_game.completeRound(game=game)
    return game
  
  def resetPlayer(player: TriviaPlayer) -> TriviaPlayer:
    trivia_game.resetPlayer(player)
    return player

  if data.answer == correct_answer:
    answer_func = pCorrect
    await sio.emit('answer-question', dict(AnswerResponse(player_correct=True)))
  else:
    answer_func = pWrong
    await sio.emit('answer-question', dict(AnswerResponse(player_correct=False)))
    pass
  round_complete = mem_store.transactionMultiKind(
    pairs=[
      ('trivia_game', game_id),
      ('player', data.player_id)
      ],
    new_val_func=answer_func
  )
  
  if round_complete:
    # TODO: Find why question data does not become QuestionData
    game = mem_store.transaction(kind='trivia_game', id=game_id, new_val_func=completeRound)
    player_data = _getPlayerDict(player_ids=game.players, mem_store=mem_store)

    round_winner = game.round_winner
    if round_winner != None:
      winner_name = player_data[round_winner].name
    else:
      winner_name = ''


    for player_id in player_data:
      player = player_data[player_id]
      sid = player.socket
      print('Emitting round complete')
      await sio.emit('round-complete',
        dict(RoundComplete(
          round_complete=True,
          is_winner=player_id==game.round_winner,
          winner_name=winner_name,
          correct=correct_answer
        )),
        to=sid
        )
      print('Emitted to', sid)
    
    print('Sleeping')
    await sleep(1)
    print('Done sleeping')
    print(game.game_complete)
    if game.game_complete:
      named_scores, winner_names = tg_services.getResultsWithNames(game=game, player_data=player_data)
      sids = _getSocketIds(player_data=player_data)
      for sid in sids:
        await sio.emit('game-complete',
        dict(ResultsResponse(
          scores=named_scores,
          winners=winner_names
        )),
        to=sid)
    else:
      game = tg_services.nextRound(game_id=game_id, player_ids=player_data, transaction=mem_store.transaction)
      await _nextRound(game, player_data)

@sio.on('get-results')
async def getResults(sid, data):
  print('Event: Get results')
  data = RoomSchema(**data)
  mem_store = dependencies.getMemoryStorage()
  
  game_id, game = _getGame(room_code=data.room_code, mem_store=mem_store)
  player_data = mem_store.getMulti(kind='player', ids=game.players, data_type=TriviaPlayer)
  named_scores, winner_names = tg_services.getResultsWithNames(game=game, player_data=player_data)
  await sio.emit('get-results',
    dict(ResultsResponse(
      scores=named_scores,
      winners=winner_names
    ))
  )
