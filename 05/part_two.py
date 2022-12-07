import os
import re

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

stacks = []

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  build_stacks = True
  numbers_pattern = re.compile(r'\d+')

  for line in f:
    if line == '\n':
      # Switch from building stacks to moving crates
      build_stacks = False
    elif build_stacks:
      # Build stacks step
      n_stacks = len(line) // 4

      if len(stacks) == 0:
        stacks = [[] for x in range(n_stacks)]
      
      for i in range(n_stacks):
        item_location = i*4 + 1
        item = line[item_location]

        if item.isalpha():
          stacks[i].insert(0, line[item_location])
    else:
      # Moving step
      numbers = numbers_pattern.findall(line)

      move_quantity = int(numbers[0])
      stack_from = int(numbers[1]) - 1
      stack_to = int(numbers[2]) - 1

      stacks[stack_to].extend(stacks[stack_from][-move_quantity:])
      stacks[stack_from] = stacks[stack_from][:-move_quantity]

for i in range(len(stacks)):
  print(stacks[i][-1], end="")

print()
