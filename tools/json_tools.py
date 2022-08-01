import logging
from types import NoneType

from pydantic import BaseModel

from domains.game.model import GameRoom

class JsonConverter:
  def __init__(self, skipped_keys: list = []) -> None:
    self._accepted_tags = dict() # Will store all of the types used, so the dicts can be converted back to those types
    self._layer = 0
    self._skipped_keys = skipped_keys # These are for var names that are heavily nested, and can be skipped to save time
  
  def _addAcceptedTag(self, class_type: type):
    type_str = class_type.__name__
    self._accepted_tags[type_str] = class_type

  def addAcceptedTags(self, class_types: list[type]):
    for class_type in class_types:
      type_str = class_type.__name__
      self._accepted_tags[type_str] = class_type

  def objToJson(self, obj):
    self._layer += 1
    obj_type = type(obj)
    type_str = obj_type.__name__
    if (obj_type is list) or (obj_type is tuple):
      new_list = list()
      for item in obj:
        new_list.append(self.objToJson(item))
      self._layer -= 1
      return new_list
    elif obj_type is set:
      new_set = set()
      for item in obj:
        new_set.add(self.objToJson(item))
      self._layer -= 1
      return new_set
    elif obj_type is dict:
      new_dict = dict()
      for key in obj:
        new_dict[key] = self.objToJson(obj[key])
      self._layer -= 1
      return new_dict
    elif (obj_type in [int,float,str,bool]) or (obj == None):
      self._layer -= 1
      return obj
    else:
      try:
        new_dict = vars(obj)
      except TypeError:
        logging.error(f'Object type: {obj_type.__name__}\nData:\n{obj}')
        exit()
      for key in new_dict:
        if key in self._skipped_keys:
          new_dict[key] = new_dict[key]
        else:
          new_dict[key] = self.objToJson(new_dict[key])
      type_str = obj_type.__name__
      new_dict['type'] = type_str
      if type_str not in self._accepted_tags:
        self._accepted_tags[type_str] = obj_type
      self._layer -= 1
      return new_dict

  def jsonToObj(self, orig):
    orig_type = type(orig)

    if orig == None:
      return None
    elif orig_type is list:
      new_list = list()
      for item in orig:
        new_list.append(self.jsonToObj(item))
      return new_list
    elif orig_type is set:
      new_set = set()
      for item in orig:
        new_set.add(self.jsonToObj(item))
      return new_set
    elif orig_type is dict:
      if 'type' in orig:
        dict_type_str = orig.pop('type')
        # https://stackoverflow.com/questions/1176136/convert-string-to-python-class-object
        dict_type = self._accepted_tags[dict_type_str]
        new_obj = dict_type.__new__(dict_type)
        for key in orig:
          val = self.jsonToObj(orig[key])
          setattr(new_obj, key, val)
        return new_obj
      else:
        new_dict = dict()
        for key in orig:
          new_dict[key] = self.jsonToObj(orig[key])
        return new_dict
    elif orig_type in [int,float,str,bool]:
      return orig
    else:
      logging.error('Type error:')
      logging.error(f'Type: {orig_type}')
      logging.error(f'Data:\n{orig}')
      raise TypeError
  
  # def _dictForModel(self, data: dict):
  #   for key in data:
  #     value = data[key]
  #     val_type = type(value)
  #     if val_type == dict:
  #       value = self._dictForModel(value)
  #     elif val_type not in [int,float,str,bool,NoneType]:
  #       value = self.baseModelToJson(value)
  #       data[key] = value
  #   return data
  
  def baseModelToJson(self, data: BaseModel):
    data_type = type(data)
    if data_type in [int,float,str,bool,NoneType]:
      return data
    elif data_type in [list, set]:
      return [self.baseModelToJson(d) for d in data]
    elif data_type == dict:
      for key in data:
        data[key] = self.baseModelToJson(data[key])
      return data
    else: # Is a BaseModel (hopefully)
      json_data = data.__dict__
      self._addAcceptedTag(data_type)
      data_type_str = data_type.__name__
      for key in json_data:
        json_data[key] = self.baseModelToJson(json_data[key])
      json_data['type'] = data_type_str
      return json_data
  
  def jsonToBaseModel(self, data: dict):
    for key in data:
      value = data[key]
      if type(value) == dict:
        data[key] = self.jsonToBaseModel(value)
    if 'type' in data:
      data_type = self._accepted_tags[data.pop('type')]
      return data_type.parse_obj(data)
    else:
      return data