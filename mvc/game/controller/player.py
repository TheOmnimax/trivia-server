from model import Player

def addScore(player: Player, score_change: int):
  player.score += score_change

def changeName(player: Player, new_name: str):
  player.name = new_name