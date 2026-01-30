import os
import re
import math
import time
from enum import Enum
from collections import deque
from collections.abc import Mapping
from copy import deepcopy
from functools import total_ordering

# type Resources = tuple[int, int, int, int]

start_time = time.time()

# Puzzle inputs and settings
FILE_NAME = "example.txt"
DEBUG_PRINT = True
TIME_LIMIT = 24


class ResourceType(Enum):
  ORE = 'ore'
  CLAY = 'clay'
  OBSIDIAN = 'obsidian'
  GEODE = 'geode'


class Blueprint:
  def __init__(self,
               id: int,
               ore_robot_ore_cost: int,
               clay_robot_ore_cost: int,
               obsidian_robot_ore_cost: int,
               obsidian_robot_clay_cost: int,
               geode_robot_ore_cost: int,
               geode_robot_obsidian_cost: int
               ) -> None:
    self.id = id
    self.robot_costs: Mapping[ResourceType, tuple[int, int, int, int]] = {
      ResourceType.ORE: (ore_robot_ore_cost, 0, 0, 0),
      ResourceType.CLAY: (clay_robot_ore_cost, 0, 0, 0),
      ResourceType.OBSIDIAN: (obsidian_robot_ore_cost, obsidian_robot_clay_cost, 0, 0),
      ResourceType.GEODE: (geode_robot_ore_cost, 0, geode_robot_obsidian_cost, 0)
    }

  def print_info(self) -> None:
    print(f'Blueprint ID: {self.id}')

    for key in self.robot_costs:
      print(f'\t{key.value} robot costs: {resource_to_string(self.robot_costs[key])}')


class State:
  def __init__(self, blueprint: Blueprint) -> None:
    self.blueprint = blueprint
    self.elapsed_time = 0
    self.resources: tuple[int, int, int, int] = (0, 0, 0, 0)
    self.robots: tuple[int, int, int, int] = (0, 0, 0, 0)

  def can_build_robot(self, robot_type: ResourceType) -> bool:
    costs = self.blueprint.robot_costs[robot_type]

    for resource_index in range(len(costs)):
      if self.resources[resource_index] < costs[resource_index]:
        return False

    return True

# - começar a construir robô
# - collect items
# - finalizar a construir robô
# - checar se dá pra construir robô


def resource_to_string(resources: tuple[int, int, int, int]) -> str:
  (ore, clay, obsidian, geode) = resources

  value = ''

  if ore > 0:
    value += f'{ore} ore'
  if clay > 0:
    if value != '':
      value += ' and '
    value += f'{clay} clay'
  if obsidian > 0:
    if value != '':
      value += ' and '
    value += f'{obsidian} obsidian'
  if geode > 0:
    if value != '':
      value += ' and '
    value += f'{geode} geode'

  return value if value != '' else 'no resources'

# Helper funcions and classes
def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

# Puzzle input parse
STRING_PATTERN = re.compile('Blueprint (\d+): Each ore robot costs (\d+) ore. Each clay robot costs (\d+) ore. Each obsidian robot costs (\d+) ore and (\d+) clay. Each geode robot costs (\d+) ore and (\d+) obsidian.')

def get_blueprint_data(line):
  raw_data = STRING_PATTERN.fullmatch(line).groups()
  mapped_data = map(lambda x : int(x), raw_data)
  converted_data = tuple(mapped_data)
  return converted_data

quality_sum = 0

with open(get_filepath(FILE_NAME), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip != "":
      data = get_blueprint_data(l_strip)
      new_blueprint = Blueprint(*data)
      new_blueprint.print_info()
      state = State(new_blueprint)
      # quality_sum += new_blueprint.get_quality_level()
      # print(f'Quality Level: {new_blueprint.get_quality_level(DEBUG_PRINT)}')
      print()

print(quality_sum)
print()
print(f'Execution time: {time.time() - start_time}')
