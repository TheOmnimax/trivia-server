from game.model import Game, Player


def addPlayer(game: Game, player: Player):
  game.players.append(player)

def removePlayer(game: Game, player: Player):
  game.players.remove(player)
