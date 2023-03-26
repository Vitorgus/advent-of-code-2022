import os
from enum import Enum, auto

# Puzzle inputs and settings
FILE_NAME = "input.txt"
DEBUG_PRINT = False

CHAMBER_WIDTH = 7
ROCK_SPAWN_LEFT_OFFSET = 2
ROCK_SPAWN_BOTTOM_OFFSET = 3

NUMBER_OF_ROCKS = 1000000000000

CHAMBER_WALLS = "|"
CHAMBER_LEFT_CORNER = "+"
CHAMBER_RIGHT_CORNER = "+"
CHAMBER_FLOOR = "-"
CHAMBER_AIR = "."
CHAMBER_STOPPED_ROCK = "#"
CHAMBER_CURRENT_ROCK = "@"

# Helper funcions and classes
Position = tuple[int, int]

def add_positions(pos_1: Position, pos_2: Position) -> Position:
  pos_1_x, pos_1_y = pos_1
  pos_2_x, pos_2_y = pos_2

  return (pos_1_x + pos_2_x, pos_1_y + pos_2_y)

def subtract_positions(pos_1: Position, pos_2: Position) -> Position:
  pos_1_x, pos_1_y = pos_1
  pos_2_x, pos_2_y = pos_2

  return (pos_1_x - pos_2_x, pos_1_y - pos_2_y)

class Movement(Enum):
  DOWN = auto()
  LEFT = auto()
  RIGHT = auto()

class Rock:
  def __init__(self, positions: list[Position] = [], name: str = "") -> None:
    self.relative_positions = positions
    self.name = name
  
  def get_positions(self, offset: Position = (0, 0)):
    offset_x, offset_y = offset
    return [(offset_x + pos_x, offset_y + pos_y) for (pos_x, pos_y) in self.relative_positions]

class HorizontalLine(Rock):
  def __init__(self) -> None:
    name = "h-line"
    super().__init__([(0, 0), (1, 0), (2, 0), (3, 0)], name)

class Cross(Rock):
  def __init__(self) -> None:
    name = "cross"
    super().__init__([(1, 2), (0, 1), (1, 1), (2, 1), (1, 0)], name)

class LShape(Rock):
  def __init__(self) -> None:
    name = "l-shape"
    super().__init__([(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)], name)

class VerticalLine(Rock):
  def __init__(self) -> None:
    name = "v-line"
    super().__init__([(0, 0), (0, 1), (0, 2), (0, 3)], name)

class Block(Rock):
  def __init__(self) -> None:
    name = "block"
    super().__init__([(0, 0), (1, 0), (0, 1), (1, 1)], name)

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
  
  def reset(self):
    self.current_index = 0

