#!/bin/python3
import curses
import sys

class Editor():
  def __init__(self):
    self.screen = curses.initscr()
    self.screen.keypad(True)
    self.screen.nodelay(1)
    self.ROWS, self.COLS = self.screen.getmaxyx()
    self.ROWS -= 1
    curses.raw()
    curses.noecho()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    self.screen.attron(curses.color_pair(1))

  def reset(self):
    self.curx = 0
    self.cury = 0
    self.offx = 0
    self.offy = 0
    self.usrx = 0
    self.buff = []
    self.total_lines = 0
    self.filename = 'Untitled.txt'
    self.modified = 0
  
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
  
  def move_cursor(self, key):
    row = self.buff[self.cury] if self.cury < self.total_lines else None
    if key == curses.KEY_LEFT:
      if self.curx != 0:
        self.curx -= 1
        self.usrx -= 1
      elif self.cury > 0:
        self.cury -= 1
        self.curx = len(self.buff[self.cury])
    elif key == curses.KEY_RIGHT:
      if row is not None and self.curx < len(row):
        self.curx += 1
        self.usrx += 1
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
    self.screen.attron(curses.color_pair(2))
    status = self.filename + ' - ' + str(self.total_lines) + ' lines'
    status += ' modified' if self.modified else ' saved'
    pos = 'Row ' + str(self.cury+1) + ', Col ' + str(self.curx+1)
    while len(status) < self.COLS - len(pos)-1: status += ' '
    status += pos + ' '
    if len(status) > self.COLS: status = status[:self.COLS]
    try: self.screen.addstr(self.ROWS, 0, status)
    except: pass
    self.screen.attron(curses.color_pair(1))
  
  def print_buffer(self):
    char_count = 0
    last_keyword = ''
    for row in range(self.ROWS):
      buffrow = row + self.offy
      for col in range(self.COLS):
        buffcol = col + self.offx
        try: self.screen.addch(row, col, self.buff[buffrow][buffcol])
        except: pass

      self.screen.clrtoeol()
      try: self.screen.addch('\n')
      except: pass

  def update_screen(self):
    self.screen.move(0, 0)
    self.scroll_buffer()
    self.print_buffer()
    self.print_status_bar()
    curses.curs_set(0)
    self.screen.move(self.cury - self.offy, self.curx - self.offx)
    curses.curs_set(1)
    self.screen.refresh()

  def read_keyboard(self):
    def ctrl(c): return ((c) & 0x1f)
    c = -1
    while (c == -1): c = self.screen.getch()
    if c == ctrl(ord('q')): self.exit()
    if c == ctrl(ord('n')): self.new_file()
    if c == ctrl(ord('s')): self.save_file()
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
    elif c == ord('\n'): self.insert_line()
    else: self.insert_char(c)
    self.update_screen()

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
