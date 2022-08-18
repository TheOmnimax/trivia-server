from typing import Optional
from pydantic import BaseModel

class Player(BaseModel):
  id: str
  name: str
  score: int = 0

class Game(BaseModel):
  players: dict[str, Player] # Key is player ID
  pass
class GameRoom(BaseModel):
  host_id: str
  members: dict[str, Player] # Key is player ID
  game: Optional[Game] # TODO: Add Generics so that "game" property can be of any type that inherits from "Game"