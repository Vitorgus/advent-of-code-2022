import os

# Puzzle inputs and settings
FILE_NAME = "input.txt"
DEBUG_PRINT = False

# Helper funcions and classes
Coord = tuple[int, int, int]

class LavaDroplet:
  def __init__(self) -> None:
    self.cubes = {}

    self.min_x = 0
    self.max_x = 0
    self.min_y = 0
    self.max_y = 0
    self.min_z = 0
    self.max_z = 0

  def __str__(self) -> str:
    result = ""
    for cube in self.cubes:
      x, y, z = cube
      result += f'{x}, {y}, {z}\n'
    return result

  def add_cube(self, coord: Coord) -> None:
    self.cubes[coord] = True

    x, y, z = coord

    if x < self.min_x:
      self.min_x = x
    if x > self.max_x:
      self.max_x = x

    if y < self.min_y:
      self.min_x = y
    if y > self.max_y:
      self.max_y = y

    if z < self.min_z:
      self.min_x = z
    if z > self.max_z:
      self.max_z = z


  def calculate_surface(self) -> int:
    surface = 0

    starting_cube = (self.min_x-1, self.min_y-1, self.min_z-1)

    visited_cubes = {}
    to_visit_cubes = [starting_cube]

    while len(to_visit_cubes) > 0:
      current_cube = to_visit_cubes.pop(0)

      if current_cube not in visited_cubes:

        neightbor_coords = get_neightbor_coords(current_cube)
        for coord in neightbor_coords:
          if coord in self.cubes:
            surface += 1
          elif coord not in visited_cubes and is_cube_inside(coord, self.min_x-1, self.max_x+1, self.min_y-1, self.max_y+1, self.min_z-1, self.max_z+1):
            to_visit_cubes.append(coord)


        visited_cubes[current_cube] = True

    return surface

def is_cube_inside(coord, min_x, max_x, min_y, max_y, min_z, max_z) -> bool:
  x, y, z = coord

  return x >= min_x and x <= max_x and y >= min_y and y <= max_y and z >= min_z and z <= max_z

def get_neightbor_coords(coord: Coord) -> list[Coord]:
  x, y, z = coord

  return [
    (x-1, y, z),
    (x+1, y, z),
    (x, y-1, z),
    (x, y+1, z),
    (x, y, z-1),
    (x, y, z+1)
  ]

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

# Puzzle input parse
lava = LavaDroplet()

with open(get_filepath(FILE_NAME), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip != "":
      coords = map(int, l_strip.split(','))
      lava.add_cube(tuple(coords))

surface = lava.calculate_surface()

if DEBUG_PRINT:
  print("Cube coordinates:")
  print(lava)
  print()
  print(f"Calculated lava surface: {surface}")
else:
  print(surface)
