import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

def get_priority(item):
  if item.islower():
    return ord(item) - ord('a') + 1
  else:
    return ord(item) - ord('A') + 27

priority_sum = 0

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    middle = len(line.strip()) // 2

    first_compartiment = line[:middle]
    second_compartiment = line[middle:]

    duplicate_item = ''
    found = False

    for i in range(len(first_compartiment)):
      for j in range(len(second_compartiment)):
        if first_compartiment[i] == second_compartiment[j]:
          duplicate_item = first_compartiment[i]
          found = True
          break
      if found:
        break

    priority_sum += get_priority(duplicate_item)

print(priority_sum)
