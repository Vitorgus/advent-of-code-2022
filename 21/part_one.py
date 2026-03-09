from __future__ import annotations

import os
import time
from enum import Enum

start_time = time.time()

# Puzzle inputs and settings
FILE_NAME = "input.txt"
DEBUG_PRINT = False
ROOT_MONKEY = "root"


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

class MonkeyGraph:
  def __init__(self, debug: bool = False) -> None:
    self.monkeys: dict[str, BaseMonkey] = {}
    self.debug = debug

  def add_monkey(self, monkey: BaseMonkey) -> None:
    self.monkeys[monkey.name] = monkey

  def get_monkey(self, name: str) -> BaseMonkey:
    return self.monkeys[name]

  def get_monkey_value(self, name: str, depth: int = 0) -> int:
    monkey = self.get_monkey(name)

    if isinstance(monkey, NumberMonkey):
      if self.debug:
        print(f'{"| " * depth}Monkey {monkey.name}: value {monkey.value}')
      return monkey.value
    elif isinstance(monkey, MathMonkey):
      value_1 = self.get_monkey_value(monkey.monkey_1, depth+1)
      value_2 = self.get_monkey_value(monkey.monkey_2, depth+1)

      result = MathOperator.perform_operation(value_1, value_2, monkey.operator)

      if self.debug:
        print(f'{"| " * depth}Monkey {monkey.name}: {monkey.monkey_1} {monkey.operator.value} {monkey.monkey_2} = {value_1} {monkey.operator.value} {value_2} = {result}')

      return result

    return -1


# Helper funcions
def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)


# Puzzle input parse
monkey_graph = MonkeyGraph(DEBUG_PRINT)

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

      monkey_graph.add_monkey(monkey)

if DEBUG_PRINT:
  print()

print(monkey_graph.get_monkey_value(ROOT_MONKEY))

print()
print(f'Execution time: {(time.time() - start_time):.2f}s')
