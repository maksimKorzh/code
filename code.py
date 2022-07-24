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
      if self.cury != 0:
        self.cury -= 1
        self.curx = 0
      else: self.curx = 0
    elif key == curses.KEY_DOWN:
      if self.total_lines and self.cury != self.total_lines-1:
        self.cury += 1
        self.curx = len(self.buff[self.cury])
      elif self.cury == self.total_lines-1:
        self.curx = len(self.buff[self.total_lines-1])
  '''
      case ARROW_UP:
        if (cury != 0) {
          cury--;
          curx = lastx;
        } else curx = 0;
        break;
      case ARROW_DOWN:
        if (total_lines && cury != total_lines - 1) {
          cury++;
          curx = lastx;
        } else if (cury == total_lines - 1) curx = text[total_lines].rlen;
        break;
    }
    row = (cury >= total_lines) ? NULL : &text[cury];
    int rowlen = row ? row->len : 0;
    if (curx > rowlen) curx = rowlen;
  }
  '''
  
  def scroll_buffer(self):
    if self.cury < self.offy: self.offy = self.cury
    if self.cury >= self.offy + self.ROWS: self.offy = self.cury - self.ROWS+1
    if self.curx < self.offx: self.offx = self.curx
    if self.curx >= self.offx + self.COLS: self.offx = self.curx - self.COLS+1

  def print_buffer(self):
    for row in range(len(self.buff)):
      if row >= self.offy and row <= self.offy + self.ROWS-1:
        for col in range(len(self.buff[row])):
          if col >= self.offx and col <= self.offx + self.COLS-1:
            try: self.screen.addch(self.buff[row][col])
            except: pass
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
    elif c == curses.KEY_HOME: pass
    elif c == curses.KEY_END: pass
    elif c == curses.KEY_LEFT: self.move_cursor(c)
    elif c == curses.KEY_RIGHT: self.move_cursor(c)
    elif c == curses.KEY_UP: self.move_cursor(c)
    elif c == curses.KEY_DOWN: self.move_cursor(c)
    elif c == curses.KEY_BACKSPACE: pass
    elif c == curses.KEY_NPAGE: pass
    elif c == curses.KEY_PPAGE: pass
    elif c == 530: pass # ctrl-end
    elif c == 535: pass # ctrl-home
    else: pass#self.insert_char(c)

  def open_file(self, filename):
    with open('code.py') as f:
      content = f.read().split('\n')
      for row in content[:-1]:
        self.buff.append([ord(c) for c in row])
        self.total_lines += 1
    self.update_screen()

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
    editor.open_file('code.py')
    editor.start()

  wrapper(main)

# last commented line