class CycleDetectionStep(Enum):
  SEARCHING = auto()
  AWAITING_SECOND_LOOP = auto()
  FINISHED = auto()

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

    self.reset()
  
  def reset(self):
    self.jet_pattern_manager.reset()

    self.rock_index = 0
    self.highest_rock_height = -1

    self.current_rock: Rock = None
    self.current_rock_pos: Position = None
    self.previous_rock_pos: Position = None

    self.movement_index = 0

    self.rock_positions: dict[Position, bool] = {}

    # Cycle detection
    self.cycle_detection_step = CycleDetectionStep.SEARCHING
    self.rocks_info: list[tuple[str, Position, int]] = []
    self.height_info: list[int] = []
    self.tortoise_index = 1
    self.hare_index = 2
    self.cycle_height_info: list[int] = []
    self.cycle_start = 0
    self.cycle_length = 0
  
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
  
  def get_rock_tower_height(self) -> int:
    return self.highest_rock_height + 1

  def is_cycle_detected(self) -> bool:
    return self.cycle_detection_step == CycleDetectionStep.FINISHED

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
  
  def fall_rock(self):
    self.previous_rock_pos = self.current_rock_pos

    self.current_rock = self.get_next_rock()
    self.current_rock_pos = self.get_rock_spawn_point()

    while True:
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

          break
        else:
          self.current_rock_pos = new_pos
      else:
        if movement == Movement.LEFT:
          new_pos = (current_pos_x - 1, current_pos_y)
        elif movement == Movement.RIGHT:
          new_pos = (current_pos_x + 1, current_pos_y)
      
        if self.check_collision(new_pos):
          pass
        else:
          self.current_rock_pos = new_pos
  
  def detect_cycle_step(self):
    if self.cycle_detection_step == CycleDetectionStep.FINISHED:
      return
    else:
      relative_rock_pos = subtract_positions(self.previous_rock_pos, self.current_rock_pos) if self.previous_rock_pos != None else None

      cycle_detection_info = (
          self.current_rock.name,
          relative_rock_pos,
          self.jet_pattern_manager.current_index
      )

      self.rocks_info.append(cycle_detection_info)
      self.height_info.append(self.highest_rock_height)

      if self.cycle_detection_step == CycleDetectionStep.AWAITING_SECOND_LOOP:
        self.tortoise_index += 1
        second_loop_end = self.cycle_start + (2 * self.cycle_length)

        if self.tortoise_index >= second_loop_end:
          second_loop_start = self.cycle_start + self.cycle_length

          self.cycle_height_info = [x - self.height_info[second_loop_start-1] for x in self.height_info[second_loop_start:second_loop_end]]
          self.cycle_detection_step = CycleDetectionStep.FINISHED
      else:
        if len(self.rocks_info) > self.hare_index:
          tortoise = self.rocks_info[self.tortoise_index]
          hare = self.rocks_info[self.hare_index]

          if tortoise != hare:
            self.tortoise_index += 1
            self.hare_index += 2
          else:
            if DEBUG_PRINT:
              print("Cycle detected!")
              print(f"Hare and tortoise first met at index {self.tortoise_index}")
              print()

            self.hare_index = self.tortoise_index
            self.tortoise_index = 0

            tortoise = self.rocks_info[self.tortoise_index]
            hare = self.rocks_info[self.hare_index]

            while tortoise != hare:
              self.hare_index += 1
              self.tortoise_index += 1

              tortoise = self.rocks_info[self.tortoise_index]
              hare = self.rocks_info[self.hare_index]
            
            if DEBUG_PRINT:
              print("Start of cycle found!")
              print(f"Hare and tortoise met at the start of the cycle at index {self.tortoise_index}")
              print()
            
            self.cycle_start = self.tortoise_index

            self.tortoise_index += 1
            tortoise = self.rocks_info[self.tortoise_index]

            while tortoise != hare:
              self.tortoise_index += 1
              tortoise = self.rocks_info[self.tortoise_index]
            
            self.cycle_length = self.tortoise_index - self.cycle_start

            if DEBUG_PRINT:
              print("Loop length found!")
              print(f"Tortoise found that the loop lenght is {self.cycle_length}")

            self.cycle_detection_step = CycleDetectionStep.AWAITING_SECOND_LOOP
            
  def get_rock_tower_height_after_n_rocks(self, n_rocks: int) -> int:
    if n_rocks <= 0:
      return 0
    
    self.reset()

    i = 0
    while i < n_rocks and not self.is_cycle_detected():
      self.fall_rock()
      self.detect_cycle_step()
      i += 1
    
    if not self.is_cycle_detected():
      return self.get_rock_tower_height()

    # Get simulated length so far
    height = self.get_rock_tower_height()

    # Get remaining height to finish current cycle
    current_cycle_index = (i - self.cycle_start - 1) % self.cycle_length
    height += self.cycle_height_info[-1] - self.cycle_height_info[current_cycle_index]
    remaining_rocks = n_rocks - i - (self.cycle_length - current_cycle_index)

    # Get height from cycles
    height += (remaining_rocks // self.cycle_length) * self.cycle_height_info[-1]

    # Get height from last rocks that don't complete a cycle
    height += self.cycle_height_info[remaining_rocks % self.cycle_length]

    return height

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

height = chamber.get_rock_tower_height_after_n_rocks(NUMBER_OF_ROCKS)

if DEBUG_PRINT:
  if not chamber.is_cycle_detected():
    print()
    print("No cycle detected!")

  print()
  print(f"Height after {NUMBER_OF_ROCKS} rocks: {height}")
else:
  print(height)
