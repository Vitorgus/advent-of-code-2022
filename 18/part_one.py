import os

# Puzzle inputs and settings
FILE_NAME = "input.txt"
DEBUG_PRINT = False

# Helper funcions and classes
Coord = tuple[int, int, int]

class LavaDroplet:
  def __init__(self) -> None:
    self.cubes = {}

  def __str__(self) -> str:
    result = ""
    for cube in self.cubes:
      x, y, z = cube
      result += f'{x}, {y}, {z}\n'
    return result

  def add_cube(self, coord: Coord) -> None:
    self.cubes[coord] = True

  def calculate_surface(self) -> int:
    surface = 0

    for cube in self.cubes.keys():
      for coord in get_neightbor_coords(cube):
        if coord not in self.cubes:
          surface += 1

    return surface

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
