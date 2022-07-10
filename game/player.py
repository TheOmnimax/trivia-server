class Player:
  def __init__(self, id: str, name: str = '', start_score: int = 0):
    self.id = id
    self.name = name
    self.score = start_score

class TimedPlayer(Player):
  def __init__(self, id: str, name: str = '', start_score: int = 0):
    super().__init__(id, name, start_score)
    self._start_time = 0
    self._can_take_action = False
    self._remaining_time = 0 # Currently does not have to be a class var, but adding if wanted for future games
  
  def playerStarted(self, timestamp: int, game_time: int):
    """Run when player starts the game. Used later to determine if the player is still allowed to play, or if their time has run out.

    Args:
        timestamp (int): Epoch time of when the player started.
        game_time (int): Total amount of time allotted to player in milliseconds
    """
    self._game_time = self._remaining_time = game_time
    self._start_time = timestamp
    self._can_take_action = True
  
  def withinTime(self, entered_time: int):
    """Checks whether the game (or turn) has ended for the player yet

    Args:
        entered_time (int): Epoch time of the action

    Returns:
        bool: Returns True if player is within the time limit and they can still enter data, and False if time is up
    """
    time_passed = entered_time - self._start_time
    self._remaining_time = self._game_time - time_passed

    if self._remaining_time > 0:
      self._can_take_action = True
    else:
      self._can_take_action = False
    
    return self._can_take_action
  
  def checkWithinTime(self):
    return self._can_take_action
