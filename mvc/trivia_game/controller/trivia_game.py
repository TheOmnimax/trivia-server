from model import TriviaGame, RoundData
from game.model import Player
from trivia.model import QuestionData, CategoryData
from daos.category_dao import CategoryDAO
from daos.question_dao import QuestionsDAO
import random

class TriviaGameError(Exception):
  pass

def getRandomQuestions(categories: list[CategoryData], num_rounds: int, question_dao: QuestionsDAO) -> list[QuestionData]:
  cat_ids = [c.id for c in categories]
  question_data = question_dao.getQuestionsFromCats(cat_ids=cat_ids)
  rand_ints = random.sample(range(0, len(question_data)), num_rounds)
  return [question_data[i] for i in rand_ints]

def newGame(id: str, players: list[Player], categories: list[CategoryData], num_rounds: int, question_dao: QuestionsDAO):
  questions = getRandomQuestions(categories=categories, num_rounds=num_rounds, question_dao=question_dao)
  return TriviaGame(
    id=id,
    players=players,categories=categories,
    num_rounds=num_rounds,
    questions=questions
  )

# TODO: QUESTION: Is there an inheritance for functions so I don't have to have the same parameters each time

def addCategories(game: TriviaGame, categories: list[CategoryData]):
  game.categories += categories

# def addQuestions(game: TriviaGame, questions: list[QuestionData]):
#   game.questions += questions

def nextQuestion(game: TriviaGame) -> int: # Will probably never need the return value, but it is here if it is needed
  if game.question_index < len(game.questions): # Only add if there are remaining questions
    game.question_index += 1
  return game.question_index

def getRound(game: TriviaGame) -> int:
  return game.question_index

def getQuestion(game: TriviaGame) -> QuestionData:
  if game.question_index < len(game.questions): # Only return if there are remaining questions
    return game.questions[game.question_index]

def addRoundTime(game: TriviaGame, player: Player, time: int):
  game.current_round_times[player] = time

def playerCorrect(game: TriviaGame, player: Player, time: int):
  if player not in game.complete_players:
    game.complete_players.append(player)
    game.current_round_times[player] = time
    if time < game.winning_time:
      game.winning_time = time

def playerWrong(game: TriviaGame, player: Player):
  if player not in game.complete_players:
    game.complete_players.append(player)

def playerCheckin(game: TriviaGame, player: Player, time: int):
  """Takes the player and their current time so far, and determines if their time has run out so far, based on the winning time so far.

  Args:
      game (TriviaGame): Current game
      player (Player): Player checking in
      time (int): How much time has passed for the player so far
  """
  if (time > game.winning_time) and (player not in game.complete_players):
    game.complete_players.append(player)
    

def roundComplete(game: TriviaGame) -> bool:
  """Determines if everyone has completed the round yet

  Args:
      game (TriviaGame): Current game

  Returns:
      bool: True if the round is complete, and they're ready to move on, and False otherwise
  """
  if len(game.players) == len(game.complete_players):
    return True
  elif len(game.players) > len(game.complete_players):
    return False
  else: # This should NEVER be true, so there should be some sort of error if there are more complete players than total players
    return None


def completeRound(game: TriviaGame):
  if roundComplete(game):
    # Get best time
    current_round_times = game.current_round_times
    best_time = min(current_round_times.values())
    if best_time != game.winning_time: # This should never be true, so if it is, I need to check the code
      raise TriviaGameError(f'The set winning time is {game.winning_time}, but the best time saved by players is {best_time}.')
    
    # Assign winners
    winners = []
    for player in current_round_times:
      if current_round_times[player] == best_time:
        winners.append(player)
    round_data = RoundData(winner=winners, time=best_time)
    if len(game.round_winners) > game.question_index: # This should never be true, since the round winners should not be added multiple times for the same round, but it is here if it is needed
      game.round_winners[game.question_index] = round_data
    else:
      game.round_winners.append(round_data)
    
    # Clean up, go to next round
    game.winning_time = None
    game.complete_players = []
    game.current_round_times = []
    nextQuestion(game)
  