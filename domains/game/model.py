from typing import List, Optional
from pydantic import BaseModel

class Player(BaseModel):
  name: str
  score: int = 0
  socket: str

class Game(BaseModel):
  players: List[str] = []

class GameRoom(BaseModel):
  host_id: str
  members: List[str]
  game_id: Optional[str]