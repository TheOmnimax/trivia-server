"""For communicating with Gcloud datastore"""

from genericpath import exists
import json
from google.cloud import datastore
import logging
import json

from grpc import server
from tools.json_tools import JsonConverter
from tools.randomization import genCode
import threading
from fastapi import HTTPException

from os import environ

# environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\max-trivia-5a46a7a8eb28.json' # TESTING ONLY

class GcloudMemoryStorage:
  def __init__(self, client: datastore.Client, kind: str, code_size: int = 6, pre_accepted: list[type] = [], skipped_keys: list[str] = []):
    self._client = client
    self._code_size = code_size
    self._kind = kind
    self._lock = threading.Lock()
    self._json_converter = JsonConverter(pre_accepted=pre_accepted, skipped_keys=skipped_keys)
  
  def transaction(self, id: str, new_val_func):
    key = self._client.key(self._kind, id)
    with self._client.transaction():
      entity = self._client.get(key)
      print('Data from server:')
      print(key)
      print(entity)
      if (entity == None):
        return None
      else:
        server_data = self._json_converter.jsonToBaseModel(entity)
        print('Data collected:')
        print(server_data)
        print('Using function:')
        print(new_val_func)
        data = new_val_func(server_data)
        print('NEW DATA:')
        print(server_data)
        entity = datastore.Entity(key)
        new_data = self._json_converter.baseModelToJson(server_data)
        entity.update(new_data)
        print('NEW ENTITY:')
        print(entity)
        self._client.put(entity)
        return data
  
  def exists(self, id: str) -> bool:
    key = self._client.key(self._kind, id)
    if self._client.get(key) == None:
      return False
    else:
      return True
  
  def create(self, obj) -> str:
    code = genCode(self._code_size)
    while exists(code):
      code = genCode(self._code_size)
    dict_obj = self._json_converter.baseModelToJson(obj)
    key = self._client.key(self._kind, code)
    entity = datastore.Entity(key=key)
    entity.update(dict_obj)
    self._client.put(entity=entity)
    return code
        
  def get(self, id: str):
    key = self._client.key(self._kind, id)
    entity = self._client.get(key)
    if entity == None:
      return None
    else:
      return self._json_converter.jsonToBaseModel(dict(entity))
  
  def getAndSet(self, id: str, predicate=None, new_val_func=None):
    try:
      if (predicate == None) or (predicate(id)):
        server_data = self.get(id)
        self._lock.acquire()
        return_data = new_val_func(server_data)
        key = self._client.key(self._kind, id)
        entity = datastore.Entity(key)
        entity.update(server_data)
        self._client.put(entity)
        return return_data
      else:
        return {'error': f'Predicate failed for ID {id}.'}
    except:
      logging.exception('Error')
      return {'error': f'Error for ID {id}.'}
    finally:
      self._lock.release()