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
  def __init__(self, blueprint: Blueprint, debug: bool = False) -> None:
    self.blueprint = blueprint
    self.debug = debug

    self.elapsed_time = 0
    self.resources: tuple[int, int, int, int] = (0, 0, 0, 0)
    self.robots: tuple[int, int, int, int] = (0, 0, 0, 0)
    self.current_building_robot: ResourceType | None = None

  def _can_build_robot(self, type: ResourceType) -> bool:
    costs = self.blueprint.robot_costs[type]

    for resource_index in range(len(costs)):
      if self.resources[resource_index] < costs[resource_index]:
        return False

    return True

  def _start_building_robot(self, type: ResourceType) -> None:
    if self.current_building_robot != None:
      print(f'ERROR: already building robot of type {self.current_building_robot}. Robot will be ovewritten')
    self.current_building_robot = type

    costs = self.blueprint.robot_costs[type]
    self.resources = subtract_resources(self.resources, costs)

    if self.debug:
      print(f'Spend {resource_to_string(costs)} to start building a {get_robot_type_string(type)} robot.')

  def _finish_building_robot(self) -> None:
    if self.current_building_robot == None:
      print(f'ERROR: No robot currently being built')
      return

    self.robots = add_resources(self.robots, get_resource_unit_tuple(self.current_building_robot))

    if self.debug:
      print(f'The new {get_robot_type_string(self.current_building_robot)} robot is ready; you now have {1} of them.')

    self.current_building_robot = None

  def elapse_time(self) -> None:
    pass



# - collect items
def get_robot_type_string(type: ResourceType) -> str:
    adj = 'cracking' if type == ResourceType.GEODE else 'collecting'
    return f'{type}-{adj}'

def add_resources(res1: tuple[int, int, int, int], res2: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
  return (
    res1[0] + res2[0],
    res1[1] + res2[1],
    res1[2] + res2[2],
    res1[3] + res2[3],
  )

def subtract_resources(res1: tuple[int, int, int, int], res2: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
  return (
    res1[0] - res2[0],
    res1[1] - res2[1],
    res1[2] - res2[2],
    res1[3] - res2[3],
  )

def get_resource_unit_tuple(type: ResourceType) -> tuple[int, int, int, int]:
  match type:
    case ResourceType.ORE:
      return (1, 0, 0, 0)
    case ResourceType.CLAY:
      return (0, 1, 0, 0)
    case ResourceType.OBSIDIAN:
      return (0, 0 ,1, 0)
    case ResourceType.GEODE:
      return (0, 0, 0, 1)
    case _:
      return (0, 0, 0, 0)

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
  match = STRING_PATTERN.fullmatch(line)

  if match != None:
    raw_data = match.groups()
    mapped_data = map(lambda x : int(x), raw_data)
    converted_data = tuple(mapped_data)
    return converted_data

  return ()

quality_sum = 0

with open(get_filepath(FILE_NAME), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip != "":
      data = get_blueprint_data(l_strip)
      new_blueprint = Blueprint(*data)
      new_blueprint.print_info()
      state = State(new_blueprint, DEBUG_PRINT)
      # quality_sum += new_blueprint.get_quality_level()
      # print(f'Quality Level: {new_blueprint.get_quality_level(DEBUG_PRINT)}')
      print()

print(quality_sum)
print()
print(f'Execution time: {time.time() - start_time}')
