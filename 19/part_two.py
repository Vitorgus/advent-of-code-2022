import os
import re
import time
import math
from enum import Enum
from collections import deque
from collections.abc import Mapping
from copy import deepcopy

# type Resources = tuple[int, int, int, int]

start_time = time.time()

# Puzzle inputs and settings
FILE_NAME = "input.txt"
DEBUG_PRINT = False
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
    self.max_cost: tuple[int, int, int, int] = (
      max(ore_robot_ore_cost, clay_robot_ore_cost, obsidian_robot_ore_cost, geode_robot_ore_cost),
      obsidian_robot_clay_cost,
      geode_robot_obsidian_cost,
      0
    )

  def print_info(self) -> None:
    print(f'Blueprint ID: {self.id}')

    for key in self.robot_costs:
      print(f'\t{key.value} robot costs: {resource_to_string(self.robot_costs[key])}')

    print()


class State:
  def __init__(self, blueprint: Blueprint, time_limit: int, debug: bool = False) -> None:
    self.blueprint = blueprint
    self.debug = debug

    self.time_limit = time_limit
    self.remaining_time = time_limit
    self.resources: tuple[int, int, int, int] = (0, 0, 0, 0)
    self.robots: tuple[int, int, int, int] = (1, 0, 0, 0)
    self.current_building_robot: ResourceType | None = None
    self.debug_build_history: list[ResourceType] = []

    self.perm_robot_blacklist = set[ResourceType]()

    self.time_to_build_robot: dict[ResourceType, int] = {}
    self._calculate_time_to_build_robots()

  def get_geodes(self) -> int:
    return self.get_resource_qty(ResourceType.GEODE)

  def get_robots_qty(self, type: ResourceType) -> int:
    return get_single_resource(self.robots, type)

  def get_resource_qty(self, type: ResourceType) -> int:
    return get_single_resource(self.resources, type)

  def print_build_history(self) -> None:
    if len(self.debug_build_history) == 0:
      return

    blueprint = self.blueprint

    robot_index = 0
    next_robot = self.debug_build_history[robot_index]

    current_resources = (0, 0, 0, 0)
    current_robots = (1, 0, 0, 0)

    is_building_robot = False

    for minute in range(1, self.time_limit + 1):
      print(f'== Minute {minute} ==')

      if next_robot != None:
        cost = blueprint.robot_costs[next_robot]

        if can_build(current_resources, cost):
          print(f'Spent {resource_to_string(cost)} to start building a {get_robot_type_string(next_robot)} robot.')
          current_resources = subtract_resources(current_resources, cost)
          is_building_robot = True

      current_resources = add_resources(current_resources, current_robots)

      for resource in ResourceType:
        robot_qty = get_single_resource(current_robots, resource)

        if robot_qty > 0:
          robot_str = get_robot_type_string(resource)
          resource_qty = get_single_resource(current_resources, resource)

          print(f'{robot_qty} {robot_str} robot{"s" if robot_qty > 1 else ""} collect {robot_qty} {resource.value}; you now have {resource_qty} {resource.value}.')

      if next_robot != None and is_building_robot:
        current_robots = add_resources(current_robots, get_resource_unit_tuple(next_robot))
        is_building_robot = False

        print(f'The new {get_robot_type_string(next_robot)} is ready; you have {get_single_resource(current_robots, next_robot)} of them.')

        robot_index += 1

        if robot_index < len(self.debug_build_history):
          next_robot = self.debug_build_history[robot_index]
        else:
          next_robot = None

      print()


  def is_it_worth_to_build_robot(self, type: ResourceType) -> bool:
    time_to_build = self.time_to_build_robot[type]

    if time_to_build < 0:
      return False

    if type in self.perm_robot_blacklist:
      return False

    return time_to_build + 1 < self.remaining_time

  def elapse_time_and_build_robot(self, robot_type: ResourceType) -> bool:
    if not self.is_it_worth_to_build_robot(robot_type):
      return False

    if self.debug:
      self.debug_build_history.append(robot_type)

    time_to_elapse = self.time_to_build_robot[robot_type]

    # Time to gather the resources, and plus one to actually build the robot
    self._elapse_time(time_to_elapse + 1)

    robot_cost = self.blueprint.robot_costs[robot_type]
    self.resources = subtract_resources(self.resources, robot_cost)
    self.robots = add_resources(self.robots, get_resource_unit_tuple(robot_type))

    if robot_type != ResourceType.GEODE:
        robot_qty = self.get_robots_qty(robot_type)
        resource_blueprint_qty = get_single_resource(self.blueprint.max_cost, robot_type)

        if robot_qty >= resource_blueprint_qty:
          self.perm_robot_blacklist.add(robot_type)

    self._calculate_time_to_build_robots()

    return True

  def elapse_remaining_time(self) -> None:
    self._elapse_time(self.remaining_time)

  def _elapse_time(self, time: int) -> None:
    production = multiply_resource(self.robots, time)
    self.resources = add_resources(self.resources, production)

    self.remaining_time -= time

  def _calculate_time_to_build_robots(self) -> None:
    for type in ResourceType:
      if (
          (type == ResourceType.OBSIDIAN and self.get_robots_qty(ResourceType.CLAY) == 0)
          or (type == ResourceType.GEODE and self.get_robots_qty(ResourceType.OBSIDIAN) == 0)
          or type in self.perm_robot_blacklist
      ):
        self.time_to_build_robot[type] = -1
        continue

      cost = self.blueprint.robot_costs[type]
      most_time = 0

      match type:
        case ResourceType.ORE | ResourceType.CLAY:
          most_time = math.ceil((get_single_resource(cost, ResourceType.ORE) - self.get_resource_qty(ResourceType.ORE)) / self.get_robots_qty(ResourceType.ORE))
        case ResourceType.OBSIDIAN:
          ore_time = math.ceil((get_single_resource(cost, ResourceType.ORE) - self.get_resource_qty(ResourceType.ORE)) / self.get_robots_qty(ResourceType.ORE))
          clay_time = math.ceil((get_single_resource(cost, ResourceType.CLAY) - self.get_resource_qty(ResourceType.CLAY)) / self.get_robots_qty(ResourceType.CLAY))
          most_time = max(ore_time, clay_time)
        case ResourceType.GEODE:
          ore_time = math.ceil((get_single_resource(cost, ResourceType.ORE) - self.get_resource_qty(ResourceType.ORE)) / self.get_robots_qty(ResourceType.ORE))
          obsidian_time = math.ceil((get_single_resource(cost, ResourceType.OBSIDIAN) - self.get_resource_qty(ResourceType.OBSIDIAN)) / self.get_robots_qty(ResourceType.OBSIDIAN))
          most_time = max(ore_time, obsidian_time)

      self.time_to_build_robot[type] = most_time


