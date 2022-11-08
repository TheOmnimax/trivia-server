from google.cloud import datastore

from .shared_functions import DatastoreDAO
from domains.trivia.model import QuestionData
from domains.trivia.schemas import NewQuestionSchema, QuestionUpdate
from typing import List

class QuestionsDAO(DatastoreDAO):
  def __init__(self, client: datastore.Client):
    """Initializer

    Args:
        client (datastore.Client): Google Datastore client
    """
    self._client = client
  
  def _genUniqueKey(self):
    """Generate unique ID for new question, and put that into a key that is used by Google Datastore. Then checks if that key already exists, and if it does, generates a new one until a key that does not exist is generated.

    Returns:
        datastore.Key: New key that can be used for a new question.
    """
    return super()._genUniqueKey('question', 16)
  
  def _assembleKey(self, id: str) -> datastore.Key:
    """Takes a new ID, and generates a key for the new question.

    Args:
        id (str): "name" or "ID" of new key.

    Returns:
        datastore.Key: New key in datastore.
    """
    return super()._assembleKey('question', id)

  def _rawToQuestion(self, question_data_raw: datastore.Entity) -> QuestionData:
    """Turns datastore entity into a format that is easy to use in Python

    Args:
        question_data_raw (datastore.Entity): Datastore entity with question data

    Returns:
        QuestionData: Data object that is easy to use in Python
    """
    question_data = QuestionData(
      id=question_data_raw.key.name,
      label=question_data_raw['label'],
      categories=question_data_raw['categories'],
      choices=question_data_raw['choices'],
      shuffle=question_data_raw['shuffle'],
      # shuffle_skip= question_data_raw['shuffle_skip'] == None  if 'shuffle_skip' in question_data_raw else None, # TODO: Make this work
      correct=question_data_raw['correct']
    )
    return question_data

  def getQuestion(self, id: str) -> QuestionData:
    """Get question data for the specified question ID

    Args:
        id (str): Question ID

    Returns:
        QuestionData: Question data that is easy to work with
    """
    question_key = self._assembleKey(id)
    question_data_raw = self._client.get(key=question_key)
    return self._rawToQuestion(question_data_raw)

  def getQuestions(self, ids: List[str]) -> List[QuestionData]:
    """Get data for multiple questions

    Args:
        ids (List[str]): IDs of quesions

    Returns:
        List[QuestionData]: List of question data objects that are easy to use in Python.
    """
    keys = [self._client.key('question', id) for id in ids]
    question_data_raw = self._client.get_multi(keys=keys)
    return [self._rawToQuestion(data) for data in question_data_raw]
  
  def _getRawQuestionsFromCat(self, cat_id: str) -> List[datastore.Entity]:
    """Takes a category IDs, and returns a list of "question" entities that uses that category. Those question entities are to be turned into "QuestionData" objects later.

    Args:
        cat_id (str): Category ID

    Returns:
        List[datastore.Entity]: List of Google Datastore question entities that contains the category provided.
    """
    query = self._client.query(kind='question')
    query.add_filter('categories', '=', cat_id)

    return list(query.fetch())
  
  def _getRawQuestionsFromCats(self, cat_ids: List[str]) -> List[datastore.Entity]:
    """Takes a list of category IDs, and returns a list of "question" entities that use those categories. Those question entities are to be turned into "QuestionData" objects later.

    Args:
        cat_ids (List[str]): List of category IDs

    Returns:
        List[datastore.Entity]: List of Google Datastore question entities that contain any of the categories provided.
    """
    all_entities = dict()
    for id in cat_ids:
      entities = self._getRawQuestionsFromCat(id)
      for entity in entities:
        entity_id = entity.key.name
        if entity_id not in all_entities:
          all_entities[entity_id] = entity
    return list(all_entities.values())

  def getAllQuestions(self) -> List[QuestionData]:
    """Get all questions saved in Google Datastore, regardless of category.

    Returns:
        List[QuestionData]: List of question data objects
    """
    query = self._client.query(kind='question')
    raw_data = list(query.fetch())

    return [self._rawToQuestion(d) for d in raw_data]


  def getQuestionsFromCat(self, cat_id: str) -> List[QuestionData]:
    """Get all questions with that category

    Args:
        cat_id (str): ID of the category

    Returns:
        List[QuestionData]: List of questions with their data
    """
    results_raw = self._getRawQuestionsFromCat(cat_id=cat_id)
    results = [self._rawToQuestion(d) for d in results_raw]
    return results

  def getQuestionsFromCats(self, cat_ids: List[str]) -> List[QuestionData]:
    """Get all questions with those categories (ensuring there are no duplicates if a question has multiple categories)

    Args:
        cat_ids (List[str]): List of category IDs

    Returns:
        List[QuestionData]: List of question data
    """
    question_data = dict()
    for id in cat_ids:
      new_data = self.getQuestionsFromCat(id)
      for q in new_data:
        if q.id not in question_data:
          question_data[q.id] = q
    return list(question_data.values())

  def addQuestion(self, question_data: NewQuestionSchema):
    """Adds a new question

    Args:
        question_data (NewQuestionSchema): New question data
    """
    # existing_cats = category_dao.existsMulti(question_data.categories) # So it only adds categories that currently exist
    # TODO: Set so only adds categories that actually exist

    question_key = self._genUniqueKey()
    question_entity = datastore.Entity(key=question_key)
    update_dict = {
      'label': question_data.label,
      'categories': question_data.categories,
      'choices': question_data.choices,
      'shuffle': question_data.shuffle,
      'correct': question_data.correct,
    }
    if question_data.shuffle_skip != None:
      update_dict['shuffle_skip'] = question_data.shuffle_skip
    question_entity.update(update_dict)
    self._client.put(question_entity)

  def updateQuestion(self, question_data: QuestionUpdate):
    """Update question with new data. The "QuestionUpdate" class has all-optional parameters, so it will only update the ones that have actual data.

    Args:
        question_data (QuestionUpdate): _description_
    """
    question_key = self._client.key('question', question_data.id)
    entity = datastore.Entity(key=question_key)

    update_dict = dict()

    if question_data.label != None:
      update_dict['label'] = question_data.label
    if question_data.categories != None:
      update_dict['categories'] = question_data.categories
    if question_data.choices != None:
      update_dict['choices'] = question_data.choices
    if question_data.shuffle != None:
      update_dict['shuffle'] = question_data.shuffle
    if question_data.shuffle_skip != None:
      update_dict['shuffle_skip'] = question_data.shuffle_skip
    if question_data.correct != None:
      update_dict['correct'] = question_data.correct

    entity.update(update_dict)
    self._client.put(entity)
  
  def deleteCatFromQuestions(self, cat_id: str):
    question_entities = self._getRawQuestionsFromCat(cat_id)
    for entity in question_entities:
      categories = entity['categories']
      categories.remove(cat_id)
      entity.update({'categories': categories})
    self._client.put_multi(question_entities)

  def deleteCatsFromQuestions(self, cat_ids: List[str]):
    question_entities = self._getRawQuestionsFromCats(cat_ids)
    for entity in question_entities:
      categories = entity['categories']
      for id in cat_ids:
        categories.remove(id)
      entity.update({'categories': categories})
    self._client.put_multi(question_entities)
  
  def deleteQuestion(self, id):
    key = self._assembleKey(id)
    self._client.delete(key)
