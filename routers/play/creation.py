from domains.general.schemas import ConnectionSchema
from domains.trivia_game.model import TriviaGame
from domains.trivia_game.schemas import CreateGame, CreateRoomResponse, JoinGameResponse, JoinGameSchema, CreateRoomSchema
from domains.trivia_game import services as tg_services
from domains.game.model import GameRoom
from domains.game import services as game_services
import dependencies
from dependencies.sio import sio
from typing import List

from gcloud_utils.datastore import EntityNotExists

@sio.on('connect')
async def connect(sid, data):
  await sio.emit('connect', dict(ConnectionSchema(sid=sid)))

@sio.on('create-room')
async def createRoom(sid, data):
  data = CreateRoomSchema(**data)
  mem_store = dependencies.getMemoryStorage()
  host_player = tg_services.createTriviaPlayer(name=data.host_name, sid=sid)
  host_id = mem_store.create(kind='trivia_player', data=host_player)
  game_room = game_services.createGameRoom(host_id=host_id)
  room_code = mem_store.create(kind='game_room', data=game_room)
  await sio.emit('create-room', data=dict(CreateRoomResponse(
    room_code=room_code,
    host_id=host_id
  )))

@sio.on('new-game')
async def newGame(sid, data):
  data = CreateGame(**data)
  # PREPARATION
  room_code = data.room_code
  mem_store = dependencies.getMemoryStorage()
  deps = dependencies.allRetrieval()
  mem_store = deps.memory_storage
  question_dao = deps.question_dao
  category_dao = deps.category_dao
  categories = category_dao.getCatsFromIds(ids=data.categories)

  # CREATE NEW GAME
  new_game = tg_services.newGame( # Create the new game
    categories=categories,
    question_dao=question_dao,
    num_rounds=data.num_rounds
    )
  game_id = mem_store.create('trivia_game', new_game) # Add the new game to the server

  # ADD TO GAME ROOM
  def addGameToGameRoom(game_room: GameRoom) -> List[str]:
    game_services.addGame(game_room=game_room, game_id=game_id)
    return game_room.members
  
  room_members = mem_store.transaction(
    id=room_code,
    kind='game_room',
    new_val_func=addGameToGameRoom
    )
  
  # ADD ROOM MEMBERS TO GAME

  def addPlayers(game: TriviaGame):
    for p in room_members:
      tg_services.addPlayer(game, p)
  
  mem_store.transaction(
    id=game_id,
    kind='trivia_game',
    new_val_func=addPlayers
    )
  await sio.emit('new-game', data={'successful': True})


@sio.on('add-player')
async def addPlayer(sid, data):
  data = JoinGameSchema(**data)
  mem_store = dependencies.getMemoryStorage()
  new_player = tg_services.createTriviaPlayer(name=data.player_name, sid=sid)
  player_id = mem_store.create(kind='trivia_player', data=new_player)

  def addMember(game_room: GameRoom):
    game_room.members.append(player_id)
    return game_room.game_id
  
  def addPlayer(game: TriviaGame):
    tg_services.addPlayer(game, player_id)
    return True

  try:
    game_id = mem_store.transaction(kind='game_room', id=data.room_code, new_val_func=addMember)
  except EntityNotExists:
    response = JoinGameResponse(successful=False, message='Game does not exist', player_id='')
    await sio.emit('add-player', data=dict(response))
    return
  successful = mem_store.transaction(kind='trivia_game', id=game_id, new_val_func=addPlayer)

  response = JoinGameResponse(player_id=player_id)
  await sio.emit('add-player', data=dict(response))

