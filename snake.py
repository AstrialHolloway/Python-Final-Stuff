# Since the Tetris is almost finished, my teacher might not let me use it for the final :<
# There is a chance I can still use it, but I will be making Snake as a backup :3

from cmu_graphics import *
import os
import sys
import random
import time

#Restarts program so I don't have to mess with closing and opening the exe thing again
def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)

app.width = 1280
app.height = 740


def onKeyPress(key):
  if (key=='p'):
    restart_program()
cmu_graphics.run()
