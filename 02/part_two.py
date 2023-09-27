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
  'C': Shapes.SCISSORS
}

letter_to_outcome = {
  'X': Outcome.LOSE,
  'Y': Outcome.DRAW,
  'Z': Outcome.WIN
}

winning_shape = {
  Shapes.ROCK: Shapes.PAPER,
  Shapes.PAPER: Shapes.SCISSORS,
  Shapes.SCISSORS: Shapes.ROCK
}

losing_shape = {
  Shapes.ROCK: Shapes.SCISSORS,
  Shapes.PAPER: Shapes.ROCK,
  Shapes.SCISSORS: Shapes.PAPER
}

def get_your_shape(enemy, outcome):
  if outcome == Outcome.DRAW:
    return enemy
  if outcome == Outcome.WIN:
    return winning_shape[enemy]
  if outcome == Outcome.LOSE:
    return losing_shape[enemy]

total_score = 0

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    shapes = line.split()

    enemy_shape = letter_to_shape[shapes[0]]
    outcome = letter_to_outcome[shapes[1]]

    your_shape = get_your_shape(enemy_shape, outcome)

    total_score += your_shape + outcome

print(total_score)
