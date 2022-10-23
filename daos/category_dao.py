from google.cloud import datastore

from .question_dao import QuestionsDAO
from .shared_functions import DatastoreDAO
from domains.trivia.model import CategoryData
from typing import List

class CategoryDAO(DatastoreDAO):
  def __init__(self, client: datastore.Client):
    self._client = client

  def _genUniqueKey(self):
    return super()._genUniqueKey('category', 16)
  
  def _assembleKey(self, id: str) -> datastore.Key:
    return super()._assembleKey('category', id)
  
  def _getCatEntity(self, id: str) -> datastore.Entity:
    cat_key = self._assembleKey(id)
    cat_entity = self._client.get(cat_key)
    return cat_entity
  
  def _getCatEntities(self, ids: List[str]) -> List[datastore.Entity]:
    keys = [self._assembleKey(id) for id in ids]
    return self._client.get_multi(keys)

  def exists(self, id: str) -> str:
    cat_entity = self._getCatEntity(id)
    if cat_entity == None:
      return False
    else:
      return True

  def existsMulti(self, ids: List[str]) -> List[bool]:
    entities = self._getCatEntities(ids)
    return [e.key.name for e in entities if e != None]

  def getLabel(self, id: str) -> str:
    cat_entity = self._getCatEntity(id)
    return cat_entity['label']
  
  def getCategories(self) -> List[CategoryData]:
    query = self._client.query(kind='category')
    entities = list(query.fetch())
    return [CategoryData(label=e['label'], id=e.key.name) for e in entities]
  
  def _getCatsfromEntities(self, entities: List[datastore.Entity]):
    return [CategoryData(label=e['label'], id=e.key.name) for e in entities]

  def _getCatEntitiesFromIds(self, ids: List[str]) -> datastore.Entity:
    keys = [self._assembleKey(id) for id in ids]
    data = self._client.get_multi(keys=keys)
    return data
  
  def getCatsFromIds(self, ids: List[str]) -> List[CategoryData]:
    entities = self._getCatEntitiesFromIds(ids=ids)
    categories = self._getCatsfromEntities(entities)
    return categories

  def getLabels(self, ids: List[str]) -> List[str]:
    data = self._getCatEntitiesFromIds(ids=ids)
    return [l['label'] for l in data]
  
  def addCat(self, label: str, parents: List[str] = [], children: List[str] = []):
    cat_key = self._genUniqueKey()
    cat_entity = datastore.Entity(key=cat_key)
    cat_entity.update({
      'label': label,
      'parents': parents,
      'children': children
    })
    self._client.put(cat_entity)
  
  def deleteCat(self, id: str):
    cat_key = self._assembleKey(id)
    self._client.delete(cat_key)
    question_dao = QuestionsDAO(client=self._client)
    question_dao.deleteCatFromQuestions(id)

  def deleteCats(self, ids: List[str]):
    cat_keys = [self._assembleKey(id) for id in ids]
    self._client.delete_multi(cat_keys)
    question_dao = QuestionsDAO(client=self._client)
    question_dao.deleteCatsFromQuestions(ids)
  
  def updateCat(self, newData: CategoryData):
    cat_key = self._assembleKey(id=newData.id)
    cat_entity = datastore.Entity(key=cat_key)
    cat_entity.update({
      'label': newData.label
    })
    self._client.put(cat_entity)
