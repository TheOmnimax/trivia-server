from fastapi import HTTPException
from typing import Dict, List, Tuple
from domains.trivia_game.model import TriviaGame, RoundData, TriviaPlayer
from domains.trivia.model import QuestionData, CategoryData
from daos.question_dao import QuestionsDAO
import random

class TriviaGameError(Exception):
  pass

def createTriviaPlayer(name: str, sid: str) -> TriviaPlayer:
  return TriviaPlayer(
    name=name,
    socket=sid
  )

def getRandomQuestions(categories: List[CategoryData], num_rounds: int, question_dao: QuestionsDAO) -> List[QuestionData]:
  cat_ids = [c.id for c in categories]
  question_data = question_dao.getQuestionsFromCats(cat_ids=cat_ids)
  num_questions = len(question_data)
  rand_ints = random.sample(
    range(0, num_questions),
    min(num_rounds, num_questions)
    )
  return [question_data[i] for i in rand_ints]

def newGame(categories: List[str], question_dao: QuestionsDAO, num_rounds: int = 10) -> TriviaGame:
  questions = getRandomQuestions(categories=categories, num_rounds=num_rounds, question_dao=question_dao)
  # TODO: Shuffle choices
  return TriviaGame(
    categories=categories,
    questions=questions,
    num_rounds=num_rounds,
  )

# TODO: QUESTION: Is there an inheritance for functions so I don't have to have the same parameters each time

def addCategories(game: TriviaGame, categories: List[CategoryData]):
  game.categories += categories

# def addQuestions(game: TriviaGame, questions: List[QuestionData]):
#   game.questions += questions

def addPlayer(game: TriviaGame, player_id: str):
  game.players.append(player_id)
  game.scores[player_id] = 0

def getPlayerNames(player_ids: List[str], player_data: Dict[str, TriviaPlayer]):
  return [player_data[p].name for p in player_ids]

def getNamedScores(scores: Dict[str, int], player_data: Dict[str, TriviaPlayer]):
  named_scores = dict()
  for p in scores:
    name = player_data[p].name
    named_scores[name] = scores[p]
  return named_scores

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
  else:
    return game.questions[len(game.questions) - 1]

def getCorrectValue(game: TriviaGame) -> int:
  question = getQuestion(game)
  return question.correct

def addRoundTime(game: TriviaGame, player_id: str, time: int): # How much time has passed for the player so far
  game.current_round_times[player_id] = time

def _playerAnswered(game: TriviaGame, player: TriviaPlayer, player_id: str, selected_choice: int):
  if player.selected_choice > -1:
    return
    raise HTTPException(status_code=428, detail='Player already answered question.')
  player.completed_round = True
  player.selected_choice = selected_choice
  game.complete_players.add(player_id)


def makePlayerCorrect(game: TriviaGame, player_id: str, player: TriviaPlayer, selected_choice: int):
  game.round_complete = True
  _playerAnswered(game=game, player=player, player_id=player_id, selected_choice=selected_choice)
  if game.round_winner == None:
    game.round_winner = player_id
  


def makePlayerWrong(game: TriviaGame, player: TriviaPlayer, player_id: str, selected_choice: int):
  _playerAnswered(game=game, player=player, player_id=player_id, selected_choice=selected_choice)
  if len(game.complete_players) >= len(game.players):
    game.round_complete = True

# def roundComplete(game: TriviaGame) -> bool:
#   return game.round_complete or len(game.complete_players) >= len(game.players)

def resetPlayer(player: TriviaPlayer):
  player.completed_round = False
  player.time_used = 0
  player.selected_choice = -1
  player.ready = True

def completeRound(game: TriviaGame):
  if game.round_complete:
    winner_id = game.round_winner
    game.round_winner = None
    game.round_complete = False
    if len(game.round_winners) <= game.question_index:
      game.round_winners.append(winner_id)
      # game.question_index += 1
    game.complete_players = set()
    if game.question_index + 1 >= len(game.questions): # Game is complete
      game.game_complete = True
      genWinners(game)
    pass


def getRoundResults(game: TriviaGame) -> RoundData:
  return game.round_winners[len(game.round_winners) - 1] # TODO: Make so the -1 is unnneccessary

def genWinners(game: TriviaGame):
  scores = {id:0 for id in game.players}
  print('Generating winners')
  print(game.round_winners)
  for id in game.round_winners:
    if id != None:
      scores[id] += 1
  game.scores = scores
  winning_score = max([scores[id] for id in scores])
  game.game_winners = [id for id in scores if scores[id] == winning_score]
  print(game.game_winners)

def getWinnerNames(game: TriviaGame, player_data: Dict[str, TriviaPlayer]) -> List[str]:
  if game.game_winners == None:
    return None
  else:
    winner_names = []
    for player_id in game.game_winners:
      winner_names.append(player_data[player_id].name)
    return winner_names

def getResultsWithNames(game: TriviaGame, player_data: Dict[str, TriviaPlayer]) -> Tuple[Dict[str, str], List[str]]:
  scores = game.scores
  print('Scores:')
  print(scores)
  named_scores = {player_data[player_id].name:scores[player_id] for player_id in scores}
  if game.game_winners == None:
    winner_names = []
  else:
    winner_names = [player_data[player_id].name for player_id in game.game_winners]
  return (named_scores, winner_names)

def startGame(game: TriviaGame):
  if game.question_index == -1:
    game.question_index = 0
    return True
  else:
    return False

def nextRound(game_id: str, player_ids: List[str], transaction) -> TriviaGame:
  def resetGameTime(game: TriviaGame) -> TriviaGame:
    game.winning_time = None
    if game.question_index < len(game.questions): # Only add if there are remaining questions
      game.round_complete = False
      game.question_index += 1
    return game
    # return game.players
  
  def resetPlayer(player: TriviaPlayer):
    player.time_used = 0
    player.selected_choice = -1
    player.completed_round = False
  
  for p in player_ids:
    transaction(kind='player', id=p, new_val_func=resetPlayer)
  return transaction(kind='trivia_game', id=game_id, new_val_func=resetGameTime)