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
    self.curs = 0
    self.buff = []
    self.total_lines = 0
    curses.raw()
    curses.noecho()

  def ctrl(self, c): return ((c) & 0x1f)
  def move_right(self):    
    if self.curs < len(self.buff):
      if self.buff[self.curs] == ord('\n'):
        self.cury += 1
        self.curx = 0
      else: self.curx += 1
      self.curs += 1;
    if self.cury == self.ROWS:
      self.cury -= 1
      self.offy += 1

  def move_left(self):
    if self.curs:
      self.curs -= 1
      if self.curx: self.curx -= 1
      else:
        if self.cury > -1: self.cury -= 1
        count = self.curs - 1
        while self.buff[count] != ord('\n'): count -= 1;
        self.curx = self.curs - count - 1
        if self.cury == 0 and not self.offy:
          self.curx = self.curs
        if self.cury == -1 and self.offy > 1:
          self.cury += 1
          self.offy -= 1
        elif self.cury == -1 and self.offy <=1:
          self.offy -= 1
          self.cury += 1
          self.curx = self.curs

  def move_up(self):
    self.move_home()
    self.move_left()
    while self.curx > self.usrx: self.move_left()
        
  def move_down(self):
    self.move_end()
    self.move_right()
    while self.curx < self.usrx:
      if self.curs == len(self.buff): break
      if self.buff[self.curs] == ord('\n'): break
      self.move_right()
  
  def page_down(self):
    if self.offy >= self.total_lines - self.ROWS - 1:
      while self.cury != self.ROWS - 1: self.move_down()
      self.move_end()
      return
    self.screen.clear()
    count = 0
    while count != self.ROWS - 1:
      if self.offy <= self.total_lines - self.ROWS - 1:
        self.offy += 1
        self.cury -= 1
      self.move_down()
      count += 1
  
  def page_up(self):
    if self.offy == 0:
      while self.cury != 0: self.move_up()
      self.move_home()
      return
    count = 0
    while count != self.ROWS - 1 and self.offy:
      self.offy -= 1
      self.cury += 1
      self.move_up()
      count += 1
  
  def move_bottom(self):
    while self.curs <= len(self.buff) - 1:
      self.page_down()
  
  def move_top(self):
    while self.curs: self.page_up()
  
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
      self.total_lines += 1
      if self.cury < self.ROWS - 1: self.cury += 1
      self.curx = -1
      self.screen.clrtoeol()
    self.buff.insert(self.curs, c); self.curs += 1
    self.curx += 1
    self.usrx = self.curx

  def print_buffer(self):
    '''
    start printing chars only when current
    buffer row is >= than the row offset
    stop printing rows when printed 24 rows
    '''
    
    
    
    rows = 0
    for c in self.buff:
      if rows >= self.offy and rows < self.ROWS + self.offy:
        try: self.screen.addch(c)
        except: pass

      if c == ord('\n'):
        rows += 1
        if rows > self.ROWS + self.offy-1: break

  def update_screen(self):
    self.screen.move(0, 0)
    curses.curs_set(0)
    self.print_buffer()
    
    #if self.cury < self.ROWS-1 and self.curx < self.COLS-1:
    self.screen.move(self.cury, self.curx)

    curses.curs_set(1)
    self.screen.refresh()

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
    elif c == curses.KEY_NPAGE: self.page_down()
    elif c == curses.KEY_PPAGE:self.page_up()
    elif c == 530: self.move_bottom()
    elif c == 535: self.move_top()
    else: self.insert_char(c)

  def open_file(self, filename):
    with open('code.py') as f:
      content = f.read()
      self.buff = [ord(c) for c in content[:-1]]
      self.total_lines = len(content.split('\n')) - 1
    self.update_screen()

  def exit(self):
    curses.endwin()
    sys.exit(0)

  def start(self):
    while(True):
      self.read_keyboard()
      self.update_screen()

if __name__ == '__main__':
  editor = Editor()
  editor.open_file('code.py')
  editor.start()

# last commented line
