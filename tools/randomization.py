
import random
import string
from typing import List

code_chars = string.ascii_lowercase + string.digits

def genCode(length: int):
  return ''.join(random.choice(code_chars) for i in range(length))

def genUniqueCode(length: int, existing: List[str]):
  code = genCode(length)
  while code in existing:
    code = genCode(length)
  return code