# Main function
def calculate_quality_level(blueprint: Blueprint, time_limit: int) -> int:
  max_geodes_state = State(blueprint, time_limit, DEBUG_PRINT)
  max_geode_prediction = 0

  states_array = deque[State]()
  states_array.append(State(blueprint, time_limit, DEBUG_PRINT))

  # max_nodes = 0


  while len(states_array) > 0:
    current_state = states_array.popleft()

    # if len(states_array) > max_nodes:
    #   max_nodes = len(states_array)

    if current_state.remaining_time <= 0:
      if current_state.get_geodes() > max_geode_prediction:
        max_geodes_state = current_state
        max_geode_prediction = max_geodes_state.get_geodes()
    else:
      remaining_time = current_state.remaining_time
      current_geodes = current_state.get_resource_qty(ResourceType.GEODE)
      current_robots = current_state.get_robots_qty(ResourceType.GEODE)

      # Geode potential production assuming one new robor will be built each minute
      geode_potential = current_geodes + (((current_robots * 2 + remaining_time - 1) * remaining_time / 2) if remaining_time > 1 else current_robots)

      if geode_potential <= max_geode_prediction:
        # print(f'SKIPPED | MAX PREDICTION: {max_geode_prediction} | POTENTIAL: {geode_potential} | PRODUCTION: {current_state.resources} | ROBOTS: {current_state.robots} | TIME LEFT: {remaining_time}')
        continue

      no_robot_built = True

      if remaining_time > 1:
        for type in [ResourceType.ORE, ResourceType.CLAY, ResourceType.OBSIDIAN, ResourceType.GEODE]:
          if current_state.remaining_time <= 2 and type != ResourceType.GEODE:
            continue

          if current_state.is_it_worth_to_build_robot(type):
            new_state = deepcopy(current_state)

            new_state.elapse_time_and_build_robot(type)
            states_array.append(new_state)

            no_robot_built = False

            if type == ResourceType.GEODE:
              geode_prediction = new_state.get_resource_qty(type) + new_state.remaining_time * new_state.get_robots_qty(type)

              if geode_prediction > max_geode_prediction:

                max_geodes_state = new_state
                max_geode_prediction = geode_prediction

                pass


        if no_robot_built:
          current_state.elapse_remaining_time()
          states_array.append(current_state)

  if max_geodes_state.remaining_time > 0:
    max_geodes_state.elapse_remaining_time()

  if max_geodes_state.debug:
    print(f'Max geodes for blueprint {new_blueprint.id}: {max_geodes_state.get_geodes()} | Quality level: {max_geodes_state.get_geodes() * blueprint.id}\n\n')

    if max_geodes_state.get_geodes() > 0:
      max_geodes_state.print_build_history()

  # print(f'Max nodes for blueprint {new_blueprint.id}: {max_nodes}')

  return max_geodes_state.get_geodes() * blueprint.id

# Helper functions
def get_robot_type_string(type: ResourceType) -> str:
    adj = 'cracking' if type == ResourceType.GEODE else 'collecting'
    return f'{type.value}-{adj}'

def get_single_resource(res: tuple[int, int, int, int], type: ResourceType) -> int:
  match type:
    case ResourceType.ORE:
      return res[0]
    case ResourceType.CLAY:
      return res[1]
    case ResourceType.OBSIDIAN:
      return res[2]
    case ResourceType.GEODE:
      return res[3]
    case _:
      return -1

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

def multiply_resource(res: tuple[int, int, int, int], value: int) -> tuple[int, int, int, int]:
  (ore, clay, obsidian, geode) = res

  return (
    ore * value,
    clay * value,
    obsidian * value,
    geode * value
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

def can_build(resources: tuple[int, int, int, int], cost: tuple[int, int, int, int]) -> bool:
  return resources[0] >= cost[0] \
      and resources[1] >= cost[1] \
      and resources[2] >= cost[2] \
      and resources[3] >= cost[3] \


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

# Puzzle input parse
def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

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

      if DEBUG_PRINT:
        new_blueprint.print_info()

      quality_level = calculate_quality_level(new_blueprint, TIME_LIMIT)
      quality_sum += quality_level

if DEBUG_PRINT:
  print(f'Quality sum = {quality_sum}')
else:
  print(quality_sum)

print()
print(f'Execution time: {(time.time() - start_time):.2f}s')
