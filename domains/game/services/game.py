from domains.game.model import Game, Player, GameRoom
from domains.game.services import player as player_services
from tools.randomization import genUniqueCode
def createGameRoom(host_player: Player):
  return GameRoom(
    host_id=host_player.id,
    members={host_player.id: host_player}
  )


def addGame(game_room: GameRoom, game: Game):
  game.players = game_room.members
  game_room.game = game

def createMember(game_room: GameRoom, name: str) -> str:
  existing_codes = [id for id in game_room.members]
  id = genUniqueCode(6, existing_codes)
  while id in game_room.members:
    id = genUniqueCode(6, existing_codes)
  game_room.members[id] = Player(id=id, name=name)
  return id

def addMemberToGame(game_room: GameRoom, player_id: str) -> bool:
  if player_id in game_room.members:
    game_room.game.players[player_id] = game_room.members[player_id]
    return True
  else:
    return False

def removePlayer(game_room: GameRoom, player: Player):
  game_room.members.pop(player.id)

def resetScores(game_room: GameRoom, base_score: int = 0):
  for player_id in game_room.members:
    player = game_room.members[player_id]
    player.score = base_score