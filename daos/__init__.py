from daos.category_dao import *
from daos.question_dao import *

from os import environ
# environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\max-trivia-5a46a7a8eb28.json' # TESTING ONLY

from google.cloud import datastore

datastore_client = datastore.Client()

category_dao = CategoryDAO(datastore_client)