from typing import Optional
from pydantic import BaseModel

class Player(BaseModel):
  id: str
  name: str
  score: int = 0

class Game(BaseModel):
  id: str
  players: list[Player]
