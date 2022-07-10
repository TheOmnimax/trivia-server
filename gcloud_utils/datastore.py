from google.cloud import datastore

from os import environ

environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\max-trivia-5a46a7a8eb28.json' # TESTING ONLY

# TODO: QUESTION: Should there be one class instance per game, or one per server?
class TriviaDatastore:
  def __init__(self) -> None:
    self._client = datastore.Client()
    self._kind = 'question'

  
  def _getEntitiesWithCats(self, categories: list[str]) -> list[datastore.Entity]:
    entity_list = []
    for category in categories:
      query = self._client.query(kind=self._kind)
      query.add_filter('categories', '=', category)
      results = list(query.fetch())
      for result in results:
        if result not in entity_list:
          entity_list.append(result)
    
    return entity_list
  
  def getQuestionsWithCats(self, categories: list[str]) -> list[dict]:
    entities = self._getEntitiesWithCats(categories)
    question_data = list()
    for entity in entities:
      question_data.append(self.entityToJson(entity))
    return question_data

  def entityToJson(self, entity: datastore.Entity) -> dict:
    entity_dict = dict()
    for item in entity.items():
      entity_dict[item[0]] = item[1]
    return entity_dict

if __name__ == '__main__':
  triva_datastore = TriviaDatastore()
  results = triva_datastore.getQuestionsWithCats(categories=['Video games', 'Other', 'Pop culture'])
  print(results)