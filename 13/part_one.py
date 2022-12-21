import os

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
      return True
    elif left > right:
      if print_debug:
        print('  ' * (depth+1), end='')
        print('- Right side is smaller, so inputs are NOT in the right order')
      return False
    else:
      return None
  elif isinstance(left, list) and isinstance(right, list):
    for i in range(min(len(left), len(right))):
      result = compare_packets(left[i], right[i], print_debug, depth+1)

      if result != None:
        return result
    
    if len(left) < len(right):
      if print_debug:
        print('  ' * (depth+1), end='')
        print('- Left side ran out of items, so inputs are in the right order')
      return True
    elif len(left) > len(right):
      if print_debug:
        print('  ' * (depth+1), end='')
        print('- Right side ran out of items, so inputs are NOT in the right order')
      return False
    else:
      return None
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

PRINT_DEBUG = False

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  left = None
  right = None
  index = 1
  index_sum = 0

  def compare(left, right):
    if PRINT_DEBUG:
      print(f'== Pair {index} ==')

    result = compare_packets(left, right, PRINT_DEBUG)
    if result == True:
      global index_sum
      index_sum += index

    if PRINT_DEBUG:
      print()
  
  for line in f:
    l_strip = line.strip()

    if l_strip != '':
      if left == None:
        left = parse_packet(l_strip)
      else:
        right = parse_packet(l_strip)
    else:
      compare(left, right)

      left = None
      right = None
      index += 1
  
  compare(left, right)

  if PRINT_DEBUG:
    print(f'Sum of packet indices in the right order: {index_sum}')
  else:
    print(index_sum)
