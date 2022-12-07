import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

MARKER_SIZE = 14

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  line = f.readline()
  
  for i in range(len(line) - MARKER_SIZE):
    marker_set = set(line[i:i + MARKER_SIZE])

    if len(marker_set) == MARKER_SIZE:
      print(i + MARKER_SIZE)
      break