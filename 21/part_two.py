from __future__ import annotations

import os
import time
from enum import Enum

start_time = time.time()

# Puzzle inputs and settings
FILE_NAME = "input.txt"
DEBUG_PRINT = False
ROOT_MONKEY = "root"
HUMAN = "humn"


# Classes
class MathOperator(Enum):
  PLUS = '+'
  MINUS = '-'
  MULTIPLY = '*'
  DIVIDE = '/'

  @classmethod
  def from_symbol(cls, symbol: str) -> MathOperator:
    match symbol:
      case '/':
        return MathOperator.DIVIDE
      case '*':
        return MathOperator.MULTIPLY
      case '-':
        return MathOperator.MINUS
      case _:
        return MathOperator.PLUS

  @classmethod
  def get_opposite(cls, operator: MathOperator) -> MathOperator:
    match operator:
      case MathOperator.DIVIDE:
        return MathOperator.MULTIPLY
      case MathOperator.MULTIPLY:
        return MathOperator.DIVIDE
      case MathOperator.MINUS:
        return MathOperator.PLUS
      case _:
        return MathOperator.MINUS

  @classmethod
  def perform_operation(cls, value_1: int, value_2: int, operator: MathOperator) -> int:
    match operator:
      case MathOperator.DIVIDE:
        return value_1 // value_2
      case MathOperator.MULTIPLY:
        return value_1 * value_2
      case MathOperator.MINUS:
        return value_1 - value_2
      case _:
        return value_1 + value_2

class BaseMonkey:
  def __init__(self, name: str) -> None:
    self.name = name

  def __str__(self) -> str:
    return self.name

class NumberMonkey(BaseMonkey):
  def __init__(self, name: str, value: int) -> None:
    super().__init__(name)
    self.value = value

  def __str__(self) -> str:
    return f'{super().__str__()}: {self.value}'

class MathMonkey(BaseMonkey):
  def __init__(self, name: str, monkey_1: str, monkey_2: str, operator: MathOperator) -> None:
    super().__init__(name)
    self.monkey_1 = monkey_1
    self.monkey_2 = monkey_2
    self.operator = operator

  def __str__(self) -> str:
    return f'{super().__str__()}: {self.monkey_1} {self.operator.value} {self.monkey_2}'

class MonkeyTree:
  def __init__(self, debug: bool = False) -> None:
    self.monkeys: dict[str, BaseMonkey] = {}
    self.debug = debug
    self.root = None

  def add_monkey(self, monkey: BaseMonkey) -> None:
    self.monkeys[monkey.name] = monkey

    if monkey.name == ROOT_MONKEY:
      self.root = monkey

  def get_monkey(self, name: str) -> BaseMonkey:
    return self.monkeys[name]

  def is_human_in_subtree(self, name: str) -> bool:
    current_monkey = self.get_monkey(name)

    if current_monkey.name == HUMAN:
      return True
    elif isinstance(current_monkey, NumberMonkey):
      return False
    elif isinstance(current_monkey, MathMonkey):
      return self.is_human_in_subtree(current_monkey.monkey_1) \
          or self.is_human_in_subtree(current_monkey.monkey_2)

    return False

  def get_monkey_value(self, name: str) -> int:
    monkey = self.get_monkey(name)

    if isinstance(monkey, NumberMonkey):
      return monkey.value
    elif isinstance(monkey, MathMonkey):
      value_1 = self.get_monkey_value(monkey.monkey_1)
      value_2 = self.get_monkey_value(monkey.monkey_2)

      result = MathOperator.perform_operation(value_1, value_2, monkey.operator)

      return result

    return -1

  def get_human_value(self) -> int:
    if self.root == None:
      return -1

    current_monkey = self.root
    calculated_value = 0

    while current_monkey.name != HUMAN and isinstance(current_monkey, MathMonkey):
      monkey_value: int
      next_monkey_name: str
      human_in_first_subtree: bool = False

      if self.is_human_in_subtree(current_monkey.monkey_1):
        next_monkey_name = current_monkey.monkey_1
        monkey_value = self.get_monkey_value(current_monkey.monkey_2)
        human_in_first_subtree = True
      else:
        next_monkey_name = current_monkey.monkey_2
        monkey_value = self.get_monkey_value(current_monkey.monkey_1)

      operator: MathOperator

      if current_monkey.name == ROOT_MONKEY:
        calculated_value = monkey_value
      elif current_monkey.operator == MathOperator.MINUS and not human_in_first_subtree:
        calculated_value = MathOperator.perform_operation(monkey_value, calculated_value, MathOperator.MINUS)
      elif current_monkey.operator == MathOperator.DIVIDE and not human_in_first_subtree:
        calculated_value = MathOperator.perform_operation(monkey_value, calculated_value, MathOperator.DIVIDE)
      else:
        operator = MathOperator.get_opposite(current_monkey.operator)
        calculated_value = MathOperator.perform_operation(calculated_value, monkey_value, operator)

      if self.debug:
        other_monkey_name = current_monkey.monkey_2 if human_in_first_subtree else current_monkey.monkey_1

        print(f'Current monkey | {current_monkey}')
        print(f'Human is in subtree from monkey: {next_monkey_name}')
        print(f'Value from monkey {other_monkey_name}: {monkey_value}')
        print(f'Value needed for next subtree: {calculated_value}')
        print()

      current_monkey = self.get_monkey(next_monkey_name)

    if current_monkey.name == HUMAN:
      return calculated_value
    else:
      print("XABU")
      return 0


# Helper funcions
def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)


# Puzzle input parse
monkey_tree =  MonkeyTree(DEBUG_PRINT)

with open(get_filepath(FILE_NAME), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip != "":
      data = l_strip.split()
      name = data[0].replace(":", "")

      monkey = None

      if len(data) == 2:
        value = int(data[1])
        monkey = NumberMonkey(name, value)
      else:
        monkey_1 = data[1]
        operator = MathOperator.from_symbol(data[2])
        monkey_2 = data[3]

        monkey = MathMonkey(name, monkey_1, monkey_2, operator)

      monkey_tree.add_monkey(monkey)

print(monkey_tree.get_human_value())

print()
print(f'Execution time: {(time.time() - start_time):.2f}s')
