import os
from enum import IntEnum, auto

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

class Shapes(IntEnum):
  ROCK = 1
  PAPER = 2
  SCISSORS = 3

class Outcome(IntEnum):
  WIN = 6
  DRAW = 3
  LOSE = 0

letter_to_shape = {
  'A': Shapes.ROCK,
  'B': Shapes.PAPER,
  'C': Shapes.SCISSORS,
  'X': Shapes.ROCK,
  'Y': Shapes.PAPER,
  'Z': Shapes.SCISSORS,
}

def get_outcome(enemy, you):
  if enemy == you:
    return Outcome.DRAW
  if ((enemy == Shapes.ROCK and you == Shapes.PAPER) or
      (enemy == Shapes.PAPER and you == Shapes.SCISSORS) or
      (enemy == Shapes.SCISSORS and you == Shapes.ROCK)):
    return Outcome.WIN
  else:
    return Outcome.LOSE

total_score = 0

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    shapes = line.split()

    enemy_shape = letter_to_shape[shapes[0]]
    your_shape = letter_to_shape[shapes[1]]

    total_score += your_shape + get_outcome(enemy_shape, your_shape)

print(total_score)
