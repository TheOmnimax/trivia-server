from fastapi import APIRouter, Depends, HTTPException

from daos.utils import getClient
from dependencies import websocket
from dependencies.model import WebSocketHelpers
from domains.trivia_game.model import TriviaGame, TriviaPlayer # TODO: QUESTION: Should this be in the main file, or in daos.utils?
from gcloud_utils.datastore import GcloudMemoryStorage
from domains.trivia_game.schemas import CreateGame, CreateRoomResponse, JoinGameResponse, JoinGameSchema, NewGameSchema, CreateRoomSchema
from domains.trivia_game import services as tg_services
from domains.game.model import Game, GameRoom
from domains.game import services as game_services
import dependencies
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi import WebSocket, WebSocketDisconnect


async def webSocketCommands(id: str, websocket: WebSocket, manager: websocket.ConnectionManager):
  try:
    while True:
      data = await websocket.receive_json()
      if ''
  except WebSocketDisconnect:
    manager.disconnect(id)
  pass



router = APIRouter()

@router.websocket('/create-room')
async def webSocketPlay(websocket: WebSocket, web_socket_helpers: WebSocketHelpers = Depends(dependencies.getWebSocketHelpers)):
  connection_manager = web_socket_helpers.connection_manager
  mem_store = web_socket_helpers.memory_storage
  await websocket.accept()
  while True:
    data = await websocket.receive_json()
    if 'name' in data:
      host_player = tg_services.createTriviaPlayer(name=data['name'])
      host_id = mem_store.create(kind='player', data=host_player)
      connection_manager.addWebSocket(host_id, websocket)
      game_room = game_services.createGameRoom(host_id=host_id)
      room_code = mem_store.create(kind='game_room', data=game_room)
      connection_manager.sendData(host_id,
        CreateRoomResponse(
          room_code=room_code,
          host_id=host_id
        )
      )
      break
  
  pass

@router.websocket('/join-game')
async def webSocketPlay(websocket: WebSocket, web_socket_helpers: WebSocketHelpers = Depends(dependencies.getWebSocketHelpers)):
  pass

@router.websocket('/create-room')
async def createRoom(data: CreateRoomSchema, web_socket_helpers: WebSocketHelpers = Depends(dependencies.getWebSocketHelpers)):
  connection_manager = web_socket_helpers.connection_manager
  mem_store = web_socket_helpers.memory_storage
  host_player = tg_services.createTriviaPlayer(name=data.host_name)
  host_id = mem_store.create(kind='player', data=host_player)
  connection_manager.connect(host_id)

  game_room = game_services.createGameRoom(host_id=host_id)
  room_code = mem_store.create(kind='game_room', data=game_room)

@router.post('/create-room')
async def createRoom(data: CreateRoomSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)): # Create a room with a single player, the host
  # mem_store = ar.memory_storage

  host_player = tg_services.createTriviaPlayer(name=data.host_name)
  host_id = mem_store.create(kind='player', data=host_player)
  game_room = game_services.createGameRoom(host_id=host_id)
  room_code = mem_store.create(kind='game_room', data=game_room)
  return  CreateRoomResponse(
    room_code=room_code,
    host_id=host_id
  )

@router.post('/new-game')
async def newGame(data: CreateGame, ar: dependencies.AllRetrieval = Depends(dependencies.allRetrieval)):
  # PREPARATION
  room_code = data.room_code
  mem_store = ar.memory_storage
  question_dao = ar.question_dao
  category_dao = ar.category_dao
  categories = category_dao.getCatsFromIds(ids=data.categories)

  # CREATE NEW GAME
  new_game = tg_services.newGame( # Create the new game
    categories=categories,
    question_dao=question_dao,
    num_rounds=5 # TODO: Update this to be customizable
    )
  game_id = mem_store.create('trivia_game', new_game) # Add the new game to the server

  # ADD TO GAME ROOM
  def addGameToGameRoom(game_room: GameRoom) -> list[str]:
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

  return {'successful': True}

@router.post('/add-player')
async def addPlayer(data: JoinGameSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):
  new_player = tg_services.createTriviaPlayer(name=data.player_name)
  player_id = mem_store.create(kind='player', data=new_player)

  def addMember(game_room: GameRoom):
    game_room.members.append(player_id)
    return game_room.game_id
  
  def addPlayer(game: TriviaGame):
    tg_services.addPlayer(game, player_id)
    return True

  game_id = mem_store.transaction(kind='game_room', id=data.room_code, new_val_func=addMember)
  successful = mem_store.transaction(kind='trivia_game', id=game_id, new_val_func=addPlayer)
  if game_id == None:
    raise HTTPException(status_code=404, detail='Room code not found')
  return JoinGameResponse(player_id=player_id)

