import os


class Cave:

  SAND_SOURCE_COORD = (500, 0)

  ROCK_SYMBOL = '#'
  AIR_SYMBOL = '.'
  SAND_SYMBOL = 'o'
  SAND_SOURCE_SYMBOL = '+'
  SAND_PATH_SYMBOL = '~'

  MARGIN_LEFT = 1
  MARGIN_RIGHT = 1
  MARGIN_DOWN = 2

  def __init__(self, rock_paths):
    self._rock_paths = rock_paths

    min_x = None
    max_x = None
    max_y = None

    for path in rock_paths:
      for coord in path:
        coord_x, coord_y = coord
        if min_x == None or coord_x < min_x:
          min_x = coord_x
        if max_x == None or coord_x > max_x:
          max_x = coord_x
        if max_y == None or coord_y > max_y:
          max_y = coord_y

    offset = max_x - min_x

    self._min_x = min_x
    self._max_x = max_x
    self._max_y = max_y
    self._offset = offset

    cave_width = offset + Cave.MARGIN_LEFT + Cave.MARGIN_RIGHT
    cave_height = max_y + Cave.MARGIN_DOWN

    self._coords = [[Cave.AIR_SYMBOL for x in range(cave_width+1)] for y in range(cave_height+1)]
    self._last_sand_path = []

    for path in self._rock_paths:
      for i in range(len(path) - 1):
        self._set_path(path[i], path[i+1])

    self._set_space(Cave.SAND_SOURCE_COORD, Cave.SAND_SOURCE_SYMBOL)

  def fall_sand(self):
    sand_coord = Cave.SAND_SOURCE_COORD
    self._last_sand_path = []

    while True:
      next_coord = self._next_sand_coord(sand_coord)

      if next_coord == None:
        return False

      if next_coord == sand_coord:
        self._set_space(sand_coord, Cave.SAND_SYMBOL)
        return True

      self._last_sand_path.append(next_coord)
      sand_coord = next_coord

  def _next_sand_coord(self, current_coord):
    current_x, current_y = current_coord

    next_y = current_y + 1
    if next_y >= len(self._coords):
      return None

    next_space = (current_x, next_y)
    if self._get_space(next_space) == Cave.AIR_SYMBOL:
      return next_space

    next_space = (current_x-1, next_y)
    if self._get_space(next_space) == Cave.AIR_SYMBOL:
      return next_space

    next_space = (current_x+1, next_y)
    if self._get_space(next_space) == Cave.AIR_SYMBOL:
      return next_space

    return current_coord

  def _set_path(self, start, end):
    start_x, start_y = start
    end_x, end_y = end

    if start_x == end_x:
      coord_x = start_x

      range_start = min(start_y, end_y)
      range_end = max(start_y, end_y)

      for i in range(range_start, range_end+1):
        self._set_space((coord_x, i), Cave.ROCK_SYMBOL)
    elif start_y == end_y:
      coord_y = start_y

      range_start = min(start_x, end_x)
      range_end = max(start_x, end_x)

      for i in range(range_start, range_end+1):
        self._set_space((i, coord_y), Cave.ROCK_SYMBOL)
    else:
      raise Exception('Invalid path coordinates: {start} and {end} don\'t form a line')

  def _translate_coords(self, coord):
    coord_x, coord_y = coord

    return (coord_x - self._min_x + Cave.MARGIN_LEFT, coord_y)

  def _set_space(self, coord, tile):
    coord_x, coord_y = self._translate_coords(coord)
    self._coords[coord_y][coord_x] = tile

  def _get_space(self, coord):
    coord_x, coord_y = self._translate_coords(coord)
    return self._coords[coord_y][coord_x]

  def get_cave_string(self, last_sand_path=False):
    result = ''
    sand_path = [self._translate_coords(coord) for coord in self._last_sand_path]

    for line in range(len(self._coords)):
      for column in range(len(self._coords[line])):
        if last_sand_path and (column, line) in sand_path:
          result += Cave.SAND_PATH_SYMBOL
        else:
          result += self._coords[line][column]
      result += '\n'

    return result

  def __str__(self) -> str:
    return self.get_cave_string()


def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

paths = []

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    coordinates = line.strip().split(' -> ')

    path = []

    for coord in coordinates:
      coord_x, coord_y = [int(x) for x in coord.split(',')]

      path.append((coord_x, coord_y))

    paths.append(path)

DEBUG_PRINT_EACH_STEP = False
DEBUG_PRINT_FINAL_STEP = False

cave = Cave(paths)

sand_count = 0

while cave.fall_sand() == True:
  sand_count += 1
  if DEBUG_PRINT_EACH_STEP:
    print(f'== STEP {sand_count} ==')
    print(cave)

if DEBUG_PRINT_FINAL_STEP:
  print('== FINAL STATE ==')
  print(cave.get_cave_string(DEBUG_PRINT_FINAL_STEP))

if DEBUG_PRINT_EACH_STEP or DEBUG_PRINT_FINAL_STEP:
  print(f'Units of sand that fell down: {sand_count}')
else:
  print(sand_count)
