import curses

screen = curses.initscr()
curses.raw()
curses.noecho()
screen.keypad(True)
screen.nodelay(1)

def ctrl(c): return ((c) & 0x1f)

COLS = 80
ROWS = 24
curx = 0
cury = 0
curs = 0
buff = []

def move_right():
  global curs, curx, cury
  if curs < len(buff):
    if buff[curs] == ord('\n'):
      cury += 1
      curx = 0
    else: curx += 1
    curs += 1;

def move_left():
  global curs, curx, cury
  if curs:
    curs -= 1
    if curx: curx -= 1
    else:
      if cury: cury -= 1
      if cury == 0:
        curx = curs
      else:
        count = curs - 1
        while(buff[count] != ord('\n')): count -= 1
        curx = curs - count - 1

while(True):
  c = screen.getch()
  if (c == -1): continue
  if c == ctrl(ord('q')): break
  elif c == curses.KEY_LEFT: move_left()
  elif c == curses.KEY_RIGHT: move_right()
  elif c == curses.KEY_BACKSPACE:
    move_left()
    if len(buff): del buff[curs]
    screen.clear()
  else:
    if c == ord('\n'): cury += 1; curx = -1;
    buff.insert(curs, c); curs += 1
    curx += 1

  screen.move(0, 0)
  curses.curs_set(0)
  [screen.addch(c) for c in buff]
  screen.move(cury, curx)
  curses.curs_set(1)
  screen.refresh()

curses.endwin()

