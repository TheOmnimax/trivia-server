from pydantic import BaseModel
from typing import Dict, List, Optional
from domains.trivia_game.model import CategoryData

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
  categories: List[str]
  num_rounds: int = 10

class NewGameSchema(BaseModel):
  successful: bool

class NewGameResponse(BaseModel):
  pass

class JoinGameSchema(BaseModel):
  room_code: str
  player_name: str

class JoinGameResponse(BaseModel):
  successful: bool = True
  message: str = "Successful"
  player_id: str

class GameResponse(BaseModel):
  player_names: List[str]

class StartGame(BaseModel):
  allowed: bool
  started: bool

class AdminResponse(BaseModel):
  successful: bool
  message: str

class GetQuestionSchema(RoomSchema):
  room_code: str

class AnswerQuestion(PlayerSchema):
  answer: int # index of the question selected
  round: int # Round number question is being answered for # IMPLEMENT

class AnswerResponse(BaseModel):
  player_correct: bool


class RoundComplete(BaseModel):
  round_complete: bool
  is_winner: bool
  winner_name: str
  correct: int
  

class PlayerCheckinResponse(BaseModel):
  player_names: List[str]
  scores: Dict[str, int]
  question: str
  choices: List[str]
  correct: Optional[int]
  player_complete: bool = False
  round_complete: bool = False
  game_complete: bool = False
  winners: Optional[List[str]]
  is_winner: Optional[bool]

class NextRoundSchema(BaseModel):
  round_num: int # Which round it is on
  question: str
  choices: List[str]

class ResultsResponse(BaseModel):
  scores: Dict[str, int]
  winners: List[str]