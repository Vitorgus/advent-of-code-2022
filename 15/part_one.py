import os
import re

def get_manhattan_distance(start, end):
  start_x, start_y = start
  end_x, end_y = end

  return abs(start_x - end_x) + abs(start_y - end_y)

class Base:
  def __init__(self, coord) -> None:
    self.coord = coord

class Beacon(Base):
  def __init__(self, coord) -> None:
    super().__init__(coord)

class Sensor(Base):
  def __init__(self, coord, closest_beacon: Beacon) -> None:
    super().__init__(coord)

    self.closest_beacon = closest_beacon
    self.distance_to_closest_beacon = get_manhattan_distance(coord, closest_beacon.coord)

class Cave:
  SENSOR_SYMBOL = 'S'
  BEACON_SYMBOL = 'B'
  NO_BEACON_SPACE_SYMBOL = '#'
  FREE_SPACE_SYMBOL = '.'

  MARGIN_LEFT = 0
  MARGIN_RIGHT = 0

  PRINT_TRESHOLD = 100000

  def __init__(self):
    self._sensor_list: list[Sensor] = []
    self._beacon_list: list[Beacon] = []

  def add_sensor(self, sensor: Sensor):
    self._sensor_list.append(sensor)
    self._beacon_list.append(sensor.closest_beacon)

  def get_cave_string(self, print_no_beacon_space=False):
    print("entering print area")
    result = ''

    min_x = None
    max_x = None
    min_y = None
    max_y = None

    for beacon in self._beacon_list:
      beacon_x, beacon_y = beacon.coord
      if min_x == None or beacon_x < min_x:
        min_x = beacon_x
      if max_x == None or beacon_x > max_x:
        max_x = beacon_x
      if min_y == None or beacon_y < min_y:
        min_y = beacon_y
      if max_y == None or beacon_y > max_y:
        max_y = beacon_y

    for sensor in self._sensor_list:
      sensor_x, sensor_y = sensor.coord
      distace = sensor.distance_to_closest_beacon

      if print_no_beacon_space:
        if min_x == None or sensor_x - distace < min_x:
          min_x = sensor_x - distace
        if max_x == None or sensor_x + distace > max_x:
          max_x = sensor_x + distace
        if min_y == None or sensor_y - distace < min_y:
          min_y = sensor_y - distace
        if max_y == None or sensor_y + distace > max_y:
          max_y = sensor_y + distace
      else:
        if min_x == None or sensor_x < min_x:
          min_x = sensor_x
        if max_x == None or sensor_x > max_x:
          max_x = sensor_x
        if min_y == None or sensor_y < min_y:
          min_y = sensor_y
        if max_y == None or sensor_y > max_y:
          max_y = sensor_y

    min_x -= Cave.MARGIN_LEFT
    max_x += Cave.MARGIN_RIGHT

    if (max_x - min_x >= Cave.PRINT_TRESHOLD
        or max_y - min_y >= Cave.PRINT_TRESHOLD):
      return f'Cave too big to transform into string. Dimensions: {max_x - min_x}, {max_y - min_y}'

    sensor_coords = [x.coord for x in self._sensor_list]
    beacon_coords = [x.coord for x in self._beacon_list]

    for coord_y in range(min_y, max_y+1):
      for coord_x in range(min_x, max_x+1):
        coord = (coord_x, coord_y)
        if coord in sensor_coords:
          result += Cave.SENSOR_SYMBOL
        elif coord in beacon_coords:
          result += Cave.BEACON_SYMBOL
        else:
          for sensor in self._sensor_list:
            symbol = Cave.FREE_SPACE_SYMBOL
            distance = get_manhattan_distance(coord, sensor.coord)

            if distance <= sensor.distance_to_closest_beacon:
              symbol = Cave.NO_BEACON_SPACE_SYMBOL
              break

          result += symbol
      result += '\n'

    return result

  def count_positions_can_not_have_beacon(self, target_y):
    positions = set()

    for sensor in self._sensor_list:
      sensor_x, sensor_y = sensor.coord
      distance = sensor.distance_to_closest_beacon

      if (sensor_y + distance >= target_y
          and sensor_y - distance <= target_y):


        """
        Values of x found by isolation x in the Manhattan distance equation:
        |x - a| + |y - b| = d

        Or, using the current variables:
        |x - sensor_x| + |sensor_y - target_y| = distance
        """

        x_coords = [
          -distance + abs(target_y - sensor_y) + sensor_x,
          distance - abs(target_y - sensor_y) + sensor_x
        ]

        x_start = min(x_coords)
        x_end = max(x_coords)

        positions = positions.union(range(x_start, x_end+1))

    sensor_coords_set = {x.coord[0] for x in self._sensor_list if x.coord[1] == target_y}
    beacon_coords_set = {x.coord[0] for x in self._beacon_list if x.coord[1] == target_y}

    positions = positions - sensor_coords_set - beacon_coords_set

    return len(positions)

  def __str__(self) -> str:
    return self.get_cave_string()


def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

DEBUG_PRINT_CAVE = False
DEBUG_SHOW_NO_BEACON_SPACES = False

TARGET_ROW = 2000000

numbers_regex = re.compile(r'[-]*\d+')

cave = Cave()

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    coords = [int(x) for x in numbers_regex.findall(line.strip())]
    sensor_x, sensor_y, beacon_x, beacon_y = coords

    sensor_coord = (sensor_x, sensor_y)
    beacon_coord = (beacon_x, beacon_y)

    beacon = Beacon(beacon_coord)
    sensor = Sensor(sensor_coord, beacon)

    cave.add_sensor(sensor)

if DEBUG_PRINT_CAVE:
  print(cave.get_cave_string(DEBUG_SHOW_NO_BEACON_SPACES))

count = cave.count_positions_can_not_have_beacon(TARGET_ROW)

if DEBUG_PRINT_CAVE:
  print(f'Positions that can\'t have the beacon at y level {TARGET_ROW}: {count}')
else:
  print(count)
