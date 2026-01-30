import os
import re
import math
import time
from enum import Enum
from collections import deque
from copy import deepcopy
from functools import total_ordering

start_time = time.time()

# Puzzle inputs and settings
FILE_NAME = "input.txt"
DEBUG_PRINT = True
TIME_LIMIT = 24

class ResourceType(Enum):
  ORE = 'ore'
  CLAY = 'clay'
  OBSIDIAN = 'obsidian'
  GEODE = 'geode'

@total_ordering
class ResourceList:
  # TODO juro que transofrmar isso num tipo de dict salva minha vida.
  # Inclusive acho que já fiz em algum desafio anterior
  def __init__(self, ore=0, clay=0, obsidian=0, geode=0) -> None:
    self.ore = ore
    self.clay = clay
    self.obsidian = obsidian
    self.geode = geode

  def __getitem__(self, key) -> int:
    if key == ResourceType.ORE or key == 'ore':
      return self.ore
    elif key == ResourceType.CLAY or key == 'clay':
      return self.clay
    elif key == ResourceType.OBSIDIAN or key == 'obsidian':
      return self.obsidian
    elif key == ResourceType.GEODE or key == 'geode':
      return self.geode
    else:
      raise KeyError

  def __add__(self, other):
    if not isinstance(other, ResourceList):
      raise NotImplemented

    return ResourceList(self.ore+other.ore,
                     self.clay+other.clay,
                     self.obsidian+other.obsidian,
                     self.geode+other.geode)

  def __sub__(self, other):
    if not isinstance(other, ResourceList):
      raise NotImplemented

    return ResourceList(self.ore-other.ore,
                     self.clay-other.clay,
                     self.obsidian-other.obsidian,
                     self.geode-other.geode)

  def __eq__(self, other) -> bool:
    if not isinstance(other, ResourceList):
      return NotImplemented

    return self.ore == other.ore \
        and self.clay == other.clay \
        and self.obsidian == other.obsidian

  def __gt__(self, other) -> bool:
    if not isinstance(other, ResourceList):
      return NotImplemented

    return self.ore >= other.ore \
        and self.clay >= other.clay \
        and self.obsidian >= other.obsidian

  def __str__(self) -> str:
    value = ''

    if self.ore > 0:
      value += f'{self.ore} ore'
    if self.clay > 0:
      if value != '':
        value += ' and '
      value += f'{self.clay} clay'
    if self.obsidian > 0:
      if value != '':
        value += ' and '
      value += f'{self.obsidian} obsidian'
    if self.geode > 0:
      if value != '':
        value += ' and '
      value += f'{self.geode} geode'

    return value if value != '' else 'no resources'

