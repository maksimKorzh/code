#!/bin/python3
import curses
import sys
from pygments.lexers import PythonLexer, CLexer
from pygments.formatters import TerminalFormatter
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace
from pygments import highlight

COLOR_SCHEME = {
  Token:              ('gray',                 'gray'),
  Comment:            ('magenta',     'brightmagenta'),
  Comment.Preproc:    ('magenta',     'brightmagenta'),
  Keyword:            ('blue',                   '**'),
  Keyword.Type:       ('green',       '*brightgreen*'),
  Operator.Word:      ('**',                     '**'),
  Name.Builtin:       ('cyan',           'brightblue'),
  Name.Function:      ('blue',           'brightblue'),
  Name.Class:         ('_green_',        'brightblue'),
  Name.Decorator:     ('magenta',     'brightmagenta'),
  Name.Variable:      ('blue',           'brightblue'),
  String:             ('yellow',       'brightyellow'),
  Number:             ('blue',         'brightyellow')
}

class Editor():
  def __init__(self):
    self.screen = curses.initscr()
    self.screen.keypad(True)
    self.screen.nodelay(1)
    self.ROWS, self.COLS = self.screen.getmaxyx()
    self.ROWS -= 1
    curses.raw()
    curses.noecho()
    self.lexers = { 'py': PythonLexer, 'c': CLexer}

  def reset(self):
    self.curx = 0
    self.cury = 0
    self.offx = 0
    self.offy = 0
    self.buff = []
    self.total_lines = 0
    self.filename = 'Untitled.txt'
    self.modified = 0
    self.search_results = []
    self.search_index = 0
  
  def insert_char(self, c):
    self.buff[self.cury].insert(self.curx, c)
    self.curx += 1
    self.modified += 1
  
  def delete_char(self):
    if self.curx:
      self.curx -= 1
      del self.buff[self.cury][self.curx]
    elif self.curx == 0 and self.cury:
      oldline = self.buff[self.cury][self.curx:]
      del self.buff[self.cury]
      self.cury -= 1
      self.curx = len(self.buff[self.cury])
      self.buff[self.cury] += oldline
      self.total_lines -= 1
    self.modified += 1

  def insert_line(self):
    oldline = self.buff[self.cury][self.curx:]
    self.buff[self.cury] = self.buff[self.cury][:self.curx]
    self.cury += 1
    self.curx = 0
    self.buff.insert(self.cury, [] + oldline)
    self.total_lines += 1
    self.modified += 1
  
  def delete_line(self):
    if len(self.buff) == 1: return
    try:
      del self.buff[self.cury]
      self.curx = 0
      self.total_lines -= 1
    except: pass
    self.modified += 1
    if self.cury >= self.total_lines:
      self.cury = self.total_lines-1

  def move_cursor(self, key):
    row = self.buff[self.cury] if self.cury < self.total_lines else None
    if key == curses.KEY_LEFT:
      if self.curx != 0: self.curx -= 1
      elif self.cury > 0:
        self.cury -= 1
        self.curx = len(self.buff[self.cury])
    elif key == curses.KEY_RIGHT:
      if row is not None and self.curx < len(row):
        self.curx += 1
      elif row is not None and self.curx == len(row) and self.cury != self.total_lines-1:
        self.cury += 1
        self.curx = 0
    elif key == curses.KEY_UP:
      if self.cury != 0: self.cury -= 1
      else: self.curx = 0
    elif key == curses.KEY_DOWN:
      if self.cury < self.total_lines-1: self.cury += 1
      else: self.curx = len(self.buff[self.cury])
    row = self.buff[self.cury] if self.cury < self.total_lines else None
    rowlen = len(row) if row is not None else 0
    if self.curx > rowlen: self.curx = rowlen
  
  def skip_word(self, key):
    if key == 545:
      self.move_cursor(curses.KEY_LEFT)
      try:
        if self.buff[self.cury][self.curx] != ord(' '):
          while self.buff[self.cury][self.curx] != ord(' '):
            if self.curx == 0: break
            self.move_cursor(curses.KEY_LEFT)
        elif self.buff[self.cury][self.curx] == ord(' '):
          while self.buff[self.cury][self.curx] == ord(' '):
            if self.curx == 0: break
            self.move_cursor(curses.KEY_LEFT)
      except: pass
    if key == 560:
      self.move_cursor(curses.KEY_RIGHT)
      try:
        if self.buff[self.cury][self.curx] != ord(' '):
          while self.buff[self.cury][self.curx] != ord(' '):
            self.move_cursor(curses.KEY_RIGHT)
        elif self.buff[self.cury][self.curx] == ord(' '):
          while self.buff[self.cury][self.curx] == ord(' '):
            self.move_cursor(curses.KEY_RIGHT)
      except: pass

  def scroll_end(self):
    while self.cury < self.total_lines-1:
      self.scroll_page(curses.KEY_NPAGE)

  def scroll_home(self):
    while self.cury:
      self.scroll_page(curses.KEY_PPAGE)

  def scroll_page(self, key):
    count = 0
    while count != self.ROWS:
      if key == curses.KEY_NPAGE:
        self.move_cursor(curses.KEY_DOWN)
        if self.offy < self.total_lines - self.ROWS: self.offy += 1
      elif key == curses.KEY_PPAGE:
        self.move_cursor(curses.KEY_UP)
        if self.offy: self.offy -= 1
      count += 1

  def scroll_buffer(self):
    if self.cury < self.offy: self.offy = self.cury
    if self.cury >= self.offy + self.ROWS: self.offy = self.cury - self.ROWS+1
    if self.curx < self.offx: self.offx = self.curx
    if self.curx >= self.offx + self.COLS: self.offx = self.curx - self.COLS+1

  def print_status_bar(self):
    status = '\x1b[7m'
    status += self.filename + ' - ' + str(self.total_lines) + ' lines'
    status += ' modified' if self.modified else ' saved'
    pos = 'Row ' + str(self.cury+1) + ', Col ' + str(self.curx+1)
    while len(status) < self.COLS - len(pos) + 3: status += ' '
    status += pos + ' '
    status += '\x1b[m'
    status += '\x1b[' + str(self.cury - self.offy+1) + ';' + str(self.curx - self.offx+1) + 'H'
    status += '\x1b[?25h'
    return status

  def print_buffer(self):
    print_buffer = '\x1b[?25l'
    print_buffer += '\x1b[H'
    for row in range(self.ROWS):
      buffrow = row + self.offy;
      if buffrow < self.total_lines:
        rowlen = len(self.buff[buffrow]) - self.offx
        if rowlen < 0: rowlen = 0;
        if rowlen > self.COLS: rowlen = self.COLS;
        try:
          print_buffer += highlight(
          ''.join([chr(c) for c in self.buff[buffrow][self.offx: self.offx + rowlen]]),
          self.lexers[self.filename.split('.')[-1]](),
          TerminalFormatter(bg='dark', colorscheme=COLOR_SCHEME))[:-1]
        except: print_buffer += ''.join([chr(c) for c in self.buff[buffrow][self.offx: self.offx + rowlen]])
      print_buffer += '\x1b[K'
      print_buffer += '\r\n'
    return print_buffer

  def update_screen(self):
    self.scroll_buffer()
    print_buffer = self.print_buffer()
    status_bar = self.print_status_bar()
    sys.stdout.write(print_buffer + status_bar)
    sys.stdout.flush()

  def read_keyboard(self):
    def ctrl(c): return ((c) & 0x1f)
    c = -1
    while (c == -1): c = self.screen.getch()
    if c == ctrl(ord('q')): self.exit()
    elif c == 9: [self.insert_char(ord(' ')) for i in range(4)]
    elif c == 353: [self.delete_char() for i in range(4) if self.curx]
    elif c == ctrl(ord('n')): self.new_file()
    elif c == ctrl(ord('s')): self.save_file()
    elif c == ctrl(ord('f')): self.search()
    elif c == ctrl(ord('g')): self.find_next()
    elif c == ctrl(ord('d')): self.delete_line()
    elif c == ctrl(ord('t')): self.indent()
    elif c == curses.KEY_HOME: self.curx = 0
    elif c == curses.KEY_END: self.curx = len(self.buff[self.cury])
    elif c == curses.KEY_LEFT: self.move_cursor(c)
    elif c == curses.KEY_RIGHT: self.move_cursor(c)
    elif c == curses.KEY_UP: self.move_cursor(c)
    elif c == curses.KEY_DOWN: self.move_cursor(c)
    elif c == curses.KEY_BACKSPACE: self.delete_char()
    elif c == curses.KEY_NPAGE: self.scroll_page(c)
    elif c == curses.KEY_PPAGE: self.scroll_page(c)
    elif c == 530: self.scroll_end()
    elif c == 535: self.scroll_home()
    elif c == 560: self.skip_word(560)
    elif c == 545: self.skip_word(545)
    elif c == ord('\n'): self.insert_line()
    elif ctrl(c) != c: self.insert_char(c)
    self.update_screen()

  def command_prompt(self, line):
    command_line = '\x1b[' + str(self.ROWS+1) + ';' + '0' + 'H'
    command_line += '\x1b[7m' + line
    command_line += ''.join([' ' for i in range(self.COLS - 22)])
    sys.stdout.write(command_line)
    sys.stdout.flush()
    self.screen.move(self.ROWS, 8)
    self.screen.refresh()
    word = ''; c = -1
    while c != 0x1b:
      c = -1
      while (c == -1): c = self.screen.getch()
      if c == 10: break
      if c == curses.KEY_BACKSPACE:
        if self.screen.getyx()[1] > 8:
          self.screen.move(self.ROWS, self.screen.getyx()[1]-1)
          self.screen.addch(' ')
          self.screen.move(self.ROWS, self.screen.getyx()[1]-1)
          word = word[:len(word)-1]
      word += chr(c)
      if c != curses.KEY_BACKSPACE: self.screen.addch(c)
      else: word = word[:len(word)-1]
    return word

  def indent(self):
    indent = self.command_prompt('indent:')
    try: # format: [rows] [cols] [+/-]
      start_row = self.cury
      end_row = self.cury + int(indent.split()[0])
      start_col = self.curx
      end_col = self.curx + int(indent.split()[1])
      dir = indent.split()[2]
      try: char = indent.split()[3]
      except: char = ''
      for row in range(start_row, end_row):
        for col in range(start_col, end_col):
          if dir == '+': self.buff[row].insert(col, ord(char if char != '' else ' '))
          if dir == '-': del self.buff[row][self.curx]
      self.modified += 1        
    except: pass

  def search(self):
    self.search_results = []
    self.search_index = 0
    word = self.command_prompt('search:')
    for row in range(len(self.buff)):
      buffrow = self.buff[row]
      for col in range(len(buffrow)):
        if ''.join([chr(c) for c in buffrow[col:col+len(word)]]) == word:
          self.search_results.append([row, col])
    if len(self.search_results):
      self.cury, self.curx = self.search_results[self.search_index]
      self.search_index += 1

  def find_next(self):
    if len(self.search_results):
      if self.search_index == len(self.search_results):
        self.search_index = 0
      try: self.cury, self.curx = self.search_results[self.search_index]
      except: pass
      self.search_index += 1

  def open_file(self, filename):
    self.reset()
    try:
      with open(filename) as f:
        content = f.read().split('\n')
        for row in content[:-1]:
          self.buff.append([ord(c) for c in row])
    except: self.buff.append([])
    if filename:
      self.filename = filename
      if '.txt' in filename: self.highlight = False
      else: self.highlight = True
    self.total_lines = len(self.buff)
    self.update_screen()
  
  def save_file(self):
    with open(self.filename, 'w') as f:
      content = ''
      for row in self.buff:
        content += ''.join([chr(c) for c in row]) + '\n'
      f.write(content)
    self.modified = 0

  def new_file(self):
    self.reset()
    self.buff.append([])
    self.total_lines = 1

  def exit(self):
    curses.endwin()
    sys.exit(0)

  def start(self):
    self.update_screen()
    while(True):
      self.read_keyboard()
      self.update_screen()

if __name__ == '__main__':
  def main(stdscr):
    editor = Editor()
    if len(sys.argv) >= 2: editor.open_file(sys.argv[1])
    else: editor.open_file('')
    editor.start()

  curses.wrapper(main)
