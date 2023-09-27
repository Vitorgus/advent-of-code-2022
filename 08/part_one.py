import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

grid = []

with open(get_filepath("example.txt"), encoding="utf-8") as f:
  for line in f:
    l_split = line.strip()
    tree_row = []

    for tree in l_split:
      tree_row.append(int(tree))

    grid.append(tree_row)


def is_visible(grid, tree_row, tree_column):
  if (tree_row == 0 or tree_column == 0 or
      tree_row == len(grid) - 1 or tree_column == len(grid[tree_row]) - 1):
    return True

  tree = grid[tree_row][tree_column]

  visible = True
  for north_coord in range(0, tree_row):
    if grid[north_coord][tree_column] >= tree:
      visible = False
      break
  if visible:
    return True

  visible = True
  for south_coord in range(tree_row + 1, len(grid)):
    if grid[south_coord][tree_column] >= tree:
      visible = False
      break
  if visible:
    return True

  visible = True
  for west_coord in range(0, tree_column):
    if grid[tree_row][west_coord] >= tree:
      visible = False
      break
  if visible:
    return True

  visible = True
  for east_coord in range(tree_column + 1, len(grid[tree_row])):
    if grid[tree_row][east_coord] >= tree:
      visible = False
      break
  if visible:
    return True

  return False


visible_trees = 0

for row in range(len(grid)):
  for column in range(len(grid[row])):
    if is_visible(grid, row, column):
      visible_trees += 1

print(visible_trees)
