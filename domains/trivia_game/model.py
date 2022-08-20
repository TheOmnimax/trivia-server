from typing import Optional, Dict, List
from pydantic import BaseModel
from domains.game.model import Game, Player
from domains.trivia.model import QuestionData, CategoryData

class RoundData(BaseModel):
  winners: list[str]
  time: Optional[int]


# NEW?
# class RoundData(BaseModel):
#   complete: list[str]
#   winners: list[Player]
#   winner_ids: list[str]
#   question: QuestionData
#   correct: int
#   round_times: dict[str, int]

class TriviaPlayer(Player):
  completed_round: bool = False
  time_used: int = 0
  selected_choice: int = -1


class TriviaGame(Game):
  """The "winning_time" will start at None, and "complete_players" and "current_round_times" will start as empty lists. As players answer the question, the "winning_time" will be set as the lowest time for that round so far (it can only go from None to a number, or lower; it can't go higher).

  The "winning_time" will be sent to each player. If their current time increases past the "winning_time" value (e.g. the "winning_time" is 5000, but their current time is 6000), then they will be added to the list of "complete_players". Players will also be added to "complete_players" as they answer the question.

  Once length of "complete_players" matches length of "players", it means all players have either answered the question, or their time has gome passed the "winning_time", so the round is over. Once that happens, the winner for the round can be calculated.
  """
  categories: List[CategoryData]
  questions: List[QuestionData]
  num_rounds: int
  question_index: int = -1 # Starts at -1 because game has not yet started
  game_complete: bool = False
  round_complete: bool = False
  round_winners: List[RoundData] = []
  winning_time: Optional[int] # Lowest time so far. 
  # TODO: QUESTION: To save on processing, should I add a property for the current round data (e.g. The IDs of the round winners, the current correct answer, etc)?
  final_scores: Optional[Dict[str, int]]
  game_winners: Optional[List[str]] # Will Have a value once the game is complete

