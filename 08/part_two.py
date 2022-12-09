import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)

grid = []

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  for line in f:
    l_split = line.strip()
    tree_row = []

    for tree in l_split:
      tree_row.append(int(tree))

    grid.append(tree_row)


def get_scenic_score(grid, tree_row, tree_column):
  tree = grid[tree_row][tree_column]

  north_score = 0
  for north_coord in range(tree_row - 1, -1, -1):
    north_score += 1
    if grid[north_coord][tree_column] >= tree:
      break
  
  south_score = 0
  for south_coord in range(tree_row + 1, len(grid)):
    south_score += 1
    if grid[south_coord][tree_column] >= tree:
      break
  
  west_score = 0
  for west_coord in range(tree_column - 1, -1, -1):
    west_score += 1
    if grid[tree_row][west_coord] >= tree:
      break
  
  east_score = 0
  for east_coord in range(tree_column + 1, len(grid[tree_row])):
    east_score += 1
    if grid[tree_row][east_coord] >= tree:
      break
  
  return north_score * south_score * west_score * east_score


highest_score = -1

for row in range(len(grid)):
  for column in range(len(grid[row])):
    current_score = get_scenic_score(grid, row, column)
    if current_score > highest_score:
      highest_score = current_score

print(highest_score)

