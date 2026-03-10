from __future__ import annotations

import os
import time
import sys

from enum import Enum, auto

start_time = time.time()

# Puzzle inputs and settings
DEFAULT_FILE_NAME = "input.txt"
DEBUG_PRINT = False

SPACE_CHAR = '.'
WALL_CHAR = '#'
EMPTY_CHAR = ' '
CURRENT_CHAR = 'O'
CLOCKWISE_INSTRUCTION = 'R'
COUNTERCLOCKWISE_INSTRUCTION = 'L'


# Classes
class Direction(Enum):
  UP = auto()
  DOWN = auto()
  LEFT = auto()
  RIGHT = auto()

  @classmethod
  def turn_clockwise(cls, dir: Direction) -> Direction:
    match dir:
     case Direction.UP:
       return Direction.RIGHT
     case Direction.RIGHT:
       return Direction.DOWN
     case Direction.DOWN:
       return Direction.LEFT
     case _:
       return Direction.UP

  @classmethod
  def turn_counterclockwise(cls, dir: Direction) -> Direction:
    match dir:
      case Direction.UP:
        return Direction.LEFT
      case Direction.LEFT:
        return Direction.DOWN
      case Direction.DOWN:
        return Direction.RIGHT
      case _:
        return Direction.UP

  @classmethod
  def get_value(cls, dir: Direction) -> int:
    match dir:
      case Direction.RIGHT:
        return 0
      case Direction.DOWN:
        return 1
      case Direction.LEFT:
        return 2
      case Direction.UP:
        return 3

    return -1

  @classmethod
  def get_arrow(cls, dir: Direction) -> str:
    match dir:
      case Direction.RIGHT:
        return '>'
      case Direction.DOWN:
        return 'v'
      case Direction.LEFT:
        return '<'
      case Direction.UP:
        return '^'

    return -1


class State:
  def __init__(self, debug: bool = False) -> None:
    self.debug = debug

    self.map: list[list[str]] = []
    self.current_row = 0
    self.current_column = 0
    self.current_direction = Direction.RIGHT
    self.move_history: list[tuple[int, int, Direction]] = []

  def __str__(self) -> str:
    return f'Row: {self.current_row} | Column: {self.current_column} | Direction: {self.current_direction.name}'

  def print_map(self) -> None:
    map = self.map

    if self.debug:
      map = []

      for line in self.map:
        map.append(line.copy())

      for move in self.move_history:
        row, column, direction = move
        arrow = Direction.get_arrow(direction)
        map[row][column] = arrow

      map[self.current_row][self.current_column] = CURRENT_CHAR

    for line in map:
      print(''.join(line))

  def add_map_line(self, line: list[str]) -> None:
    self.map.append(line)

  def find_password(self, instructions: list[str]) -> int:
    self._define_initial_position()

    for instruction in instructions:
      if instruction.isdecimal():
        self._walk_forward(int(instruction))

      else:
        if instruction == CLOCKWISE_INSTRUCTION:
          self.current_direction = Direction.turn_clockwise(self.current_direction)
        else:
          self.current_direction = Direction.turn_counterclockwise(self.current_direction)

    return self._calculate_password()

  def _define_initial_position(self) -> None:
    row = self.map[0]

    for col in range(len(row)):
      if row[col] == SPACE_CHAR:
        self.current_column = col
        break

  def _walk_forward(self, steps: int) -> None:
    row_increment = 0
    column_increment = 0

    match self.current_direction:
      case Direction.RIGHT:
        column_increment = 1
      case Direction.DOWN:
        row_increment = 1
      case Direction.LEFT:
        column_increment = -1
      case Direction.UP:
        row_increment = -1

    for i in range(steps):
      next_row = self.current_row + row_increment
      next_column = self.current_column + column_increment

      next_tile = self._get_tile(next_row, next_column)

      if next_tile == EMPTY_CHAR:
        reverse_row_increment = row_increment * -1
        reverse_column_increment = column_increment * -1

        next_row += reverse_row_increment
        next_column += reverse_column_increment

        while self._get_tile(next_row, next_column) != EMPTY_CHAR:
          next_row += reverse_row_increment
          next_column += reverse_column_increment

        next_row -= reverse_row_increment
        next_column -= reverse_column_increment

        next_tile = self._get_tile(next_row, next_column)

      if next_tile == WALL_CHAR:
        break
      else:
        self.move_history.append((self.current_row, self.current_column, self.current_direction))

        self.current_row = next_row
        self.current_column = next_column

  def _get_tile(self, row: int, column: int) -> str:
    if row < 0 or row >= len(self.map):
      return EMPTY_CHAR

    if column < 0 or column >= len(self.map[row]):
      return EMPTY_CHAR

    return self.map[row][column]

  def _calculate_password(self) -> int:
    return 1000 * (self.current_row + 1) + \
        4 * (self.current_column + 1) + \
        Direction.get_value(self.current_direction)


# Helper funcions
def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)


# Puzzle input parse
state = State(DEBUG_PRINT)
instructions: list[str] = []

file_name = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_FILE_NAME

try:
  with open(get_filepath(file_name), encoding="utf-8") as f:
    for line in f:
      l_strip = line.rstrip()

      if l_strip != "":
        if SPACE_CHAR in l_strip or WALL_CHAR in l_strip:
          state.add_map_line(list(l_strip))
        else:
          current_instruction = ''

          for char in l_strip:
            if char.isdecimal():
              current_instruction += char
            else:
              instructions.append(current_instruction)
              current_instruction = ''
              instructions.append(char)

          if current_instruction != '':
            instructions.append(current_instruction)

  password = state.find_password(instructions)

  if DEBUG_PRINT:
    state.print_map()
    print()

  print(password)

  print()
  print(f'Execution time: {(time.time() - start_time):.2f}s')
except FileNotFoundError:
  print(f'No such file: {file_name}')
