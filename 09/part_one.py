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
    return (line - 1, row)

  if dir == 'D':
    return (line + 1, row)

  if dir == 'L':
    return (line, row - 1)

  if dir == 'R':
    return (line, row + 1)

  return (line, row)

def visualize_visited_positions(positions, line_size=None, row_size=None):
  max_line = max([line for (line, row) in positions])
  min_line = min([line for (line, row) in positions])
  max_row = max([row for (line, row) in positions])
  min_row = min([row for (line, row) in positions])

  n_lines = max_line - min_line + 1
  n_rows = max_row - min_row + 1

  if line_size == None and row_size == None:
    grid = [['.' for x in range(n_rows)] for y in range(n_lines)]
  else:
    grid = [['.' for x in range(row_size)] for y in range(line_size)]

  for (line, row) in positions:
    new_line = line - min_line
    new_row = row - min_row

    grid[new_line][new_row] = '#'

  grid[-min_line][-min_row] = 's'

  for line in grid:
    for pos in line:
      print(pos, end='')
    print()

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

# visualize_visited_positions(tail_visited_positions)
# print()
print(len(tail_visited_positions))
