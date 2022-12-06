import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

def overlap(start_1, end_1, start_2, end_2):
  if start_1 < start_2 and end_1 < start_2:
    return False
  if start_2 < start_1 and end_2 < start_1:
    return False 
  return True

overlap_count = 0

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  for line in f:
    first_elf, second_elf = line.strip().split(',')

    first_elf_start, first_elf_end = first_elf.split('-')
    second_elf_start, second_elf_end = second_elf.split('-')

    first_elf_start = int(first_elf_start)
    first_elf_end = int(first_elf_end)
    second_elf_start = int(second_elf_start)
    second_elf_end = int(second_elf_end)

    if overlap(first_elf_start, first_elf_end, second_elf_start, second_elf_end):
      overlap_count += 1

print(overlap_count)
