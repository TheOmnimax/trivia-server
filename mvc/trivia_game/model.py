import imp
from typing import Optional
from pydantic import BaseModel
from game.model import Game, Player
from trivia.model import QuestionData, CategoryData

class RoundData(BaseModel):
  winners: list[Player]
  time: int


class TriviaGame(Game):
  """The "winning_time" will start at None, and "complete_players" and "current_round_times" will start as empty lists. As players answer the question, the "winning_time" will be set as the lowest time for that round so far (it can only go from None to a number, or lower; it can't go higher).

  The "winning_time" will be sent to each player. If their current time increases past the "winning_time" value (e.g. the "winning_time" is 5000, but their current time is 6000), then they will be added to the list of "complete_players". Players will also be added to "complete_players" as they answer the question.

  Once length of "complete_players" matches length of "players", it means all players have either answered the question, or their time has gome passed the "winning_time", so the round is over. Once that happens, the winner for the round can be calculated.
  """
  categories: list[CategoryData]
  questions: list[QuestionData]
  num_rounds: int
  question_index: int = 0
  round_winners: list[RoundData] = []
  winning_time: Optional[int] # Lowest time so far. 
  complete_players: list[Player] = []
  current_round_times: dict[Player, int] = []

