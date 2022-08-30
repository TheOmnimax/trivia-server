from typing import List, Optional
from pydantic import BaseModel

class Player(BaseModel):
  name: str
  score: int = 0

class Game(BaseModel):
  players: List[str] = []

class GameRoom(BaseModel):
  host_id: str
  members: list[str]
  game_id: Optional[str]