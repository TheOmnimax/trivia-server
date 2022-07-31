import random

def shuffle(data: int):
  data_length = len(data)
  max_int = data_length - 1
  for i in data_length:
    rand_int = random.randint(0, max_int)
    hold = data[rand_int]
    data[rand_int] = data[i]
    data[i] = hold
  return data

print(random.randint(3, 9))