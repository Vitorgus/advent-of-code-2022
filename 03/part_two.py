import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

def get_priority(item):
  if item.islower():
    return ord(item) - ord('a') + 1
  else:
    return ord(item) - ord('A') + 27

GROUP_SIZE = 3

elf_group = []
priority_sum = 0

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    elf_group.append(line.strip())

    if len(elf_group) >= GROUP_SIZE:
      for item in elf_group[0]:
        all_elves_have_item = True

        for elf in elf_group[1:]:
          if not item in elf:
            all_elves_have_item = False
            break

        if all_elves_have_item:
          priority_sum += get_priority(item)
          break

      elf_group = []

print(priority_sum)
