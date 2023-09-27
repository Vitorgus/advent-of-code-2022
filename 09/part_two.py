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

def calculate_position(prev_knot, current_knot):
  cur_knot_line, cur_knot_row = current_knot
  prev_knot_line, prev_knot_row = prev_knot

  new_position = None
  min_distance = None

  for i in range(cur_knot_line-1, cur_knot_line+2):
    for j in range(cur_knot_row-1, cur_knot_row+2):
      if i == cur_knot_line and j == cur_knot_row:
        continue

      distance = ((prev_knot_line - i)**2 + (prev_knot_row-j)**2) ** (1/2)

      if min_distance == None or distance < min_distance:
        new_position = (i, j)
        min_distance = distance

  return new_position

def move(knots_pos, dir):
  head_line, head_row = knots_pos[0]

  knots_new_pos = []
  head_new_pos = set()

  if dir == 'U':
    head_new_pos = (head_line - 1, head_row)

  if dir == 'D':
    head_new_pos = (head_line + 1, head_row)

  if dir == 'L':
    head_new_pos = (head_line, head_row - 1)

  if dir == 'R':
    head_new_pos = (head_line, head_row + 1)

  knots_new_pos.append(head_new_pos)

  for i in range(1, len(knots_pos)):
    if not is_touching(knots_new_pos[i-1], knots_pos[i]):
      new_pos = calculate_position(knots_new_pos[i-1], knots_pos[i])
      knots_new_pos.append(new_pos)
    else:
      knots_new_pos.append(knots_pos[i])

  return knots_new_pos

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

KNOTS_NUMBER = 10

knots_position = [(0, 0) for x in range(KNOTS_NUMBER)]

tail_visited_positions = { knots_position[-1] }

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    input = line.strip().split()

    direction = input[0]
    n_steps = int(input[1])

    for i in range(n_steps):
      knots_position = move(knots_position, direction)

      tail_visited_positions.add(knots_position[-1])

# visualize_visited_positions(tail_visited_positions)
# print()
print(len(tail_visited_positions))
