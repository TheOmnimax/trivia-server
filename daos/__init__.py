from daos.base_models import *
from daos.category_dao import *
from daos.question_dao import *

from google.cloud import datastore

datastore_client = datastore.Client()

category_dao = CategoryDAO(datastore_client)