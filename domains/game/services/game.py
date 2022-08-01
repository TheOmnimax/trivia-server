from domains.game.model import Game, Player, GameRoom
from domains.game.services import player as player_services
def createGameRoom(host_player: Player):
  return GameRoom(
    host_id=host_player.id,
    members={host_player.id: host_player}
  )


def addGame(game_room: GameRoom, game: Game):
  game.players = game_room.members
  game_room.game = game

def addPlayer(game_room: GameRoom, player: Player):
  game_room.members[player.id] = player # TODO: Will need to make sure that since game.players is from game_room.members, that when one is updated, the other is updated as well. If not, will have to update each one each time

def removePlayer(game_room: GameRoom, player: Player):
  game_room.members.pop(player.id)

def resetScores(game_room: GameRoom, base_score: int = 0):
  for player_id in game_room.members:
    player = game_room.members[player_id]
    player.score = base_score