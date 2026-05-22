import os
from cmu_graphics import *

app.width = 1280
app.height = 740
games = Group()

app.background = gradient('black', 'dimGray', 'black', start='top')
for i in range (4):
    tetris = Rect(50,100,150,250,fill=gradient('black','midnightBlue',start='top'),border='black',borderWidth=5)
    tetrisIcon = Image('assets\\tetris\\images\\logo.png', 125, 225, width=110, height=80,align='center')
    nonGame = Rect(305 + 255 * i,100,150,250,fill='white',border='black',borderWidth=5)
    games.add(tetris, tetrisIcon, nonGame)

startup_script = r'C:\Users\Copilot\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\run.bat'

def onMousePress(x, y, button):
    if 50 <= x <= 200 and 100 <= y <= 350 and button == 0:
        if os.path.exists(startup_script):
            os.startfile(startup_script)


def onStep():
    games.centerY = app.height / 2

cmu_graphics.run()