import curses
import sys

screen = curses.initscr()
curses.raw()
curses.noecho()
screen.keypad(True)
screen.nodelay(1)
COLS = 80
ROWS = 24
usrx = 0
curx = 0
cury = 0
curs = 0
buff = []

def ctrl(c): return ((c) & 0x1f)

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

def move_up():
  move_home()
  move_left()
  while curx > usrx:
    move_left()

def move_down():
  move_end()
  move_right()
  while curx < usrx:
    if curs == len(buff): break
    if buff[curs] == ord('\n'): break
    move_right()

def move_home():
  global usrx
  while(True):
    if curs == 0:
      usrx = curs
      break
    elif buff[curs-1] == ord('\n'): break
    move_left()

def move_end():
  global usrx
  while(True):
    if curs == len(buff):
      usrx = curx
      break
    if buff[curs] == ord('\n'): break
    move_right()

def delete_char():
  move_left()
  if len(buff): del buff[curs]
  screen.clear()

def insert_char(c):
  global curs, curx, cury, usrx
  if c == ord('\n'): cury += 1; curx = -1;
  buff.insert(curs, c); curs += 1
  curx += 1
  usrx = curx

def exit():
  curses.endwin()
  sys.exit(0)

def read_keyboard():
  global usrx
  c = -1
  while (c == -1): c = screen.getch()
  if c == ctrl(ord('q')): exit()
  elif c == curses.KEY_HOME: move_home(); usrx = curx
  elif c == curses.KEY_END: move_end(); usrx = curx
  elif c == curses.KEY_LEFT: move_left(); usrx = curx
  elif c == curses.KEY_RIGHT: move_right(); usrx = curx
  elif c == curses.KEY_UP: move_up()
  elif c == curses.KEY_DOWN: move_down()
  elif c == curses.KEY_BACKSPACE: delete_char()
  else: insert_char(c)

def update_screen():
  screen.move(0, 0)
  curses.curs_set(0)
  [screen.addch(c) for c in buff]
  screen.move(cury, curx)
  curses.curs_set(1)
  screen.refresh()

while(True):
  read_keyboard()
  update_screen()


