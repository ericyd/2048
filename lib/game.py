import random
from util import grouper, compose, transpose, flatten, list_map

class Game:
  def __init__(self):
    self.board = self.generate()
    while len(list(filter(lambda x: x != 0, self.board))) < 2:
      self.board[random.randint(0, len(self.board) - 1)] = 2
    self.collapse_line = compose(self.sort_zeros, self.combine_adjacent, self.sort_zeros)
    self.score = 0
    self.score_move = 0
    self.previous_move = None

  def generate(self):
    return [
      0, 0, 0, 0,
      0, 0, 0, 0,
      0, 0, 0, 0,
      0, 0, 0, 0
    ]

  # run all moves as "fake"
  # if any move results are different from the existing board, then the game is not done
  def is_complete(self, array=None):
    array = array if array is not None else self.board
    result = True
    for direction in ['up', 'down', 'left', 'right']:
      if self.move(direction, fake = True) != array:
        result = False
        break
    return result

  def highest_tile(self):
    return max(self.board)

  def group(self, grouping, array=None):
    array = array if array is not None else self.board
    # group into nested list of lists, 4 items each
    nested_array = grouper(array, 4)
    if grouping == 'columns':
      nested_array = transpose(*nested_array)
    return nested_array

  def ungroup(self, grouping, array=None):
    array = array if array is not None else self.board
    nested_array = array[:]
    if grouping == 'columns':
      nested_array = transpose(*nested_array)
    # flatten - credit: https://stackoverflow.com/a/952952/3991555
    flat_array = flatten(nested_array)
    return flat_array

  def update(self, new_board, fake = False):
    if fake:
      return new_board
    elif self.board != new_board:
      # set previous move so self.back() will work
      self.previous_move = self.board[:]
      # set the board to the new pieces
      self.board = new_board
      # find a random index that is currently "0" and make it a "2"
      zero_pieces = filter(lambda tuple: tuple[1] == 0, enumerate(self.board))
      zero_indices = list_map(lambda tuple: tuple[0], zero_pieces)
      random_index = random.choice(zero_indices)
      self.board[random_index] = 2
      # add score
      self.score += self.score_move
      self.score_move = 0
    return self.board

  def move(self, direction, fake = False):
    self.score_move = 0
    if direction == 'back':
      return self.back()
    elif direction == 'up':
      lines = self.group('columns')
      new_lines = list_map(self.collapse_line, lines)
      return self.update(self.ungroup('columns', new_lines), fake)
    elif direction == 'down':
      lines = list_map(reversed, self.group('columns'))
      new_lines = list_map(self.collapse_line, lines)
      return self.update(self.ungroup('columns', list_map(reversed, new_lines)), fake)
    elif direction == 'left':
      lines = self.group('rows')
      new_lines = list_map(self.collapse_line, lines)
      return self.update(self.ungroup('rows', new_lines), fake)
    elif direction == 'right':
      lines = list_map(reversed, self.group('rows'))
      new_lines = list_map(self.collapse_line, lines)
      return self.update(self.ungroup('rows', list_map(reversed, new_lines)), fake)

  def back(self):
    if (self.previous_move != None):
      self.board = self.previous_move[:]
      # only allow going back once
      self.previous_move = None
    return self.board

  # this is kind of ugly but I can't figure out how to sort things in a more nuanced way
  # for [0, 2, 0, 4], returns [2, 4, 0, 0]
  def sort_zeros(self, line):
    new_line = []
    for x in line:
      if x != 0:
        new_line.append(x)
    while len(new_line) < 4:
      new_line.append(0)
    return new_line

  # for [4, 4, 2, 2], returns [8, 0, 4, 0]
  def combine_adjacent(self, line):
    new_line = line[:]
    for i, x in enumerate(line):
      # no need to check the last value
      if i == len(line) - 1:
        break
      if new_line[i + 1] == new_line[i]:
        new_line[i + 1] = 0
        new_value = new_line[i] * 2
        new_line[i] = new_value
        self.score_move += new_value
    return new_line

  def save(self):
    self.__saved_board = self.board[:]
    self.__saved_score = self.score

  def reset(self):
    self.board = self.__saved_board[:]
    self.score = self.__saved_score