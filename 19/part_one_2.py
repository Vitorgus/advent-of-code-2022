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
FILE_NAME = "input.txt"
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

    print()


class State:
  def __init__(self, blueprint: Blueprint, debug: bool = False) -> None:
    self.blueprint = blueprint
    self.debug = debug

    self.time = 0
    self.resources: tuple[int, int, int, int] = (0, 0, 0, 0)
    self.robots: tuple[int, int, int, int] = (1, 0, 0, 0)
    self.current_building_robot: ResourceType | None = None
    self.log = ''

    self.robot_blacklist = set[ResourceType]()

  def get_geodes(self) -> int:
    return self.get_resources(ResourceType.GEODE)

  def get_robots(self, type: ResourceType) -> int:
    match type:
      case ResourceType.ORE:
        return self.robots[0]
      case ResourceType.CLAY:
        return self.robots[1]
      case ResourceType.OBSIDIAN:
        return self.robots[2]
      case ResourceType.GEODE:
        return self.robots[3]
      case _:
        return 0

  def get_resources(self, type: ResourceType) -> int:
    match type:
      case ResourceType.ORE:
        return self.resources[0]
      case ResourceType.CLAY:
        return self.resources[1]
      case ResourceType.OBSIDIAN:
        return self.resources[2]
      case ResourceType.GEODE:
        return self.resources[3]
      case _:
        return 0

  def add_to_blacklist(self, type: ResourceType) -> None:
    self.robot_blacklist.add(type)

  def clear_blacklist(self) -> None:
    self.robot_blacklist.clear()

  def can_build_robot(self, type: ResourceType) -> bool:
    costs = self.blueprint.robot_costs[type]

    if type in self.robot_blacklist:
      return False

    for resource_index in range(len(costs)):
      if self.resources[resource_index] < costs[resource_index]:
        return False

    return True

  def start_building_robot(self, type: ResourceType) -> None:
    # ALERT: estou assumindo que só é possível fazer um único robô por vez
    if self.current_building_robot != None:
      self.log += f'ERROR: already building robot of type {self.current_building_robot.value}. Robot will be ovewritten.\n'
    self.current_building_robot = type

    costs = self.blueprint.robot_costs[type]
    self.resources = subtract_resources(self.resources, costs)

    if self.debug:
      self.log += f'Spend {resource_to_string(costs)} to start building a {get_robot_type_string(type)} robot.\n'

  def finish_building_robot(self) -> None:
    # ALERT: estou assumindo que só é possível fazer um único robô por vez
    if self.current_building_robot == None:
      return

    self.robots = add_resources(self.robots, get_resource_unit_tuple(self.current_building_robot))

    if self.debug:
      self.log += f'The new {get_robot_type_string(self.current_building_robot)} robot is ready; you now have {self.get_robots(self.current_building_robot)} of them.\n'

    self.current_building_robot = None

  def elapse_time(self) -> None:
    self.time += 1

    if self.debug:
      if self.time > 1:
        self.log += '\n'

      self.log += f'== Minute {self.time} ==\n'

  def execute_robots_functions(self) -> None:
    self.resources = add_resources(self.resources, self.robots)

    if self.debug:
      for resource in [ResourceType.ORE, ResourceType.CLAY, ResourceType.OBSIDIAN, ResourceType.GEODE]:
        robots_number = self.get_robots(resource)

        if robots_number > 0:
          action = 'crack' if resource == ResourceType.GEODE else 'collect'
          action += 's' if robots_number > 1 else ''

          current_resource_number = self.get_resources(resource)
          final_resource_str = f'open {resource.value}' if resource == ResourceType.GEODE else f'{resource.value}'

          self.log += f'{robots_number} {resource.value}-{action}ing robot {action} {robots_number} {resource.value}; you now have {current_resource_number} {final_resource_str}.\n'


# Main function
def calculate_quality_level(blueprint: Blueprint, time_limit: int) -> int:
  max_geodes_state = State(blueprint, DEBUG_PRINT)
  current_time = 0
  cutoff_resource_type = ResourceType.OBSIDIAN
  was_cutoff_robot_built = False
  number_of_cutoff_robots = 0

  states_array = deque[State]()
  states_array.append(State(blueprint, DEBUG_PRINT))


  # começar while loop de enquanto ainda tem estado na fila
  while len(states_array) > 0:
    # print(f'states len = {len(states_array)} | current time = {current_time}')
    current_state = states_array.popleft()

    # se o tempo do estado for maior que o current time da função:
    if current_state.time > current_time:
      # se alguém construiu um robô de geodo, tira TODOS os estados que não construíram um robô de geodo
      if was_cutoff_robot_built:
        current_states_len = len(states_array)

        for _ in range(current_states_len):
          state = states_array.popleft()

          if state.get_robots(cutoff_resource_type) >= number_of_cutoff_robots:
            states_array.append(state)

        if current_state.get_robots(cutoff_resource_type) < number_of_cutoff_robots:
          continue
      # atualiza o current time e o check se algué construiu robô de geodo.
      current_time = current_state.time
      was_cutoff_robot_built = False
      number_of_cutoff_robots = 0

    # se o estado chegou chegou no tempo...
    if current_state.time >= time_limit:
      # verificar se o número de geodos é maior do que o máximo
      if current_state.get_geodes() > max_geodes_state.get_geodes():
        #  se sim, bots na variável
        max_geodes_state = current_state
    else:
      # senão chegou no final do tempo:
      # - ver se é possível fazer robo de geodo; se SIM, fazer ele, colocar novo estado na fila, e só
        # - senão, ver se é possível fazer os outros robôs, se SIM, cria o robô, passa o tempo e bota na fila
      blacklist = []

      for type in [ResourceType.ORE, ResourceType.CLAY, ResourceType.OBSIDIAN, ResourceType.GEODE]:
        if current_state.can_build_robot(type):
          new_state = deepcopy(current_state)

          new_state.elapse_time()
          new_state.start_building_robot(type)
          new_state.execute_robots_functions()
          new_state.finish_building_robot()
          new_state.clear_blacklist()

          states_array.append(new_state)
          blacklist.append(type)

          if type == ResourceType.GEODE:
            cutoff_resource_type = ResourceType.GEODE

          if type == cutoff_resource_type:
            was_cutoff_robot_built = True
            number_of_cutoff_robots = new_state.get_robots(type)
            continue

      # - depois, faz sem criar nenhum robô
      new_state = deepcopy(current_state)

      for type in blacklist:
        new_state.add_to_blacklist(type)

      new_state.elapse_time()
      new_state.execute_robots_functions()

      states_array.append(new_state)

  if max_geodes_state.debug:
    print(max_geodes_state.log)

    print(f'Max geodes for blueprint {new_blueprint.id}: {max_geodes_state.get_geodes()} | Quality level: {max_geodes_state.get_geodes() * blueprint.id}\n')

  # no final do while, returnar o máximo de geodos multiplicado pelo id
  return max_geodes_state.get_geodes() * blueprint.id

# Helper functions
def get_robot_type_string(type: ResourceType) -> str:
    adj = 'cracking' if type == ResourceType.GEODE else 'collecting'
    return f'{type.value}-{adj}'

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
  print()
  print(f'Execution time: {time.time() - start_time}')
else:
  print(quality_sum)
