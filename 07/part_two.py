import os

def get_filepath(file):
  absolute_path = os.path.dirname(__file__)
  return os.path.join(absolute_path, file)


class BaseStruct:
  def __init__(self, name):
    self.name = name
  
  def get_size(self):
    pass
  
  def print_content(self):
    print(self.name)


class FileStruct(BaseStruct):
  def __init__(self, name, size):
    super().__init__(name)
    self.size = size
  
  def get_size(self):
    return self.size
  
  def print_content(self, depth=0):
    print('| ' * depth, end="")
    print(f'- {self.name} (file, size={self.size})')


class DirStruct(BaseStruct):
  def __init__(self, name, parent_dir=None):
    super().__init__(name)
    self.content = []
    self.parent_dir = parent_dir
  
  def get_size(self):
    size = 0
    for child in self.content:
      size += child.get_size()
    return size
  
  def print_content(self, depth=0):
    print('| ' * depth, end="")
    print(f'- {self.name} (dir)')

    for child in self.content:
      child.print_content(depth + 1)
  
  def create_file(self, name, size):
    file = FileStruct(name, size)
    self.content.append(file)
  
  def create_dir(self, name):
    dir = DirStruct(name, self)
    self.content.append(dir)
  
  def get_subdir(self, name):
    for content in self.content:
      if isinstance(content, DirStruct) and content.name == name:
        return content
    return None


def get_min_deletable_dir(current_dir, space_needed):
  deletable_dir = None

  for child in current_dir.content:
    if isinstance(child, DirStruct):
      dir = get_min_deletable_dir(child, space_needed)

      if dir != None:
        dir_size = dir.get_size()

        if dir_size > space_needed:
          if deletable_dir == None or dir_size < deletable_dir.get_size():
            deletable_dir = dir
  
  current_dir_size = current_dir.get_size()

  if current_dir_size > space_needed:
    if deletable_dir == None or current_dir_size < deletable_dir.get_size():
      deletable_dir = current_dir

  return deletable_dir

root = DirStruct('/')

with open(get_filepath("input.txt"), encoding="utf-8") as f:
  current_dir = root

  for line in f:
    l_strip = line.strip()

    if l_strip.startswith('$'):
      # It's a command
      command = l_strip.removeprefix('$ ')

      if command.startswith('ls'):
        # List command, do nothing for now
        continue
      elif command.startswith('cd'):
        # Change directory command
        target_dir = command.removeprefix('cd ')

        if target_dir == '/':
          current_dir = root
        elif target_dir == '..':
          current_dir = current_dir.parent_dir
        else:
          current_dir = current_dir.get_subdir(target_dir)

          if current_dir == None:
            raise Exception('Target directory not found')
    else:
      # Not a command, meaning it's the output of the list command
      arg1, arg2 = l_strip.split(' ')

      if arg1 == 'dir':
        # The listed object is a directory
        dir_name = arg2
        current_dir.create_dir(dir_name)
      else:
        # The listed object is a file
        file_name, file_size = arg2, int(arg1)
        current_dir.create_file(file_name, file_size)

root.print_content()
print()

TOTAL_DISKSPACE = 70000000
UPDATE_SIZE = 30000000

unused_space = TOTAL_DISKSPACE - root.get_size()

if unused_space > UPDATE_SIZE:
  print('No file deletion needed!')
else:
  needed_space = UPDATE_SIZE - unused_space 
  print(f'Space needed to delete: {needed_space}')
  
  file = get_min_deletable_dir(root, needed_space)
  print(f'File to delete: {file.name} (size={file.get_size()})')
