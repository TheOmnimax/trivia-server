
import random
import string

code_chars = string.ascii_lowercase + string.digits

def genCode(length: int):
  return ''.join(random.choice(code_chars) for i in range(length))

def genUniqueCode(length: int, existing: list[str]):
  code = genCode(length)
  while code in existing:
    code = genCode(length)
  return code