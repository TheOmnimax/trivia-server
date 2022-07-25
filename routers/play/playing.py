from fastapi import APIRouter, Depends
from game_old.room import Game, GameRoom
from game_old.memory_storage import room_storage
from tools.randomization import genCode

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

class RoomData(BaseModel):
  room_code: str

@router.post('/get-question')
async def getQuestion(data: RoomData, client = Depends(getClient)):
  
  def gq(game_room: GameRoom):
    pass

  return {
    'question': 'Question from server',
    'choices': [
      'Choice 1',
      'Choice 2',
      'Choice 3',
      'Choice 4'
    ]
  }
