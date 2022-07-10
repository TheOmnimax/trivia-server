from nis import cat
from typing import Optional
from xml.dom.minidom import Entity
from google.cloud import datastore
from pydantic import BaseModel
from tools.randomization import genCode

# BASE MODELS

class AddQuestionData(BaseModel):
  label: str
  categories: list[str]
  choices: list[str]
  shuffle: bool
  shuffle_skip: Optional[list[int]]
  correct: int

class QuestionData(AddQuestionData):
  id: str

class QuestionUpdateData(BaseModel):
  id: str
  label: Optional[str]
  categories: Optional[list[str]]
  choices: Optional[list[str]]
  shuffle: Optional[bool]
  shuffle_skip: Optional[list[int]]
  correct: Optional[int]

# SHARED FUNCTIONS

def _genKey(client: datastore.Client, kind: str, size: int):
    id = genCode(16)
    return client.key('question', id)

def _genUniqueKey(client: datastore.Client, kind: str, size: int):
  key = _genKey(client, kind, size)
  data = client.get(key)
  while data != None:
    key = _genKey(client, kind, size)
    data = client.get(key)
  return key


# QUESTION DAO

class QuestionsDAO:
  def __init__(self, client: datastore.Client):
    self._client = client

  def _rawToQuestion(self, question_data_raw: datastore.Entity) -> QuestionData:
    question_data = QuestionData(
      id=question_data_raw.key.name,
      label=question_data_raw['label'],
      categories=question_data_raw['categories'],
      choices=question_data_raw['choices'],
      shuffle=question_data_raw['shuffle'],
      shuffle_skip= question_data_raw['shuffle_skip'] == None  if 'shuffle_skip' in question_data_raw else None,
      correct=question_data_raw['correct']
    )
    return question_data

  def getQuestion(self, id: str) -> QuestionData:
    question_key = self._client.key('question', id)
    question_data_raw = self._client.get(key=question_key)
    return self._rawToQuestion(question_data_raw)

  def getQuestions(self, ids: list[str]) -> list[QuestionData]:
    keys = [self._client.key('question', id) for id in ids]
    question_data_raw = self._client.get_multi(keys=keys)
    return [self._rawToQuestion(data) for data in question_data_raw]
  
  def getQuestionsFromCat(self, cat_id: str) -> list[QuestionData]:
    query = self._client.query(kind='question')
    query.add_filter('categories', '=', cat_id)

    results_raw = list(query.fetch())
    results = [self._rawToQuestion(d) for d in results_raw]
    return results

  def getQuestionsFromCats(self, cat_ids: list[str]) -> list[QuestionData]:
    question_data = dict()
    for id in cat_ids:
      new_data = self.getQuestionsFromCat(id)
      for q in new_data:
        if q.id not in question_data:
          question_data[q.id] = q
    return list(question_data.values())
  
  def _genKey(self):
    id = genCode(16)
    return self._client.key('question', id)

  def addQuestion(self, question_data: AddQuestionData):
    question_key = _genUniqueKey(self._client, 'question', 16)
    question_entity = datastore.Entity(key=question_key)
    print(question_data)
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

  def updateQuestion(self, question_data: QuestionUpdateData):
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

# CATEGORIES

class CategoryDAO:
  def __init__(self, client: datastore.Client):
    self._client = client
  
  def _getCatEntity(self, id: str) -> datastore.Entity:
    cat_key = self._client.key('category', id)
    cat_entity = self._client.get(cat_key)
    return cat_entity
  
  def exists(self, id: str) -> str:
    cat_entity = self._getCatEntity(id)
    if cat_entity == None:
      return False
    else:
      return True

  def getLabel(self, id: str) -> str:
    cat_entity = self._getCatEntity(id)
    return cat_entity['label']
  
  def getLabels(self, ids: list[str]) -> list[str]:
    keys = [self._client.key('category', id) for id in ids]
    data = self._client.get_multi(keys=keys)
    return [l['label'] for l in data]
  
  def addCat(self, label: str, parents: list[str] = [], children: list[str] = []):
    cat_key = _genUniqueKey(self._client, 'category', 16)
    cat_entity = datastore.Entity(key=cat_key)
    cat_entity.update({
      'label': label,
      'parents': parents,
      'children': children
    })
    self._client.put(cat_entity)

