import threading
from tools.json_tools import JsonConverter
from fastapi import HTTPException
import json
import logging
from game_old.room import GameRoom
from enum import Enum

class GameError(Enum):
  room_not_found = 0

class MemoryStorage:
  def __init__(self, skipped_keys: list[str] = []):
    self._lock = threading.Lock()
    self._data = dict()
    self._json_converter = JsonConverter(skipped_keys=skipped_keys)
  
  def exists(self, room_code):
    if room_code in self._data:
      return True
    else:
      message = f'Game room {room_code} not found!'
      logging.info(message)
      raise HTTPException(status_code=404, detail=message)

  def set(self, game_room: GameRoom):
    self._lock.acquire()
    try:
      room_code = game_room.room_code
      self._data[room_code] = json.dumps(self._json_converter.objToJson(game_room))
    except:
      pass
    finally:
      self._lock.release()
        
  def get(self, room_code) -> GameRoom:
    """Given a game code, returns a game room

    Args:
        room_code (str): Game code

    Returns:
        GameRoom: Game room with that code
    """
    try:
      raw_data = self._data[room_code]
    except KeyError:
      logging.warning(f'Room code {room_code} not found')
      for code in self._data:
        logging.info(code)
      return dict()
    try:
      return self._json_converter.jsonToObj(json.loads(raw_data))
    except:
      logging.exception('Unknown error')
      return dict()
  def getAndSet(self, room_code, predicate=None, new_val_func=None):
    self._lock.acquire()
    try:
      if (predicate == None) or (predicate(room_code)):
        game_room = self.get(room_code)
        if new_val_func == None:
          return 'No action given'
        else:
          data = new_val_func(game_room)
          self._data[room_code] = json.dumps(self._json_converter.objToJson(game_room))
          return data
      else:
        logging.info(f'Game room {room_code} not found')
        return GameError.room_not_found
    except:
      logging.exception('Error')
      return {'error': 'Game room not found'}
    finally:
      self._lock.release()

room_storage = MemoryStorage()