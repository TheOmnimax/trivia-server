from typing import Optional
from domains.trivia_game.model import TriviaGame, RoundData, TriviaPlayer
from domains.game.model import Player
from domains.trivia.model import QuestionData, CategoryData
from daos.category_dao import CategoryDAO
from daos.question_dao import QuestionsDAO
import random
from tools.randomization import genUniqueCode
from threading import Timer

class TriviaGameError(Exception):
  pass

def createTriviaPlayer(name: str) -> TriviaPlayer:
  return TriviaPlayer(
    name=name
  )

def getRandomQuestions(categories: list[CategoryData], num_rounds: int, question_dao: QuestionsDAO) -> list[QuestionData]:
  cat_ids = [c.id for c in categories]
  question_data = question_dao.getQuestionsFromCats(cat_ids=cat_ids)
  num_questions = len(question_data)
  rand_ints = random.sample(
    range(0, num_questions),
    min(num_rounds, num_questions)
    )
  return [question_data[i] for i in rand_ints]

def newGame(categories: list[str], question_dao: QuestionsDAO, num_rounds: int = 10) -> TriviaGame:
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

# def nextQuestion(game: TriviaGame) -> int: # Will probably never need the return value, but it is here if it is needed
#     # Clean up, go to next round
#   game.winning_time = None
#   game.complete_players = dict()
#   game.current_round_times = []
#   if game.question_index < len(game.questions): # Only add if there are remaining questions
#     game.question_index += 1
#   return game.question_index

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
  if player_id not in game.complete_players:
    game.complete_players[player_id] = time
    game.current_round_times[player_id] = time
    if game.winning_time == None:
      game.winning_time = time
    elif time < game.winning_time:
      game.winning_time = time

def makePlayerWrong(game: TriviaGame, player_id: str):
  if player_id not in game.complete_players:
    game.complete_players[player_id] = None

def playerCheckin(game: TriviaGame, player_id: str, time: int):
  """Takes the player and their current time so far, and determines if their time has run out so far, based on the winning time so far.

  Args:
      game (TriviaGame): Current game
      player (Player): Player checking in
      time (int): How much time has passed for the player so far
  """
  if (time > game.winning_time) and (player_id not in game.complete_players):
    game.complete_players[player_id] = time
    

# def roundComplete(game: TriviaGame) -> bool:
#   """Determines if everyone has completed the round yet

#   Args:
#       game (TriviaGame): Current game

#   Returns:
#       bool: True if the round is complete, and they're ready to move on, and False otherwise
#   """
#   if len(game.players) == len(game.complete_players):
#     return True
#   elif len(game.players) > len(game.complete_players):
#     return False
#   else: # This should NEVER be true, so there should be some sort of error if there are more complete players than total players
#     return None


def roundComplete(player_data: dict[str, TriviaPlayer], winning_time: Optional[int]) -> bool:
  complete_results = []
  for player_id in player_data:
    player = player_data[player_id]
    if (winning_time != None) and (player.time_used > winning_time): # Time exceeded current time
      complete_results.append(True)
    elif player.selected_choice == -1: # Not yet selected a choice
      complete_results.append(False)
    else:
      complete_results.append(True)
  
  if False in complete_results:
    return False
  else:
     return True

def completeRound(game: TriviaGame, player_data: dict[str, TriviaPlayer], completionFunction):
  # Check to make sure round is complete
  if roundComplete(player_data=player_data, winning_time=game.winning_time) and (len(game.round_winners) < game.question_index + 1): # If the round is complete, and the round winners have not been calculated yet
    # Get best time
    winning_time = game.winning_time
    current_question = game.questions[game.question_index]
    correct_ids = [p for p in player_data if player_data[p].selected_choice == current_question.correct] # IDs of players who selected the correct choice
    if (winning_time == None) or (len(correct_ids) == 0):
      winner_ids = list()
    else:
      winner_ids = [p for p in correct_ids if player_data[p].time_used == winning_time] # IDs of players who selected the correct choice, AND their time used matches the winning time
      if len(winner_ids) == 0:
        raise TriviaGameError(f'The set winning time is {game.winning_time}, but the best time saved by players is {winning_time}.')
      
    round_data = RoundData(winners=winner_ids, time=winning_time)
    if len(game.round_winners) > game.question_index: # This should never be true, since the round winners should not be added multiple times for the same round, but it is here if it is needed
      game.round_winners[game.question_index] = round_data
    else:
      game.round_winners.append(round_data)
    
    if game.question_index + 1 >= len(game.questions): # Game is complete
      game.game_complete = True
      genWinners(game)
    else:
      completionFunction()


def getRoundResults(game: TriviaGame) -> RoundData:
  return game.round_winners[game.question_index - 1] # TODO: Make so the -1 is unnneccessary

def genWinners(game: TriviaGame):
  scores = dict()
  for player_id in game.players:
    scores[player_id] = 0
  
  for round in game.round_winners:
    round_winners = round.winners
    for winner_id in round_winners:
      scores[winner_id] += 1
  game.final_scores = scores
  top_score = max(scores.values())
  if top_score == 0:
    game.game_winners = []
  else:
    winners = []
    for player_id in scores:
      if scores[player_id] == top_score:
        winners.append(player_id)
    game.game_winners = winners

def getWinnerNames(game: TriviaGame) -> list[str]:
  if game.game_winners == None:
    return None
  else:
    winner_names = []
    for player_id in game.game_winners:
      winner_names.append(game.players[player_id].name)
    return winner_names

def startGame(game: TriviaGame):
  if game.question_index == -1:
    game.question_index = 0
    return True
  else:
    return False

def nextRound(game_id: str, transaction):
  def resetGameTime(game: TriviaGame) -> list[str]:
    game.winning_time = None
    if game.question_index < len(game.questions): # Only add if there are remaining questions
      game.question_index += 1
    return game.players
  
  def resetPlayer(player: TriviaPlayer):
    player.time_used = 0
    player.selected_choice = -1
    player.completed_round = False
  
  player_ids = transaction(kind='trivia_game', id=game_id, new_val_func=resetGameTime)
  for p in player_ids:
    transaction(kind='player', id=p, new_val_func=resetPlayer)