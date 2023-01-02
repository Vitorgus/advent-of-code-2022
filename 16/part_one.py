import os
import re

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)


class Valve:
  def __init__(self, name, flow) -> None:
    self.name = name
    self.flow = flow
    self.connections: list[str] = []
    self.is_open = False
  
  def add_connection(self, name):
    self.connections.append(name)
  
  def has_connection(self, name):
    return name in self.connections
  
  def open(self):
    self.is_open = True
  
  def close(self):
    self.is_open = False
  
  def __str__(self) -> str:
    return self.name

class Cave:
  def __init__(self) -> None:
    self.valves: list[Valve] = []
  
  def add_valve(self, name, flow):
    valve = Valve(name, flow)
    self.valves.append(valve)
  
  def get_valve(self, name):
    for valve in self.valves:
      if valve.name == name:
        return valve
    
    return None
  
  def add_connection(self, name_from, name_to):
    valve = self.get_valve(name_from)

    if valve != None:
      valve.add_connection(name_to)
  
  def get_open_valves(self):
    return [valve for valve in self.valves if valve.is_open]
  
  def has_closed_working_valves(self):
    for valve in self.valves:
      if valve.flow > 0 and not valve.is_open:
        return True
    
    return False
  
  def get_closed_working_valves(self):
    return [x for x in self.valves if x.flow > 0 and not x.is_open]
  
  def get_current_pressure(self):
    valves = self.get_open_valves()
    pressure = 0

    for valve in valves:
      pressure += valve.flow
    
    return pressure

def get_min_paths(cave: Cave, start_valve_name: str):
  # Calculate min distance from a node using Dijkstra's algorithm
  valves_to_explore = [start_valve_name]
  valves_explored = []

  min_paths = { start_valve_name: [] }

  while len(valves_to_explore) > 0:
    valve_name = min(valves_to_explore, key=lambda x: len(min_paths[x]))
    valve = cave.get_valve(valve_name)

    valves_to_explore.remove(valve_name)
    valves_explored.append(valve_name)

    for next_valve_name in valve.connections:
      if next_valve_name in valves_explored:
        continue

      current_path = min_paths[valve_name] + [next_valve_name]

      if next_valve_name in valves_to_explore:
        if len(current_path) < len(min_paths[next_valve_name]):
          min_paths[next_valve_name] = current_path
      else:
        valves_to_explore.append(next_valve_name)
        min_paths[next_valve_name] = current_path
  
  return min_paths

def get_all_min_paths(cave: Cave):
  # Get the min distance to all nodes
  all_min_paths = {}

  for valve in cave.valves:
    valve_name = valve.name
    all_min_paths[valve_name] = get_min_paths(cave, valve_name)
  
  return all_min_paths

DEBUG_PRINT = False

VALVE_NAME_AND_FLOW_PATTERN = 'Valve (\w+) has flow rate=(\d+)'
VALVE_START = 'AA'
TIME_TO_OPEN_VALVE = 1
TOTAL_TIME = 30

cave = Cave()

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  for line in f:
    part_1, part_2 = [s.strip() for s in line.split(';')]

    part_1_info = re.fullmatch(VALVE_NAME_AND_FLOW_PATTERN, part_1).groups()
    valve_name = part_1_info[0]
    valve_flow = int(part_1_info[1])

    cave.add_valve(valve_name, valve_flow)

    valve_connections = []
    if 'valves' in part_2:
      valve_connections = part_2.removeprefix('tunnels lead to valves ').split(', ')
    else:
      valve_connections = part_2.removeprefix('tunnel leads to valve ').split(', ')
    
    for connection in valve_connections:
      cave.add_connection(valve_name, connection)

all_min_paths = get_all_min_paths(cave)

def get_max_pressure(cave: Cave, current_valve: Valve, time: int) -> tuple[int, list[list[str]]]:
  if time <= 0 or not cave.has_closed_working_valves():
    return (0, [])

  remaining_time = time
  possible_valves = cave.get_closed_working_valves()
  min_path = all_min_paths[current_valve.name]
  
  total_pressure = 0
  steps = []

  for next_valve in possible_valves:
    next_valve.open()

    remaining_time = time - len(min_path[next_valve.name]) - TIME_TO_OPEN_VALVE
    next_valve_pressure = next_valve.flow * remaining_time

    next_max_pressure, next_max_steps = get_max_pressure(cave, next_valve, remaining_time)
    possible_total_pressure = next_valve_pressure + next_max_pressure

    if possible_total_pressure > total_pressure:
      total_pressure = possible_total_pressure
      steps = [min_path[next_valve.name]] + next_max_steps
    
    next_valve.close()

  return (total_pressure, steps)

start_valve = cave.get_valve(VALVE_START)

pressure, steps = get_max_pressure(cave, start_valve, TOTAL_TIME)

if DEBUG_PRINT:
  current_step = steps.pop(0)
  target_valve = current_step[-1]

  for minute in range(1, TOTAL_TIME+1):
    print(f'== Minute {minute} ==')

    open_valves = cave.get_open_valves()
    current_pressure = cave.get_current_pressure()
    if len(open_valves) == 0:
      print('No valves are open')
    elif len(open_valves) == 1:
      print(f'Valve {open_valves[0]} is open, releasing {current_pressure} pressure')
    else:
      valves_string = ''
      for valve in open_valves[:-2]:
        valves_string += f'{valve}, '
      valves_string += f'{open_valves[-2]} and {open_valves[-1]}'
      print(f'Valves {valves_string} are open, releasing {current_pressure} pressure.')
    
    if len(current_step) > 0:
      current_valve = current_step.pop(0)
      print(f'You move to valve {current_valve}')
    elif target_valve != None:
      cave.get_valve(target_valve).open()
      print(f'You open valve {target_valve}')
      if len(steps) > 0:
        current_step = steps.pop(0)
        target_valve = current_step[-1]
      else:
        target_valve = None
    
    print()
  
  print(f'Maximum pressure: {pressure}')
else:
  print(pressure)
