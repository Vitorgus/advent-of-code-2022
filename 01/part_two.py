import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

top_three = [0, 0, 0]
current_cal = 0

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip == "":
      min_top_three = min(top_three)

      if current_cal > min_top_three:
        for i in range(len(top_three)):
          if top_three[i] == min_top_three:
            top_three[i] = current_cal
            break

      current_cal = 0
    else:
      current_cal += int(l_strip)

print(sum(top_three))