class State:
  def __init__(self) -> None:
    self.time = 0
    self.resources = ResourceList()
    self.robots = {
      ResourceType.ORE: 1,
      ResourceType.CLAY: 0,
      ResourceType.OBSIDIAN: 0,
      ResourceType.GEODE: 0
    }
    self.robot_build_order = []

  def estimate_production(self, time = 0) -> ResourceList:
    if time <= 0:
      return ResourceList()

    ore_production = self.robots[ResourceType.ORE] * time
    clay_production = self.robots[ResourceType.CLAY] * time
    obsidian_production = self.robots[ResourceType.OBSIDIAN] * time
    geode_production = self.robots[ResourceType.GEODE] * time

    return ResourceList(ore_production,
                     clay_production,
                     obsidian_production,
                     geode_production)

  def pass_time(self, time = 0) -> None:
    if time <= 0:
      return

    production = self.estimate_production(time)
    self.resources += production
    self.time += time

    if self.time > TIME_LIMIT:
      raise Exception(f'LIMIT: current time = {self.time}')

  def pass_remaining_time(self) -> None:
    remaining_time = TIME_LIMIT - self.time
    self.pass_time(remaining_time)

  def build_robot(self, robot_type: ResourceType, robot_cost: ResourceList) -> None:
    if self.resources < robot_cost:
      raise Exception('Cannot build robot')

    self.pass_time(1)
    self.resources -= robot_cost
    self.robots[robot_type] += 1
    self.robot_build_order.append(robot_type)

  def print_info(self) -> None:
    print(f'Time elapsed: {self.time}')
    print(f'Resources: {self.resources}')
    print(f'Robots: {self.robots}')
    print(f'Build order: {self.robot_build_order}')


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
    self.max_geodes_possible = 0
    self.robot_costs = {
      ResourceType.ORE: ResourceList(ore_robot_ore_cost),
      ResourceType.CLAY: ResourceList(clay_robot_ore_cost),
      ResourceType.OBSIDIAN: ResourceList(obsidian_robot_ore_cost, obsidian_robot_clay_cost),
      ResourceType.GEODE: ResourceList(geode_robot_ore_cost, 0, geode_robot_obsidian_cost)
    }

  # Check if it's possible to build said robot on time
  def is_possible_to_build(self, robot_type: ResourceType, state: State) -> bool:
    remaining_time = TIME_LIMIT - state.time - 1

    # It's not zero because it takes one time to build the robot
    if remaining_time <= 0:
      return False

    robot_costs = self.robot_costs[robot_type]
    possible_production = state.estimate_production(remaining_time)

    return possible_production >= robot_costs

  def should_build(self, robot_type: ResourceType, state: State) -> bool:
    if robot_type == ResourceType.GEODE:
      return True

    # Return false if there are already enough robots to build literally any robot in one minute
    needs_more_robots = False
    for cost in self.robot_costs.values():
      if cost[robot_type] > state.robots[robot_type]:
        return True

    return False

  def time_to_build(self, robot_type: ResourceType, state: State) -> int:
    time_to_pass = 0

    cost_list = self.robot_costs[robot_type]
    for resource in state.robots:
      # check if you have robot available
      # And check if you don't already have the available resources
      qty_needed = cost_list[resource] - state.resources[resource]
      if qty_needed > 0:
        if state.robots[resource] <= 0:
          return math.inf

        time_needed_to_produce = math.ceil(qty_needed/state.robots[resource])
        if time_needed_to_produce > time_to_pass:
          time_to_pass = time_needed_to_produce

    return time_to_pass

  def pass_time_and_build(self, robot_type_to_build: ResourceType, state: State) -> State:
    # should make new robot and pass the time

    # Calculate needed time to acquire robot
    time_to_pass = self.time_to_build(robot_type_to_build, state)

    if time_to_pass + state.time > TIME_LIMIT:
      raise Exception('OUT OF TIME')

    # Pass said time and product
    new_state = deepcopy(state)
    new_state.pass_time(time_to_pass)
    new_state.build_robot(robot_type_to_build, self.robot_costs[robot_type_to_build])

    return new_state

  def calculate_max_geodes_possible(self, debug=False) -> None:
    self.max_geodes_possible = 0

    possible_states: deque[State] = deque()
    possible_states.append(State())

    final_state = None

    while (len(possible_states) > 0):
      current_state = possible_states.popleft()

      no_robot_to_build = True

      for robot in self.robot_costs:
        if self.is_possible_to_build(robot, current_state):
          if self.should_build(robot, current_state):
            no_robot_to_build = False
            new_state = self.pass_time_and_build(robot, current_state)
            possible_states.append(new_state)

      # Add final state, when you can't build any more robots due to time limit
      if no_robot_to_build:
        current_state.pass_remaining_time()

        if current_state.resources.geode > self.max_geodes_possible:
          self.max_geodes_possible = current_state.resources.geode
          final_state = current_state

  def get_quality_level(self, debug=False) -> int:
    if self.max_geodes_possible == 0:
      self.calculate_max_geodes_possible(debug)

    return self.id * self.max_geodes_possible

  def print_info(self) -> None:
    print(f'Blueprint ID: {self.id}')

    for key in self.robot_costs:
      print(f'\t{key.value} robot costs: {self.robot_costs[key]}')


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
      quality_sum += new_blueprint.get_quality_level()
      print(f'Quality Level: {new_blueprint.get_quality_level(DEBUG_PRINT)}')
      print()

print(quality_sum)
print()
print(f'Execution time: {time.time() - start_time}')
