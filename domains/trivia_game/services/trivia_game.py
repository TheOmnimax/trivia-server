from domains.trivia_game.model import TriviaGame, RoundData
from domains.game.model import Player
from domains.trivia.model import QuestionData, CategoryData
from daos.category_dao import CategoryDAO
from daos.question_dao import QuestionsDAO
import random
from tools.randomization import genUniqueCode

class TriviaGameError(Exception):
  pass

def getRandomQuestions(categories: list[CategoryData], num_rounds: int, question_dao: QuestionsDAO) -> list[QuestionData]:
  cat_ids = [c.id for c in categories]
  question_data = question_dao.getQuestionsFromCats(cat_ids=cat_ids)
  num_questions = len(question_data)
  rand_ints = random.sample(range(0, min(num_rounds, num_questions)), num_questions)
  return [question_data[i] for i in rand_ints]

def newGame(categories: list[CategoryData], question_dao: QuestionsDAO, num_rounds: int = 10) -> TriviaGame:
  questions = getRandomQuestions(categories=categories, num_rounds=num_rounds, question_dao=question_dao)
  # TODO: Shuffle choices
  return TriviaGame(
    players=[],
    categories=categories,
    questions=questions,
    num_rounds=num_rounds,
  )

# TODO: QUESTION: Is there an inheritance for functions so I don't have to have the same parameters each time

def addCategories(game: TriviaGame, categories: list[CategoryData]):
  game.categories += categories

# def addQuestions(game: TriviaGame, questions: list[QuestionData]):
#   game.questions += questions

def addPlayer(game: TriviaGame, player: Player):
  existing_codes = [player.id for player in game.players]
  id = genUniqueCode(6, existing_codes)
  game.players
  return id

def nextQuestion(game: TriviaGame) -> int: # Will probably never need the return value, but it is here if it is needed
    # Clean up, go to next round
  game.winning_time = None
  game.complete_players = []
  game.current_round_times = []
  if game.question_index < len(game.questions): # Only add if there are remaining questions
    game.question_index += 1
  return game.question_index

def getRound(game: TriviaGame) -> int:
  return game.question_index

def getQuestion(game: TriviaGame) -> QuestionData:
  if game.question_index < len(game.questions): # Only return if there are remaining questions
    return game.questions[game.question_index]

def getCorrectValue(game: TriviaGame) -> int:
  question = getQuestion(game)
  return question.correct

def addRoundTime(game: TriviaGame, player_id: str, time: int): # How much time has passed for the player so far
  game.current_round_times[player_id] = time

def makePlayerCorrect(game: TriviaGame, player_id: str, time: int):
  print('PLAYER RIGHT')
  if player_id not in game.complete_players:
    game.complete_players.append(player_id)
    print(f'NEW COMPLETE PLAYERS: {game.complete_players}')
    game.current_round_times[player_id] = time
    if time < game.winning_time:
      game.winning_time = time

def playerWrong(game: TriviaGame, player_id: str):
  print('PLAYER WRONG')
  if player_id not in game.complete_players:
    game.complete_players.append(player_id)
    print(f'NEW COMPLETE PLAYERS: {game.complete_players}')

def playerCheckin(game: TriviaGame, player_id: str, time: int):
  """Takes the player and their current time so far, and determines if their time has run out so far, based on the winning time so far.

  Args:
      game (TriviaGame): Current game
      player (Player): Player checking in
      time (int): How much time has passed for the player so far
  """
  if (time > game.winning_time) and (player_id not in game.complete_players):
    game.complete_players.append(player_id)
    

def roundComplete(game: TriviaGame) -> bool:
  """Determines if everyone has completed the round yet

  Args:
      game (TriviaGame): Current game

  Returns:
      bool: True if the round is complete, and they're ready to move on, and False otherwise
  """
  print(f'There are {game.players} players, and {game.complete_players} complete players')
  if len(game.players) == len(game.complete_players):
    return True
  elif len(game.players) > len(game.complete_players):
    return False
  else: # This should NEVER be true, so there should be some sort of error if there are more complete players than total players
    return None


def completeRound(game: TriviaGame):
  if roundComplete(game) and (len(game.round_winners) < game.question_index + 1): # If the round is complete, and the round winners have not been calculated yet
    # Get best time
    
    winners = list()
    current_round_times = game.current_round_times
    best_time = min(current_round_times.values())
    if game.winning_time == None: # No winner this round
      best_time = 0
    elif best_time != game.winning_time: # This should never be true, so if it is, I need to check the code
      raise TriviaGameError(f'The set winning time is {game.winning_time}, but the best time saved by players is {best_time}.')
    else:
      # Assign winners
      for player in current_round_times:
        if current_round_times[player] == best_time:
          winners.append(player)
    round_data = RoundData(winners=winners, time=best_time)
    if len(game.round_winners) > game.question_index: # This should never be true, since the round winners should not be added multiple times for the same round, but it is here if it is needed
      game.round_winners[game.question_index] = round_data
    else:
      game.round_winners.append(round_data)
    
    # nextQuestion(game) # TODO: Add a delay


def getRoundResults(game: TriviaGame) -> RoundData:
  return game.round_winners[game.question_index - 1] # TODO: Make so the -1 is unnneccessary
