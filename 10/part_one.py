import os

class BaseCommand:
  def __init__(self, duration):
    self.duration = duration

  def has_finished(self):
    return self.duration == 0

  def execute(self):
    self.duration -= 1
    return self.has_finished()

class NoopCommand(BaseCommand):
  def __init__(self):
    super().__init__(1)

  def __str__(self):
    return 'noop'

class AddxCommand(BaseCommand):
  def __init__(self, value):
    super().__init__(2)
    self.value = value

  def __str__(self) -> str:
    return f'addx {self.value}'


def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

commands_list = []

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    command = line.strip()

    if command.startswith('noop'):
      commands_list.append(NoopCommand())
    elif command.startswith('addx'):
      add_value = int(command.removeprefix('addx '))
      commands_list.append(AddxCommand(add_value))

# for command in commands_list:
#   print(command)

x = 1
cycle = 0
signal_strengh_sum = 0
measure_cycles = range(20, 221, 40)

while len(commands_list) != 0:
  current_command = commands_list[0]

  # Start of the cycle
  cycle += 1

  # During the cicly
  if cycle in measure_cycles:
    signal_strengh_sum += cycle * x

  # After the cycle
  current_command.execute()

  if current_command.has_finished():
    if isinstance(current_command, AddxCommand):
      x += current_command.value

    commands_list.pop(0)

print(signal_strengh_sum)
