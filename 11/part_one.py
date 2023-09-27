import os


class Monkey:
  RELIEF_DAMPENER = 3

  def __init__(self, id) -> None:
    self.id = id
    self.items = []
    self.operation = ''
    self.test_number = 0
    self.test_true_destination = -1
    self.test_false_destination = -1
    self.inspect_count = 0

  def add_item(self, item) -> None:
    self.items.append(item)

  def execute_operation(self, item, debug=False):
    if '+' in self.operation:
      # Add operation
      if debug:
        print('    Worry level increases', end=' ')
      op_terms = self.operation.split(' + ')

      first_term = item if op_terms[0] == 'old' else int(op_terms[0])
      second_term = item if op_terms[1] == 'old' else int(op_terms[1])

      if debug:
        if op_terms[1] == 'old':
          print('by itself', end=' ')
        else:
          print(f'by {second_term}', end=' ')

      result = first_term + second_term

      if debug:
        print(f'to {result}', )

      return result
    elif '*' in self.operation:
      # multiply operation
      if debug:
        print('    Worry level is multiplied', end=' ')
      op_terms = self.operation.split(' * ')

      first_term = item if op_terms[0] == 'old' else int(op_terms[0])
      second_term = item if op_terms[1] == 'old' else int(op_terms[1])

      if debug:
        if op_terms[1] == 'old':
          print('by itself', end=' ')
        else:
          print(f'by {second_term}', end=' ')

      result = first_term * second_term

      if debug:
        print(f'to {result}', )

      return result

  def relief_dampener(self, item, debug=False):
    result = item // self.RELIEF_DAMPENER

    if debug:
      print(f'    Monkey gets bored with item. Worry level is divided by {self.RELIEF_DAMPENER} to {result}')

    return result

  def get_throw_destination(self, item, debug=False):
    if item % self.test_number == 0:
      if debug:
        print(f'    Current worry level is divisible by {self.test_number}')

      return self.test_true_destination
    else:
      if debug:
        print(f'    Current worry level is divisible by {self.test_number}')

      return self.test_false_destination

  def inspect_and_trow_item(self,  debug=False):
    if len(self.items) == 0:
      return

    item = self.items.pop(0)
    self.inspect_count += 1
    if debug:
      print(f'  Monkey {self.id} inspects an item with worry level {item}')

    item = self.execute_operation(item, debug)
    item = self.relief_dampener(item, debug)

    destination = self.get_throw_destination(item)

    if debug:
      print(f'    Item with worry level {item} is thrown to monkey {destination}')

    return (item, destination)

def get_monkey(monkey_list, monkey_id):
  for monkey in monkey_list:
    if monkey.id == monkey_id:
      return monkey

  return None

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

monkey_list = []
current_monkey = None

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    l_strip = line.strip()

    if l_strip.startswith('Monkey'):
      monkey_id = int(l_strip.removeprefix('Monkey ').replace(':', ''))
      current_monkey = Monkey(monkey_id)
      monkey_list.append(current_monkey)
    elif l_strip.startswith('Starting items'):
      items_list = l_strip.removeprefix('Starting items: ').replace(',', '').split()

      for item in items_list:
        current_monkey.add_item(int(item))
    elif l_strip.startswith('Operation'):
      operation = l_strip.removeprefix('Operation: new = ')
      current_monkey.operation = operation
    elif l_strip.startswith('Test'):
      test_number = int(l_strip.removeprefix('Test: divisible by '))
      current_monkey.test_number = test_number
    elif l_strip.startswith('If true'):
      test_true_destination = int(l_strip.removeprefix('If true: throw to monkey '))
      current_monkey.test_true_destination = test_true_destination
    elif l_strip.startswith('If false'):
      test_false_destination = int(l_strip.removeprefix('If false: throw to monkey '))
      current_monkey.test_false_destination = test_false_destination

NUMBER_ROUNDS = 20
MOST_ACTIVE_NUMBERS = 2

DEBUG_STEP_BY_STEP = False
DEBUG_ROUND_ITEMS = False
DEBUG_INSPECT_COUNTS = False

for round in range(NUMBER_ROUNDS):
  if DEBUG_STEP_BY_STEP:
    print(f'--- Round {round} ---')

  for monkey in monkey_list:
    if DEBUG_STEP_BY_STEP:
      print(f'Monkey {monkey.id}:')

    while len(monkey.items) > 0:
      item, target = monkey.inspect_and_trow_item(DEBUG_STEP_BY_STEP)
      target_monkey = get_monkey(monkey_list, target)

      if target_monkey is not None:
        target_monkey.add_item(item)

  if DEBUG_STEP_BY_STEP:
      print()

  if DEBUG_ROUND_ITEMS:
    print(f'After round {round + 1}, the monkeys are holding items with these worry levels:')

    for monkey in monkey_list:
      print(f'Monkey {monkey.id}:', end=' ')

      for i in range(len(monkey.items)):
        print(monkey.items[i], end='')

        if i != len(monkey.items) - 1:
          print(', ', end='')
      print()
    print()

if DEBUG_INSPECT_COUNTS:
  print(f'After all {NUMBER_ROUNDS} rounds:')
  for monkey in monkey_list:
    print(f'Monkey {monkey.id} inspected items {monkey.inspect_count} times')
  print()

inspect_counts = sorted([monkey.inspect_count for monkey in monkey_list], reverse=True)
monkey_business = 1

for i in range(MOST_ACTIVE_NUMBERS):
  monkey_business *= inspect_counts[i]

if DEBUG_STEP_BY_STEP or DEBUG_ROUND_ITEMS or DEBUG_INSPECT_COUNTS:
  print(f'Monkey business value: {monkey_business}')
else:
  print(monkey_business)
