import os
import time
from collections import deque

start_time = time.time()


# Puzzle inputs and settings
FILE_NAME = "input.txt"
DEBUG_PRINT = False


# Classes
class Node:
  def __init__(self, data: int) -> None:
    self.data = data
    self.next: Node = self
    self.prev: Node = self

class CustomList:
  def __init__(self, debug: bool = False) -> None:
    self.debug = debug
    self.size: int = 0
    self.first: Node = Node(-1)
    self.zero: Node | None = None

  def __str__(self) -> str:
    result = ''

    aux = self.first

    for i in range(self.size):
      if i > 0:
        result += ', '
      result += str(aux.data)
      aux = aux.next

    return result

  def append(self, data: int) -> None:
    node = None

    match self.size:
      case 0:
        self.first.data = data
        node = self.first
      case 1:
        node = Node(data)
        first = self.first

        first.next = node
        first.prev = node
        node.next = first
        node.prev = first
      case _:
        node = Node(data)
        first = self.first

        aux = self.first.prev
        first.prev = node
        node.next = first
        aux.next = node
        node.prev = aux

    self.size += 1

    if data == 0:
      self.zero = node

  def mix(self) -> None:
    node_queue = deque[Node]()

    aux = self.first

    if aux.next == self.first:
      return

    while aux.next != self.first:
      node_queue.append(aux)
      aux = aux.next

    node_queue.append(aux)

    if self.debug:
      print('Initial arrangement:')
      print(self)
      print()

    while len(node_queue) > 0:
      node = node_queue.popleft()
      aux = node.prev

      # Remove the node and all it's references
      if node == self.first:
        self.first = node.next

      node.prev.next = node.next
      node.next.prev = node.prev
      node.next = node
      node.prev = node

      # calculate how much to move
      counter = node.data % (self.size - 1)
      clockwise = True

      if counter > node.data // 2:
        counter = self.size - 1 - counter
        clockwise = False

      while counter > 0:
        aux = aux.next if clockwise else aux.prev
        counter -= 1

      # Add node in new position
      aux.next.prev = node
      node.next = aux.next
      aux.next = node
      node.prev = aux

      if self.debug:
        print(f'{node.data} moves between {node.prev.data} and {node.next.data}:')
        print(self)
        print()

  def get_coord_sum(self) -> int:
    if self.zero == None:
      return -1

    sum = 0

    for i in [1000, 2000, 3000]:
      aux = self.zero

      counter = i % self.size
      clockwise = True

      if counter > i // 2:
        counter = self.size - counter
        clockwise = False

      while counter > 0:
        aux = aux.next if clockwise else aux.prev
        counter -= 1

      sum += aux.data

    return sum


# Helper funcions
def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

# Puzzle input parse
node_list = CustomList(DEBUG_PRINT)

with open(get_filepath(FILE_NAME), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip != "":
      data = int(l_strip)
      node_list.append(data)

node_list.mix()
print(node_list.get_coord_sum())

print()
print(f'Execution time: {(time.time() - start_time):.2f}s')
