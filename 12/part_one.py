import os
import string

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)


def get_square(grid, pos):
  line, column = pos
  square = grid[line][column]

  if square == START_SYMBOL:
    return 'a'
  elif square == END_SYMBOL:
    return 'z'
  else:
    return square

def set_square(grid, pos, value):
  line, column = pos
  grid[line][column] = value

def can_traverse(grid, current, target):
  current_square = get_square(grid, current)
  target_square = get_square(grid, target)

  if target_square not in string.ascii_lowercase:
    return False

  if ord(target_square) <= ord(current_square) + 1:
    return True
  else:
    return False


def can_go_up(grid, pos):
  line, column = pos
  if line > 0:
     next_pos = (line - 1, column)
     if can_traverse(grid, pos, next_pos):
      return True
  return False

def can_go_down(grid, pos):
  line, column = pos
  if line < len(grid) - 1:
     next_pos = (line + 1, column)
     if can_traverse(grid, pos, next_pos):
      return True
  return False

def can_go_left(grid, pos):
  line, column = pos
  if column > 0:
     next_pos = (line, column - 1)
     if can_traverse(grid, pos, next_pos):
      return True
  return False

def can_go_right(grid, pos):
  line, column = pos
  if column < len(grid[line]) - 1:
     next_pos = (line, column + 1)
     if can_traverse(grid, pos, next_pos):
      return True
  return False


def go_up(pos):
  line, column = pos
  return (line-1, column)

def go_down(pos):
  line, column = pos
  return (line+1, column)

def go_left(pos):
  line, column = pos
  return (line, column-1)

def go_right(pos):
  line, column = pos
  return (line, column+1)


def is_going_up(current_pos, next_pos):
  current_line, current_column = current_pos
  next_line, next_column = next_pos

  if next_column == current_column and next_line == current_line - 1:
    return True
  else:
    return False

def is_going_down(current_pos, next_pos):
  current_line, current_column = current_pos
  next_line, next_column = next_pos

  if next_column == current_column and next_line == current_line + 1:
    return True
  else:
    return False

def is_going_left(current_pos, next_pos):
  current_line, current_column = current_pos
  next_line, next_column = next_pos

  if next_column == current_column - 1 and next_line == current_line:
    return True
  else:
    return False

def is_going_right(current_pos, next_pos):
  current_line, current_column = current_pos
  next_line, next_column = next_pos

  if next_column == current_column + 1 and next_line == current_line:
    return True
  else:
    return False


def get_next_positions(grid, pos):
  next_positions = []

  if can_go_up(grid, pos):
    next_step = go_up(pos)
    next_positions.append(next_step)

  if can_go_down(grid, pos):
    next_step = go_down(pos)
    next_positions.append(next_step)

  if can_go_left(grid, pos):
    next_step = go_left(pos)
    next_positions.append(next_step)

  if can_go_right(grid, pos):
    next_step = go_right(pos)
    next_positions.append(next_step)

  return next_positions

def get_euclidean_distance(pos_1, pos_2):
  line_1, column_1 = pos_1
  line_2, column_2 = pos_2

  distance_squared = (line_2 - line_1)**2 + (column_2 - column_1)**2

  return distance_squared ** (1/2)

def get_min_path(grid, start_pos, end_pos):
  # A* pathfinding

  # Setup
  positions_explored = []
  positions_to_explore = []

  distance_to_target = dict()
  min_distance_to_position = dict()
  previous_position = dict()

  positions_to_explore.append(start_pos)
  distance_to_target[start_pos] = get_euclidean_distance(start_pos, end_pos)
  min_distance_to_position[start_pos] = 0


  f_value = lambda x: distance_to_target[x] + min_distance_to_position[x]

  # Main loop, while you have positions to explore
  while len (positions_to_explore) > 0:
    current_pos = min(positions_to_explore, key=f_value)

    # Check if you arrived
    if current_pos == end_pos:
      path = []
      pos = current_pos

      while pos in previous_position:
        path.append(pos)
        pos = previous_position[pos]

      return path[::-1]

    positions_to_explore.remove(current_pos)
    positions_explored.append(current_pos)

    # Check which directions you can go from here
    next_positions = get_next_positions(grid, current_pos)

    for next_pos in next_positions:
      if next_pos in positions_explored:
        # If position already explored, skip
        continue

      if next_pos not in positions_to_explore:
        # If position is not in list to explore, add it
        positions_to_explore.append(next_pos)

        distance = get_euclidean_distance(next_pos, end_pos)
        distance_to_target[next_pos] = distance

        min_distance = min_distance_to_position[current_pos] + 1
        min_distance_to_position[next_pos] = min_distance

        previous_position[next_pos] = current_pos
      else:
        # If positions was already added to explore
        current_min_distance = min_distance_to_position[current_pos] + 1
        if current_min_distance < min_distance_to_position[next_pos]:
          # If current path to position is less than previous path, update it
          min_distance_to_position[next_pos] = current_min_distance
          previous_position[next_pos] = current_pos

  # No path found
  return None


START_SYMBOL = 'S'
END_SYMBOL = 'E'

grid = []
start_position = None
end_position = None

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    line = list(line.strip())

    if START_SYMBOL in line:
      start_line = len(grid)
      start_column = line.index(START_SYMBOL)

      start_position = (start_line, start_column)

    if END_SYMBOL in line:
      end_line = len(grid)
      end_column = line.index(END_SYMBOL)

      end_position = (end_line, end_column)

    grid.append(line)


DEBUG_PRINT_PATH = False

min_path = get_min_path(grid, start_position, end_position)

if min_path == None:
  print('No path found')
else:
  min_steps_number = len(min_path)

  if DEBUG_PRINT_PATH:
    path_grid = [['.' for x in range(len(grid[y]))] for y in range(len(grid))]

    debug_min_path = [start_position] + min_path
    for i in range(len(debug_min_path) - 1):
      line, column = debug_min_path[i]

      if is_going_up(debug_min_path[i], debug_min_path[i+1]):
        path_grid[line][column] = '^'
      elif is_going_down(debug_min_path[i], debug_min_path[i+1]):
        path_grid[line][column] = 'v'
      elif is_going_left(debug_min_path[i], debug_min_path[i+1]):
        path_grid[line][column] = '<'
      elif is_going_right(debug_min_path[i], debug_min_path[i+1]):
        path_grid[line][column] = '>'

    finish_line, finish_column = debug_min_path[-1]
    path_grid[finish_line][finish_column] = END_SYMBOL

    for line in path_grid:
      for square in line:
        print(square, end='')
      print()

    print()
    print(f'Minumin number of steps = {min_steps_number}')
  else:
    print(min_steps_number)
