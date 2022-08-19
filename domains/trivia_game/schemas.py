from pydantic import BaseModel
from typing import Optional
from domains.trivia_game.model import CategoryData
from domains.trivia_game.model import RoundData

class CategorySchema(CategoryData):
  pass

class RoomSchema(BaseModel):
  room_code: str

class PlayerSchema(RoomSchema):
  player_id: str

class AdminSchema(RoomSchema): # For doing admin work by the host like going to the next round
  host_id: str

class CreateRoomSchema(BaseModel):
  host_name: str = 'Host'

class CreateRoomResponse(BaseModel):
  room_code: str
  host_id: str
  pass

class CreateGame(BaseModel):
  room_code: str
  host_id: str
  categories: list[str]
  num_rounds: int = 10

class NewGameSchema(BaseModel):
  successful: bool

class NewGameResponse(BaseModel):
  pass

class JoinGameSchema(BaseModel):
  room_code: str
  player_name: str

class JoinGameResponse(BaseModel):
  player_id: str

class AdminResponse(BaseModel):
  successful: bool
  message: str

class GetQuestionSchema(RoomSchema):
  room_code: str

class PlayerCheckinSchema(PlayerSchema):
  time: int

class AnswerQuestion(PlayerCheckinSchema):
  answer: int # index of the question selected

class AnswerResponse(BaseModel):
  player_correct: bool
  
class PlayerCheckinResponse(BaseModel):
  correct: Optional[int]
  winners: Optional[list[str]]
  is_winner: Optional[bool]
  player_complete: bool = False
  game_complete: bool = False

class StillPlaying(PlayerCheckinResponse):
  question: str
  choices: list[str]
  player_complete: bool
  round_complete: bool
  pass

class GameCompleteResponse(PlayerCheckinResponse):
  game_complete: bool = True

class ResultsResponse(BaseModel):
  scores: dict[str, int]
  winners: list[str]