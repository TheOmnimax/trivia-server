from typing import Optional
from google.cloud import datastore
from pydantic import BaseModel
from tools.randomization import genCode


class DatastoreDAO:
  def __init__(self, client: datastore.Client):
    self._client = client
  
  def _genKey(self, kind: str, size: int):
    id = genCode(size)
    return self._client.key(kind, id)
  
  
  def _genUniqueKey(self, kind: str, size: int):
    key = self._genKey(kind, size)
    data = self._client.get(key)
    while data != None:
      key = self._genKey(kind, size)
      data = self._client.get(key)
    return key

  def _assembleKey(self, kind: str, id: str) -> datastore.Key:
    return self._client.key(kind, id)