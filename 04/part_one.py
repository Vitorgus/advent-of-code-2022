import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

def fully_overlap(start_1, end_1, start_2, end_2):
  if start_1 <= start_2 and end_1 >= end_2:
    return True
  if start_2 <= start_1 and end_2 >= end_1:
    return True
  return False

full_overlap_count = 0

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    first_elf, second_elf = line.strip().split(',')

    first_elf_start, first_elf_end = first_elf.split('-')
    second_elf_start, second_elf_end = second_elf.split('-')

    first_elf_start = int(first_elf_start)
    first_elf_end = int(first_elf_end)
    second_elf_start = int(second_elf_start)
    second_elf_end = int(second_elf_end)

    if fully_overlap(first_elf_start, first_elf_end, second_elf_start, second_elf_end):
      full_overlap_count += 1

print(full_overlap_count)
