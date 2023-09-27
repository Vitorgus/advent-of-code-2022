import os
from functools import cmp_to_key

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

def parse_packet(packet: str):
  if packet.isdecimal():
    # Number
    return int(packet)
  else:
    # List
    element = ''
    bracket_count = 0
    parsed_packet = []

    if packet == '[]':
      pass

    for char in packet:
      if char == '[':
        bracket_count += 1
        if bracket_count > 1:
          element += char
      elif char == ']':
        if bracket_count > 1:
          element += char
        else:
          if element != '':
            parsed_element = parse_packet(element)
            parsed_packet.append(parsed_element)
            element = ''
        bracket_count -= 1
      elif char == ',' and bracket_count == 1:
        if element != '':
          parsed_element = parse_packet(element)
          parsed_packet.append(parsed_element)
          element = ''
      else:
        element += char

    return parsed_packet

def compare_packets(left, right, print_debug=False, depth=0):
  if print_debug:
    print('  ' * depth, end='')
    print(f'- Compare {left} vs {right}')

  if isinstance(left, int) and isinstance(right, int):
    if left < right:
      if print_debug:
        print('  ' * (depth+1), end='')
        print('- Left side is smaller, so inputs are in the right order')
      return -1
    elif left > right:
      if print_debug:
        print('  ' * (depth+1), end='')
        print('- Right side is smaller, so inputs are NOT in the right order')
      return 1
    else:
      return 0
  elif isinstance(left, list) and isinstance(right, list):
    for i in range(min(len(left), len(right))):
      result = compare_packets(left[i], right[i], print_debug, depth+1)

      if result != 0:
        return result

    if len(left) < len(right):
      if print_debug:
        print('  ' * (depth+1), end='')
        print('- Left side ran out of items, so inputs are in the right order')
      return -1
    elif len(left) > len(right):
      if print_debug:
        print('  ' * (depth+1), end='')
        print('- Right side ran out of items, so inputs are NOT in the right order')
      return 1
    else:
      return 0
  else:
    left_array = left
    right_array = right

    if isinstance(left, int):
      left_array = [left]
      if print_debug:
        print('  ' * (depth+1), end='')
        print(f'- Mixed types; convert left to {left_array} and retry comparison')
    if isinstance(right, int):
      right_array = [right]
      if print_debug:
        print('  ' * (depth+1), end='')
        print(f'- Mixed types; convert right to {right_array} and retry comparison')

    return compare_packets(left_array, right_array, print_debug, depth+1)

DIVIDER_PACKETS = [[[2]], [[6]]]

PRINT_COMPARISON_DEBUG = False
PRINT_ORDERED_PACKETS_DEBUG = False

packets = DIVIDER_PACKETS.copy()

with open(get_filepath("example.txt"), encoding="utf-8") as f:

  for line in f:
    l_strip = line.strip()

    if l_strip != '':
      packet = parse_packet(l_strip)
      packets.append(packet)

packets.sort(key=cmp_to_key(lambda x, y: compare_packets(x, y, PRINT_COMPARISON_DEBUG)))

if PRINT_ORDERED_PACKETS_DEBUG:
  for packet in packets:
    print(packet)

decoder_key = 1

for divider in DIVIDER_PACKETS:
  index = packets.index(divider)
  decoder_key *= index + 1

if PRINT_COMPARISON_DEBUG or PRINT_ORDERED_PACKETS_DEBUG:
  print()
  print(f'Decoder key value: {decoder_key}')
else:
  print(decoder_key)
