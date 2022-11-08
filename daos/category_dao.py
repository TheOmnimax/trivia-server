from google.cloud import datastore

from .question_dao import QuestionsDAO
from .shared_functions import DatastoreDAO
from domains.trivia.model import CategoryData
from typing import List

class CategoryDAO(DatastoreDAO):
  """
  Used to work with trivia category data. Can generate new categories, retrieve category labels, and more.
  """
  def __init__(self, client: datastore.Client):
    """Initializer

    Args:
        client (google.cloud.datastore.Client): Google Datastore client
    """
    self._client = client

  def _genUniqueKey(self) -> datastore.Key:
    """Generate unique ID for new category, and put that into a key that is used by Google Datastore. Then checks if that key already exists, and if it does, generates a new one until a key that does not exist is generated.

    Returns:
        datastore.Key: New key that can be used for a new category.
    """
    return super()._genUniqueKey('category', 16)
  
  def _assembleKey(self, id: str) -> datastore.Key:
    """Takes a new ID, and generates a key for the new category.

    Args:
        id (str): "name" or "ID" of new key.

    Returns:
        datastore.Key: New key in datastore.
    """
    return super()._assembleKey('category', id)
  
  def _getCatEntity(self, id: str) -> datastore.Entity:
    """Takes the ID of a category, and retrieves it from datastore.

    Args:
        id (str): ID of the category

    Returns:
        datastore.Entity: Raw entity containing the category data.
    """
    cat_key = self._assembleKey(id)
    cat_entity = self._client.get(cat_key)
    return cat_entity
  
  def _getCatEntities(self, ids: List[str]) -> List[datastore.Entity]:
    """Retrieves multiple category datastore entities from IDs

    Args:
        ids (List[str]): List of IDs for category entities

    Returns:
        List[datastore.Entity]: Entities containing datastore data
    """
    keys = [self._assembleKey(id) for id in ids]
    return self._client.get_multi(keys)

  def exists(self, id: str) -> bool:
    """Checks if a category with that ID exists.

    Args:
        id (str): ID of category

    Returns:
        bool: True if there is a category with that ID, False if it does not exist.
    """
    cat_entity = self._getCatEntity(id)
    if cat_entity == None:
      return False
    else:
      return True

  def existsMulti(self, ids: List[str]) -> List[bool]:
    """Checks for multiple category IDs, and checks if they exist.

    Args:
        ids (List[str]): List of category IDs.

    Returns:
        List[bool]: Ordered list of which ones exist; True if it exists, False otherwise.
    """
    entities = self._getCatEntities(ids)
    return [e.key.name for e in entities if e != None]

  def getLabel(self, id: str) -> str:
    """Label of the specified category label ID

    Args:
        id (str): ID of the category

    Returns:
        str: Category label
    """
    cat_entity = self._getCatEntity(id)
    return cat_entity['label']
  
  def getCategories(self) -> List[CategoryData]:
    """Get data for every category saved in datastore

    Returns:
        List[CategoryData]: List of all categories and their data
    """
    query = self._client.query(kind='category')
    entities = list(query.fetch())
    return [CategoryData(label=e['label'], id=e.key.name) for e in entities]
  
  def _getCatsfromEntities(self, entities: List[datastore.Entity]) -> List[CategoryData]:
    """Takes raw entity data, and turns it into data that is much easier to work with in Python

    Args:
        entities (List[datastore.Entity]): Entities containing category data

    Returns:
        List[CategoryData]: List of categories with their data
    """
    return [CategoryData(label=e['label'], id=e.key.name) for e in entities]

  def _getCatEntitiesFromIds(self, ids: List[str]) -> datastore.Entity:
    """Gets raw category datastore entities from a list of IDs

    Args:
        ids (List[str]): List of category IDs

    Returns:
        datastore.Entity: List of category datastore entities
    """
    keys = [self._assembleKey(id) for id in ids]
    data = self._client.get_multi(keys=keys)
    return data
  
  def getCatsFromIds(self, ids: List[str]) -> List[CategoryData]:
    """Retrieves data for specified categories in a format easy to use in Python

    Args:
        ids (List[str]): List of category IDs

    Returns:
        List[CategoryData]: Category data for the specified IDs
    """
    entities = self._getCatEntitiesFromIds(ids=ids)
    categories = self._getCatsfromEntities(entities)
    return categories

  def getLabels(self, ids: List[str]) -> List[str]:
    """Labels for the specified categories

    Args:
        ids (List[str]): Category IDs

    Returns:
        List[str]: Category labels of the specified IDs
    """
    data = self._getCatEntitiesFromIds(ids=ids)
    return [l['label'] for l in data]
  
  def addCat(self, label: str, parents: List[str] = [], children: List[str] = []):
    """Add brand new category

    Args:
        label (str): Category label
        parents (List[str], optional): IDs of the parents of this category (categories this category should be listed under). Defaults to [], meaning it is a top-level category.
        children (List[str], optional): IDs of the children of this category (categories that are subcategories of this category). Defaults to [], meaning it is a bottom-level category.
    """
    cat_key = self._genUniqueKey()
    cat_entity = datastore.Entity(key=cat_key)
    cat_entity.update({
      'label': label,
      'parents': parents,
      'children': children
    })
    self._client.put(cat_entity)
  
  def deleteCat(self, id: str):
    """Deletes category with that ID

    Args:
        id (str): ID of the category to delete.
    """
    cat_key = self._assembleKey(id)
    self._client.delete(cat_key)
    question_dao = QuestionsDAO(client=self._client)
    question_dao.deleteCatFromQuestions(id)

  def deleteCats(self, ids: List[str]):
    """Deletes the categories with those IDs

    Args:
        ids (List[str]): IDs of the categories to delete
    """
    cat_keys = [self._assembleKey(id) for id in ids]
    self._client.delete_multi(cat_keys)
    question_dao = QuestionsDAO(client=self._client)
    question_dao.deleteCatsFromQuestions(ids)
  
  def updateCat(self, newData: CategoryData):
    """Update existing category with new data.

    Args:
        newData (CategoryData): Updated category data. Will already contain the category ID.
    """
    cat_key = self._assembleKey(id=newData.id)
    cat_entity = datastore.Entity(key=cat_key)
    cat_entity.update({
      'label': newData.label
    })
    self._client.put(cat_entity)
