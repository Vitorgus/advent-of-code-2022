import os
from enum import Enum, auto

# Puzzle inputs and settings
FILE_NAME = "input.txt"
DEBUG_PRINT_STEP_BY_STEP = False
DEBUG_PRINT_FINAL_CHAMBER = False

CHAMBER_WIDTH = 7
ROCK_SPAWN_LEFT_OFFSET = 2
ROCK_SPAWN_BOTTOM_OFFSET = 3

NUMBER_OF_ROCKS = 2022

CHAMBER_WALLS = "|"
CHAMBER_LEFT_CORNER = "+"
CHAMBER_RIGHT_CORNER = "+"
CHAMBER_FLOOR = "-"
CHAMBER_AIR = "."
CHAMBER_STOPPED_ROCK = "#"
CHAMBER_CURRENT_ROCK = "@"

# Helper funcions and classes
Position = tuple[int, int]

class Movement(Enum):
  DOWN = auto()
  LEFT = auto()
  RIGHT = auto()

class Rock:
  def __init__(self, positions: list[Position] = []) -> None:
    self.relative_positions = positions
  
  def get_positions(self, offset: Position = (0, 0)):
    offset_x, offset_y = offset
    return [(offset_x + pos_x, offset_y + pos_y) for (pos_x, pos_y) in self.relative_positions]

class HorizontalLine(Rock):
  def __init__(self) -> None:
    super().__init__([(0, 0), (1, 0), (2, 0), (3, 0)])

class Cross(Rock):
  def __init__(self) -> None:
    super().__init__([(1, 2), (0, 1), (1, 1), (2, 1), (1, 0)])

class LShape(Rock):
  def __init__(self) -> None:
    super().__init__([(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)])

class VerticalLine(Rock):
  def __init__(self) -> None:
    super().__init__([(0, 0), (0, 1), (0, 2), (0, 3)])

class Block(Rock):
  def __init__(self) -> None:
    super().__init__([(0, 0), (1, 0), (0, 1), (1, 1)])

class JetPatternManager:
  def __init__(self, pattern: str) -> None:
    self.pattern = pattern
    self.current_index = 0
  
  def get_next_movement(self):
    movement = self.pattern[self.current_index]
    self.current_index += 1

    if self.current_index >= len(self.pattern):
      self.current_index -= len(self.pattern)
    
    if movement == "<":
      return Movement.LEFT
    elif movement == ">":
      return Movement.RIGHT
    else:
      raise Exception("Unknown movement")

class Chamber:
  def __init__(self, width: int, jet_pattern: str) -> None:
    self.width = width
    self.jet_pattern_manager = JetPatternManager(jet_pattern)

    self.rocks: list[Rock] = [
      HorizontalLine(),
      Cross(),
      LShape(),
      VerticalLine(),
      Block()
    ]

    self.rock_index = 0
    self.highest_rock_height = -1
    self.has_rock_just_finished_falling = False

    self.current_rock = self.get_next_rock()
    self.current_rock_pos = self.get_rock_spawn_point()

    self.movement_index = 0

    self.rock_positions: dict[Position, bool] = {}
  
  def get_next_rock(self) -> Rock:
    rock = self.rocks[self.rock_index]
    self.rock_index += 1

    if self.rock_index >= len(self.rocks):
      self.rock_index -= len(self.rocks)
    
    return rock
  
  def get_rock_spawn_point(self) -> Position:
    return (
      ROCK_SPAWN_LEFT_OFFSET,
      self.highest_rock_height + ROCK_SPAWN_BOTTOM_OFFSET + 1
    )
  
  def get_next_movement(self) -> Movement:
    movement: Movement

    if self.movement_index % 2 == 0:
      movement = self.jet_pattern_manager.get_next_movement()
    else:
      movement = Movement.DOWN
    
    self.movement_index += 1

    return movement
  
  def check_collision(self, new_position: Position) -> bool:
    positions = self.current_rock.get_positions(new_position)

    collide = False

    for pos in positions:
      pos_x, pos_y = pos
      if pos in self.rock_positions or pos_x < 0 or pos_x >= self.width or pos_y < 0:
        collide = True
        break
    
    return collide
  
  def print_chamber(self):
    max_current_rock_pos = max(self.current_rock.get_positions(self.current_rock_pos), key= lambda x : x[1])
    highest_coord = max(self.highest_rock_height, max_current_rock_pos[1])

    for y in range(highest_coord, -1, -1):
      print(CHAMBER_WALLS, end="")

      for x in range(self.width):
        pos = (x, y)

        if pos in self.rock_positions:
          print(CHAMBER_STOPPED_ROCK, end="")
        elif pos in self.current_rock.get_positions(self.current_rock_pos):
          print(CHAMBER_CURRENT_ROCK, end="")
        else:
          print(CHAMBER_AIR, end="")
        
      print(CHAMBER_WALLS)
    
    print(CHAMBER_LEFT_CORNER, end="")
    print(CHAMBER_FLOOR * self.width, end="")
    print(CHAMBER_RIGHT_CORNER)
  
  def move_rock(self):
    current_pos_x, current_pos_y = self.current_rock_pos
    movement = self.get_next_movement()

    if movement == Movement.DOWN:
      new_pos = (current_pos_x, current_pos_y - 1)

      if self.check_collision(new_pos):
        current_rock_positions = self.current_rock.get_positions(self.current_rock_pos)
        for pos in current_rock_positions:
          self.rock_positions[pos] = True

        _, max_y = max(current_rock_positions, key= lambda x : x[1])
        if max_y > self.highest_rock_height:
          self.highest_rock_height = max_y

        self.current_rock = self.get_next_rock()
        self.current_rock_pos = self.get_rock_spawn_point()
        self.has_rock_just_finished_falling = True
      else:
        self.current_rock_pos = new_pos
        self.has_rock_just_finished_falling = False
    else:
      if movement == Movement.LEFT:
        new_pos = (current_pos_x - 1, current_pos_y)
      elif movement == Movement.RIGHT:
        new_pos = (current_pos_x + 1, current_pos_y)
    
      if self.check_collision(new_pos):
        pass
      else:
        self.current_rock_pos = new_pos
      
      self.has_rock_just_finished_falling = False
  
  def get_rock_tower_height(self) -> int:
    return self.highest_rock_height + 1

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

# Puzzle input parse
chamber: Chamber = None

with open(get_filepath(FILE_NAME), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip != "":
      chamber = Chamber(CHAMBER_WIDTH, l_strip)

i = 0
while i < NUMBER_OF_ROCKS:
  chamber.move_rock()

  if chamber.has_rock_just_finished_falling:
    i += 1
    if DEBUG_PRINT_STEP_BY_STEP:
      chamber.print_chamber()
      print()

if not DEBUG_PRINT_STEP_BY_STEP and DEBUG_PRINT_FINAL_CHAMBER:
  chamber.print_chamber()
  print()

print(chamber.get_rock_tower_height())
