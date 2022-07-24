from curses import wrapper
import curses
import sys

class Editor():
  def __init__(self):
    self.screen = curses.initscr()
    self.screen.keypad(True)
    self.screen.nodelay(1)
    self.COLS = 80
    self.ROWS = 24
    self.offx = 0
    self.offy = 0
    self.usrx = 0
    self.curx = 0
    self.cury = 0
    self.buff = []
    self.total_lines = 0
    curses.raw()
    curses.noecho()
    curses.start_color()
    curses.init_pair(1, 15, curses.COLOR_BLACK)
    self.screen.attron(curses.color_pair(1))
  
  def insert_char(self, c):
    self.buff[self.cury].insert(self.curx, c)
    self.curx += 1
  
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

  def insert_line(self):
    oldline = self.buff[self.cury][self.curx:]
    self.buff[self.cury] = self.buff[self.cury][:self.curx]
    self.cury += 1
    self.curx = 0
    self.buff.insert(self.cury, [] + oldline)
    self.total_lines += 1
  
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
    elif key == curses.KEY_DOWN:
      if self.cury < self.total_lines-1:
        self.cury += 1
    row = self.buff[self.cury] if self.cury < self.total_lines else None
    rowlen = len(row) if row is not None else 0
    if self.curx > rowlen: self.curx = rowlen
  
  def scroll_page(self, key):
    if key == curses.KEY_PPAGE: self.cury = self.offy
    elif key == curses.KEY_NPAGE:
      self.cury = self.offy + self.ROWS -1
      if self.cury > self.total_lines: self.cury = self.total_lines
    times = self.ROWS
    while times:
      self.move_cursor(curses.KEY_UP if key == curses.KEY_PPAGE else curses.KEY_DOWN)
      times -= 1

  def scroll_buffer(self):
    if self.cury < self.offy: self.offy = self.cury
    if self.cury >= self.offy + self.ROWS: self.offy = self.cury - self.ROWS+1
    if self.curx < self.offx: self.offx = self.curx
    if self.curx >= self.offx + self.COLS: self.offx = self.curx - self.COLS+1
  
  def print_buffer(self):
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
    curses.curs_set(0)
    self.screen.move(self.cury - self.offy, self.curx - self.offx)
    curses.curs_set(1)
    self.screen.refresh()

  def read_keyboard(self):
    def ctrl(c): return ((c) & 0x1f)
    c = -1
    while (c == -1): c = self.screen.getch()
    if c == ctrl(ord('q')): self.exit()
    if c == ctrl(ord('s')): self.save_file()
    elif c == curses.KEY_HOME: pass
    elif c == curses.KEY_END: pass
    elif c == curses.KEY_LEFT: self.move_cursor(c)
    elif c == curses.KEY_RIGHT: self.move_cursor(c)
    elif c == curses.KEY_UP: self.move_cursor(c)
    elif c == curses.KEY_DOWN: self.move_cursor(c)
    elif c == curses.KEY_BACKSPACE: self.delete_char()
    elif c == curses.KEY_NPAGE: self.scroll_page(c)
    elif c == curses.KEY_PPAGE: self.scroll_page(c)
    elif c == 530: pass # ctrl-end
    elif c == 535: pass # ctrl-home
    elif c == ord('\n'): self.insert_line()
    else: self.insert_char(c)

  def open_file(self, filename):
    with open(filename) as f:
      content = f.read().split('\n')
      for row in content[:-1]:
        self.buff.append([ord(c) for c in row])
    self.total_lines = len(self.buff)
    self.update_screen()
  
  def save_file(self):
    with open('test.txt', 'w') as f:
      content = ''
      for row in self.buff:
        content += ''.join([chr(c) for c in row]) + '\n'
      f.write(content)

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
    editor.open_file('test.txt')
    editor.start()

  wrapper(main)

# last commented line
# EOF
