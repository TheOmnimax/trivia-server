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
  game_room = mem_store.get(kind='game_room', id=room_code, data_type=GameRoom)
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
        round_num=game.question_index,
        question=question.label,
        choices=question.choices
        )),
      to=sid
      )

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

  if data.round != game.question_index: # Answer for a different round. Probably answered at same time as winner of last round, but game has since moved on
    return

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

  def completeRound(game: TriviaGame) -> Tuple[TriviaGame, str]:
    round_winner = game.round_winner
    trivia_game.completeRound(game=game)
    return (game, round_winner)

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
    game, round_winner = mem_store.transaction(kind='trivia_game', id=game_id, new_val_func=completeRound)
    player_data = _getPlayerDict(player_ids=game.players, mem_store=mem_store)

    if round_winner != None:
      winner_name = player_data[round_winner].name
    else:
      winner_name = ''


    for player_id in player_data:
      player = player_data[player_id]
      sid = player.socket
      await sio.emit('round-complete',
        dict(RoundComplete(
          round_complete=True,
          is_winner=player_id==round_winner,
          winner_name=winner_name,
          correct=correct_answer
        )),
        to=sid
        )
    
    game_id, game = _getGame(data.room_code, mem_store)
    if game.game_complete:
      named_scores, winner_names = tg_services.getResultsWithNames(game=game, player_data=player_data)
      sids = _getSocketIds(player_data=player_data)
      await sleep(1)
      for sid in sids:
        await sio.emit('game-complete',
        dict(ResultsResponse(
          scores=named_scores,
          winners=winner_names
        )),
        to=sid)
    else:
      game = tg_services.nextRound(game_id=game_id, player_ids=player_data, transaction=mem_store.transaction)
      
      print('Sleeping')
      await sleep(1)
      print('Done sleeping')
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
