from typing import Optional
from pydantic import BaseModel

class Player(BaseModel):
  name: str
  score: int = 0

class Game(BaseModel):
  players: list[str]

class GameRoom(BaseModel):
  host_id: str
  members: list[str]
  game_id: Optional[str]