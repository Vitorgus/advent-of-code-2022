import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

def is_touching(head_pos, tail_pos):
  head_line, head_row = head_pos
  tail_line, tail_row = tail_pos
  
  if (head_line >= tail_line - 1 and
      head_line <= tail_line + 1 and
      head_row >= tail_row - 1 and
      head_row <= tail_row + 1):
    return True

  return False

def move(head_pos, dir):
  line, row = head_pos

  if dir == 'U':
    return (line + 1, row)

  if dir == 'D':
    return (line - 1, row)

  if dir == 'L':
    return (line, row - 1)

  if dir == 'R':
    return (line, row + 1)

  return (line, row)

head_position = (0, 0)
tail_position = (0, 0)

tail_visited_positions = { tail_position }

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  for line in f:
    input = line.strip().split()

    direction = input[0]
    n_steps = int(input[1])

    for i in range(n_steps):
      new_head_position = move(head_position, direction)

      if not is_touching(new_head_position, tail_position):
        tail_position = head_position
        tail_visited_positions.add(tail_position)
      
      head_position = new_head_position

print(len(tail_visited_positions))
