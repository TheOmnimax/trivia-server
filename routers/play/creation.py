from fastapi import APIRouter, Depends

from daos.utils import getClient # TODO: QUESTION: Should this be in the main file, or in daos.utils?
from gcloud_utils.datastore import GcloudMemoryStorage
from domains.trivia_game.schemas import CreateGame, CreateRoomResponse, JoinGameResponse, JoinGameSchema, NewGameSchema, CreateRoomSchema
from domains.trivia_game import services as tg_services
from domains.game.model import Game, GameRoom
from domains.game import services as game_services
import dependencies

router = APIRouter()

@router.post('/create-room')
async def createRoom(data: CreateRoomSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)): # Create a room with a single player, the host
  # mem_store = ar.memory_storage
  host_player = game_services.createPlayer(name=data.host_name)
  game_room = game_services.createGameRoom(host_player=host_player)

  room_code = mem_store.create(game_room)
  return CreateRoomResponse(
    room_code=room_code,
    host_id=host_player.id
  )

@router.post('/new-game')
async def newGame(data: CreateGame, ar: dependencies.AllRetrieval = Depends(dependencies.allRetrieval)):
  room_code = data.room_code

  mem_store = ar.memory_storage
  question_dao = ar.question_dao
  category_dao = ar.category_dao
  categories = category_dao.getCatsFromIds(ids=data.categories)
  def cg(game_room: GameRoom):
    # game_code = mem_store.create()
    new_game = tg_services.newGame(
      categories=categories,
      question_dao=question_dao
      ) # TODO: QUESTION: Should I feed in the entire CreateGame schema, or break it up, then feed that in? I feel like the latter, in case the function will be used for other things
    
    game_services.addGame(game_room=game_room, game=new_game)
    return NewGameSchema(
      successful=True
    )
  
  response = mem_store.transaction(id=room_code, new_val_func=cg)
  return response

@router.post('/add-player')
async def addPlayer(data: JoinGameSchema, mem_store: GcloudMemoryStorage = Depends(dependencies.getMemoryStorage)):
  room_code = data.room_code
  new_player = game_services.createPlayer(name=data.player_name)
  def ap(game_room: GameRoom):
    player_id = tg_services.addPlayer(new_player) # TODO: Update with game
    return JoinGameResponse(player_id=player_id)
  response = mem_store.transaction(id=room_code, new_val_func=ap)
  return response

