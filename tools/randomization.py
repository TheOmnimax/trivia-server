
import random
import string

code_chars = string.ascii_lowercase + string.digits

def genCode(length: int):
  return ''.join(random.choice(code_chars) for i in range(length))