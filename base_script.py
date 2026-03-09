import os
import time

start_time = time.time()

# Puzzle inputs and settings
FILE_NAME = "example.txt"
DEBUG_PRINT = True

# Helper funcions and classes
def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

# Puzzle input parse
with open(get_filepath(FILE_NAME), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip != "":
      # TODO
      pass

print()
print(f'Execution time: {(time.time() - start_time):.2f}s')
