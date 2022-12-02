import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

max_cal = 0
current_cal = 0

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip == "":
      if current_cal > max_cal:
        max_cal = current_cal
        
      current_cal = 0
    else:
      current_cal += int(l_strip)

print(max_cal)
