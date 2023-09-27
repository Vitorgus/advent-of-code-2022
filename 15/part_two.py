import os
import re
from collections import deque

def get_manhattan_distance(start, end):
  start_x, start_y = start
  end_x, end_y = end

  return abs(start_x - end_x) + abs(start_y - end_y)

def get_tuning_frequency(coord):
  coord_x, coord_y = coord
  return (coord_x * 4000000) + coord_y


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

  def is_in_range(self, coord):
    distance = get_manhattan_distance(self.coord, coord)

    return distance <= self.distance_to_closest_beacon


class Area:
  def __init__(self, start_coord, end_coord) -> None:
    self.start = start_coord
    self.end = end_coord

  def get_boundary_points(self):
    if self.is_a_point():
      return [self.start]

    start_x, start_y = self.start
    end_x, end_y = self.end

    return [
      self.start,
      (end_x, start_y),
      (start_x, end_y),
      self.end
    ]

  def is_a_point(self):
    return self.start == self.end

  def get_quadrants(self):
    start_x, start_y = self.start
    end_x, end_y = self.end

    diff_x = end_x - start_x
    diff_y = end_y - start_y

    if diff_x > 0 and diff_y > 0:
      # Area is not a line, can be divided in four
      middle_x = start_x + (diff_x // 2)
      middle_y = start_y + (diff_y // 2)

      return [
        Area(self.start, (middle_x, middle_y)),
        Area((middle_x+1, start_y), (end_x, middle_y)),
        Area((start_x, middle_y+1), (middle_x, end_y)),
        Area((middle_x+1, middle_y+1), self.end)
      ]
    elif diff_x <= 0 and diff_y > 0:
      # Area is a vertical line, divide in two
      middle_y = start_y + (diff_y // 2)

      return [
        Area(self.start, (start_x, middle_y)),
        Area((start_x, middle_y+1), self.end)
      ]
    elif diff_x > 0 and diff_y <= 0:
      # Area is a horizontal line, divide in two
      middle_x = start_x + (diff_x // 2)

      return [
        Area(self.start, (middle_x, start_y)),
        Area((middle_x+1, start_y), self.end)
      ]
    else:
      # Point, cannot be divided
      return []

  def __str__(self) -> str:
    if self.is_a_point():
      return f'Point {self.start}'
    else:
      return f'Area starts at {self.start} and ends at {self.end}'


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

  def get_cave_string(self, area=None, print_no_beacon_space=False):
    print("entering print area")
    result = ''


    min_x = None
    max_x = None
    min_y = None
    max_y = None

    if area != None:
      start_x, start_y = area.start
      end_x, end_y = area.end

      min_x = start_x
      min_y = start_y
      max_x = end_x
      max_y = end_y
    else:
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
          if print_no_beacon_space:
            for sensor in self._sensor_list:
              symbol = Cave.FREE_SPACE_SYMBOL
              distance = get_manhattan_distance(coord, sensor.coord)

              if distance <= sensor.distance_to_closest_beacon:
                symbol = Cave.NO_BEACON_SPACE_SYMBOL
                break

            result += symbol
          else:
            result += Cave.FREE_SPACE_SYMBOL
      result += '\n'

    return result

  def find_missing_beacon(self, area: Area):
    """
    The idea here is to keep dividing the ares until you reach the beacon
    You get an area, and see if it exists completely inside a beacon's range
    If it does: discard that area
    If not: subdivide that area, and do the same process to the divisions
    """

    search_areas = deque([area])

    while len(search_areas) > 0:
      current_area = search_areas.popleft()

      is_inside_a_sensor = False
      touches_a_sensor = False

      for sensor in self._sensor_list:
        is_inside_this_sensor = True

        for coord in current_area.get_boundary_points():
          if sensor.is_in_range(coord):
            touches_a_sensor = True
          else:
            is_inside_this_sensor = False

        if is_inside_this_sensor:
          is_inside_a_sensor = True
          break

      if is_inside_a_sensor:
        # Discards the area
        pass
      elif touches_a_sensor:
        # The area touches a sensor, divide it and search the divisions
        quadrants = current_area.get_quadrants()
        search_areas.extend(quadrants)
      else:
        # Area does not touch any sensor, might be the beacon
        if current_area.is_a_point():
          return current_area.start


    return None

  def __str__(self) -> str:
    return self.get_cave_string()


def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

DEBUG_PRINT_CAVE = False
DEBUG_SHOW_NO_BEACON_SPACES = False

LIMIT_X = 4000000
LIMIT_Y = 4000000

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

search_area = Area((0, 0), (LIMIT_X, LIMIT_Y))

if DEBUG_PRINT_CAVE:
  print(cave.get_cave_string(search_area, DEBUG_SHOW_NO_BEACON_SPACES))

beacon_coord = cave.find_missing_beacon(search_area)

if beacon_coord:
  frequency = get_tuning_frequency(beacon_coord)

  if DEBUG_PRINT_CAVE:
    print(f'Missing beacon tuning frequency: {frequency}')
  else:
    print(get_tuning_frequency(beacon_coord))
else:
  print('Beacon not found')
