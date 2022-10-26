from domains.game.model import Player
from tools.randomization import genUniqueCode
from typing import List

def createPlayer(name: str, base_score: int = 0, code_length: int = 6, existing_ids: List[str] = []) -> Player:
  code = genUniqueCode(code_length, existing=existing_ids)
  return Player(
    id=code,
    name=name,
    score=base_score
  )

def addScore(player: Player, score_change: int):
  player.score += score_change

def changeName(player: Player, new_name: str):
  player.name = new_name

def resetScore(player: Player, new_score: int = 0):
  player.score = new_score