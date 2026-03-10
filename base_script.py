import os
import time
import sys

start_time = time.time()

# Puzzle inputs and settings
DEFAULT_FILE_NAME = "example.txt"
DEBUG_PRINT = True

# Helper funcions and classes
def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

# Puzzle input parse
file_name = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_FILE_NAME

try:
  with open(get_filepath(file_name), encoding="utf-8") as f:
    for line in f:
      l_strip = line.strip()

      if l_strip != "":
        # TODO
        pass

  print()
  print(f'Execution time: {(time.time() - start_time):.2f}s')
except FileNotFoundError:
  print(f'No such file: {file_name}')
