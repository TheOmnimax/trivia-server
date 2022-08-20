"""For communicating with Gcloud datastore"""

from genericpath import exists
from html import entities
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

environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\max-trivia-5a46a7a8eb28.json' # TESTING ONLY

class GcloudMemoryStorage:
  def __init__(self, client: datastore.Client, code_size: int = 6, pre_accepted: list[type] = [], skipped_keys: list[str] = []):
    self._client = client
    self._code_size = code_size
    self._lock = threading.Lock()
    self._json_converter = JsonConverter(pre_accepted=pre_accepted, skipped_keys=skipped_keys)
  
  def transaction(self, kind: str, id: str, new_val_func, predicate = None):
    if (id == '' or id == None):
      return None
    key = self._client.key(kind, id)
    with self._client.transaction():
      entity = self._client.get(key)
      if (entity == None):
        return None
      else:
        server_data = self._json_converter.jsonToBaseModel(entity)

        if (predicate != None) and (not predicate(server_data)):
          return None

        data = new_val_func(server_data)
        entity = datastore.Entity(key)
        new_data = self._json_converter.baseModelToJson(server_data)
        entity.update(new_data)
        self._client.put(entity)
        return data

  def transactionMulti(self,
    pairs: tuple[str, str],
    new_val_func
    ):
    keys = [self._client.key(*p) for p in pairs]
    entities_unordered = list(self._client.get_multi(keys))
    # print('Unordered:')
    # print(entities_unordered)

    # Put into correct order
    entities = []
    for key in keys:
      name = key.name
      kind = key.kind
      added = False
      for entity in entities_unordered:
        if (entity.key.name == name) and (entity.kind == kind):
          entities.append(entity)
          added = True
          break
      if not added:
        entities.append(None)
    # print('Entities:')
    # print(entities)

    data_list = [self._json_converter.jsonToBaseModel(e) for e in entities]
    with self._client.transaction():
      return_data = new_val_func(*data_list)
      for e in range (len(entities)):
        entity = entities[e]
        update_data = self._json_converter.baseModelToJson(data_list[e])
        entity.update(update_data)
      self._client.put_multi(entities)
    return return_data


    pass

  def exists(self, kind: str, id: str) -> bool:
    key = self._client.key(kind, id)
    if self._client.get(key) == None:
      return False
    else:
      return True
  
  def create(self, kind: str, data) -> str:
    code = genCode(self._code_size)
    while exists(code):
      code = genCode(self._code_size)
    dict_obj = self._json_converter.baseModelToJson(data)
    key = self._client.key(kind, code)
    entity = datastore.Entity(key=key)
    entity.update(dict_obj)
    self._client.put(entity=entity)
    return code
  
  # def holdId(self, kind: str) -> str:
  #   code = genCode(self._code_size)
  #   while exists(code):
  #     code = genCode(self._code_size)
  #   key = self._client.key(kind, code)
  #   entity = datastore.Entity(key=key)
  #   self._client.put(entity=entity)
  #   return code

  # def addDataObject(self, kind: str, id: str, data) -> bool:
  #   key = self._client.key(kind, id)
  #   entity = self._client.get(key)
  #   entity.update(data)
  #   self._client.put(entity=entity)
        
  def get(self, kind: str, id: str, data_type = None):
    key = self._client.key(kind, id)
    entity = self._client.get(key)
    if entity == None:
      return None
    else:
      data = self._json_converter.jsonToBaseModel(dict(entity))
      if data_type == None:
        return data
      else:
        return data_type.parse_obj(data) 
  
  def getMulti(self, kind: str, ids: list[str], data_type = None) -> dict:
    keys = [self._client.key(kind, id) for id in ids]
    entities = self._client.get_multi(keys)
    if data_type == None:
      return {e.key.name:self._json_converter.jsonToBaseModel(dict(e)) for e in entities}
    else:
      return {e.key.name:data_type.parse_obj(self._json_converter.jsonToBaseModel(dict(e))) for e in entities}
  
  def query(self, kind: str, filters: list[tuple], data_type = None) -> list:
    query = self._client.query(kind=kind)
    for filter in filters:
      query.add_filter(*filter)
    raw_results = query.fetch()
    results = list()
    for result in raw_results:
      data = dict(result)
      data['id'] = result.key.name
      results.append(data)
    if (data_type == None):
      return results
    else:
      return [data_type.parse_obj(data) for data in results]