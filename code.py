import curses
import sys

class Editor():
  def __init__(self):
    self.screen = curses.initscr()
    self.screen.keypad(True)
    self.screen.nodelay(1)
    curses.raw()
    curses.noecho()
    self.COLS = 80
    self.ROWS = 24
    self.usrx = 0
    self.curx = 0
    self.cury = 0
    self.curs = 0
    self.buff = []

  def ctrl(self, c): return ((c) & 0x1f)
  def move_right(self):    
    if self.curs < len(self.buff):
      if self.buff[self.curs] == ord('\n'):
        self.cury += 1
        self.curx = 0
      else: self.curx += 1
      self.curs += 1;

  def move_left(self):
    if self.curs:
      self.curs -= 1
      if self.curx: self.curx -= 1
      else:
        if self.cury: self.cury -= 1
        if self.cury == 0: self.curx = self.curs
        else:
          count = self.curs - 1
          while(self.buff[count] != ord('\n')): count -= 1
          self.curx = self.curs - count - 1

  def move_up(self):
    self.move_home()
    self.move_left()
    while self.curx > self.usrx:
      self.move_left()

  def move_down(self):
    self.move_end()
    self.move_right()
    while self.curx < self.usrx:
      if self.curs == len(self.buff): break
      if self.buff[self.curs] == ord('\n'): break
      self.move_right()

  def move_home(self):
    while(True):
      if self.curs == 0:
        self.usrx = self.curs
        break
      elif self.buff[self.curs-1] == ord('\n'): break
      self.move_left()

  def move_end(self):
    while(True):
      if self.curs == len(self.buff):
        self.usrx = self.curx
        break
      if self.buff[self.curs] == ord('\n'): break
      self.move_right()

  def delete_char(self):
    self.move_left()
    if len(self.buff): del self.buff[self.curs]
    self.screen.clear()

  def insert_char(self, c):
    if c == ord('\n'):
      self.cury += 1
      self.curx = -1;
    self.buff.insert(self.curs, c); self.curs += 1
    self.curx += 1
    self.usrx = self.curx

  def exit(self):
    curses.endwin()
    sys.exit(0)

  def read_keyboard(self):
    self.usrx = self.usrx
    c = -1
    while (c == -1): c = self.screen.getch()
    if c == self.ctrl(ord('q')): self.exit()
    elif c == curses.KEY_HOME: self.move_home(); self.usrx = self.curx
    elif c == curses.KEY_END: self.move_end(); self.usrx = self.curx
    elif c == curses.KEY_LEFT: self.move_left(); self.usrx = self.curx
    elif c == curses.KEY_RIGHT: self.move_right(); self.usrx = self.curx
    elif c == curses.KEY_UP: self.move_up()
    elif c == curses.KEY_DOWN: self.move_down()
    elif c == curses.KEY_BACKSPACE: self.delete_char()
    else: self.insert_char(c)

  def update_screen(self):
    self.screen.move(0, 0)
    curses.curs_set(0)
    [self.screen.addch(c) for c in self.buff]
    self.screen.move(self.cury, self.curx)
    curses.curs_set(1)
    self.screen.refresh()
  
  def start(self):
    while(True):
      self.read_keyboard()
      self.update_screen()

if __name__ == '__main__':
  editor = Editor()
  editor.start()

