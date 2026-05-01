#Goofy tetris code :3
#This code is for my final project for my advanced coding class.
#The final project was going to be a fnf remake, but that would take way too long to work on, so I am choosing this :3
#IDK how long this dang thing will take to finish, but I don't care. As long as I can finish it before the end of the school year lol
#If you make the screen size larger than 1280x740, it may look wrong, soooooo keep it like it is currently :3
#I'm too lazy to add good comments, so don't expect super organized comments lol

from cmu_graphics import *
import os
import sys
import random
import time
import math
import json

#Restarts program so I don't have to mess with closing and opening the exe thing again
def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)

#vars
app.width = 1280
app.height = 740
app.volume = 0.1

app.hardMode = False
app.pieceBag = []
app.selectedDifficulty = 'Normal'
app.selectedLevel = 1
app.startLevel = 1
app.level = 1
app.playing = False
app.steps = 0
app.stepCount = 0
app.score = 0
app.linesCleared = 0
app.startTime = None
app.moveDelay = 0
app.moveCooldown = 5
app.blockSize = 50
app.offsetX = 400
app.offsetY = 20
app.cols = 10
app.timerThing = 0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, 'data', 'Tetris', 'save.txt')

def save_high_score():
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, 'w') as file:
        json.dump({
            'normal': app.highScoreNormal,
            'hard': app.highScoreHard
        }, file)

def load_high_score():
    try:
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)

            if isinstance(data, dict):
                normal = int(data.get('normal', 0))
                hard = int(data.get('hard', 0))
            elif isinstance(data, int):
                normal = data
                hard = 0
            else:
                normal = 0
                hard = 0

            return {'normal': normal, 'hard': hard}
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"Note: High score not loaded ({e})")
        return {'normal': 0, 'hard': 0}

scores = load_high_score()
app.highScoreNormal = scores['normal']
app.highScoreHard = scores['hard']
app.highScore = app.highScoreNormal
app.newHighScore = False

pieceListEasyMode = [
    't', 'O', 'I',
    'L', 'J'
]
pieceList = [
    'Z', 'S', 't', 'O', 'I',
    'L', 'J'
]
pieceListHardMode = [
    'Z', 'S', 't', 'O', 'I',
    'L', 'J', 'U', 'T'
]

tetrisTitleMusic = Sound('assets\\tetris\\sounds\\title.mp3')
tetrisTitleMusic.play(loop=True)
tetrisEndMusic = Sound('assets\\tetris\\sounds\\gameOver.mp3')
tetrisMusic = Sound('assets\\tetris\\sounds\\music.mp3')
rotateSound = Sound('assets\\tetris\\sounds\\rotateSound.wav')
moveSound = Sound('assets\\tetris\\sounds\\move.wav')
rowClearSound = Sound('assets\\tetris\\sounds\\lineClear.wav')

def setVolume():
    tetrisTitleMusic.setVolume(app.volume)
    tetrisEndMusic.setVolume(app.volume)
    tetrisMusic.setVolume(app.volume)
    rotateSound.setVolume(app.volume)
    moveSound.setVolume(app.volume)
    rowClearSound.setVolume(app.volume)
setVolume()




# background stuff, yeah
bg = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))

playfieldWidth = app.cols * app.blockSize
playfieldHeight = int((app.height - app.offsetY) // app.blockSize) * app.blockSize

playfieldPanel = Rect(
    app.offsetX - 10,
    app.offsetY - 10,
    playfieldWidth + 20,
    playfieldHeight + 20,
    fill=gradient('dimGrey', 'black'),
    opacity=80,
    border='white',
    borderWidth=2
)

tiles = Group()

rows = int(playfieldHeight // app.blockSize)

for col in range(app.cols):
    for row in range(rows):

        x = app.offsetX + col * app.blockSize
        y = app.offsetY + row * app.blockSize

        tile = Rect(
            x, y,
            app.blockSize,
            app.blockSize,
            fill=None,
            border=rgb(40, 40, 40),
            borderWidth=1
        )

        inner = Rect(
            x + 1,
            y + 1,
            app.blockSize - 2,
            app.blockSize - 2,
            fill=rgb(20, 20, 20),
            opacity=30
        )

        tiles.add(tile)
        tiles.add(inner)

placedPieces = Group()
ghostPiece = Group()
curPiece = Group()
previewBlocks = Group()

tetrisInGameIconImage = 'assets\\tetris\\images\\logo.png'
tetrisInGameIcon = Image(tetrisInGameIconImage, 0, 0)
tetrisInGameIcon.width = tetrisInGameIcon.width * 0.2
tetrisInGameIcon.height = tetrisInGameIcon.height * 0.2
tetrisInGameIcon.centerX=1100
tetrisInGameIcon.centerY=600


Label("Next Piece:", 1050, 100, size=20, fill="white", bold=True,font='Tears in Rain')
scoreLabel = Label("Score: 0", 1100, 260 + 100, size=18, fill="white", bold=True,font='Tears in Rain')
linesLabel = Label("Lines: 0", 1100, 290 + 100, size=18, fill="white", bold=True,font='Tears in Rain')

levelLabel = Label("Level: 1", 1100, 320 + 100, size=18, fill="white", bold=True,font='Tears in Rain')

timeLabel = Label("Time: 00:00", 1100, 350 + 100, size=18, fill="white", bold=True,font='Tears in Rain')


titleBG = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))
titlePanel = Rect(app.width/2 - 350,15,700,680,fill=gradient('dimGrey', 'black'),opacity=85,border='white',borderWidth=2)
titleIcon = Image(tetrisInGameIconImage,0,0)
titleIcon.width=titleIcon.width*0.5
titleIcon.height=titleIcon.height*0.5
titleIcon.centerX=app.width/2
titleIcon.centerY=250
titleStartText = Label('PRESS "SPACE" TO SELECT MODE',app.width/2,500,fill='white',bold=True,size=30,font='Tears in Rain')
titleControlsText = Label('PRESS "TAB" FOR CONTROLS!',app.width/2,600,fill='white',bold=True,size=30,font='Tears in Rain')
titleGroup = Group(titleBG,titlePanel,titleIcon,titleStartText,titleControlsText)
titleGroup.visible=True

selectionBG = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))
selectionPanel = Rect(app.width/2 - 350,80,700,560,fill=gradient('dimGrey', 'black'),opacity=85,border='white',borderWidth=2)
selectionTitle = Label('SELECT DIFFICULTY & LEVEL',app.width/2,140,fill='white',bold=True,size=34,font='Tears in Rain')
selectionDifficultyText = Label(f'Difficulty: {app.selectedDifficulty}',app.width/2,240,fill='white',bold=True,size=28,font='Tears in Rain')
selectionLevelText = Label(f'Level: {app.selectedLevel}',app.width/2,320,fill='white',bold=True,size=28,font='Tears in Rain')
selectionHelpText = Label('LEFT / RIGHT = Difficulty | UP / DOWN = Level | SPACE = Start',app.width/2,420,fill='white',bold=True,size=17,font='Tears in Rain')
selectionNoteText = Label('Press ESC to go back to title',app.width/2,490,fill='white',bold=True,size=18,font='Tears in Rain')
selectionGroup = Group(selectionBG, selectionPanel, selectionTitle, selectionDifficultyText, selectionLevelText, selectionHelpText, selectionNoteText)
selectionGroup.visible=False

controlsBG = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))
controlsPanel = Rect(app.width/2 - 350,80,700,560,fill=gradient('dimGrey', 'black'),opacity=85,border='white',borderWidth=2)
controlsText = Label("CONTROLS",app.width/2,130,fill='white',bold=True,size=40,font='Tears in Rain')
controlsleft = Label("Left / A : Move Left", app.width/2, 200,fill='white', bold=True, size=24, font='Tears in Rain')
controlsright = Label("Right / D : Move Right", app.width/2, 240,fill='white', bold=True, size=24, font='Tears in Rain')
controlsdown = Label("Down / S : Soft Drop", app.width/2, 280,fill='white', bold=True, size=24, font='Tears in Rain')
controlsdrop = Label("SPACE : Hard Drop", app.width/2, 320,fill='white', bold=True, size=24, font='Tears in Rain')
controlsrotateleft = Label("Z : Rotate Left", app.width/2, 380,fill='white', bold=True, size=24, font='Tears in Rain')
controlsrotateright = Label("X : Rotate Right", app.width/2, 420,fill='white', bold=True, size=24, font='Tears in Rain')
controlsrestart = Label("R : Restart Game", app.width/2, 480,fill='white', bold=True, size=24, font='Tears in Rain')
controlsback = Label("ESC : Back", app.width/2, 520,fill='white', bold=True, size=24, font='Tears in Rain')
controlsGroup = Group(controlsBG,controlsPanel,controlsText,controlsleft,controlsright,controlsdown,controlsdrop,controlsrotateleft,controlsrotateright,controlsrestart,controlsback)
controlsGroup.visible = False


endBG = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))
endPanel = Rect(app.width/2 - 350,15,700,680,fill=gradient('dimGrey', 'black'),opacity=85,border='white',borderWidth=2)
endIcon = Image(tetrisInGameIconImage,0,0)
endIcon.width=endIcon.width*0.5
endIcon.height=endIcon.height*0.5
endIcon.centerX=app.width/2
endIcon.centerY=200
endText = Label('GAME OVER',app.width/2,400,fill='white',bold=True,size=30,font='Tears in Rain')
endScoreText = Label("SCORE: " + str(app.score),endPanel.left + 50,450,fill='white',bold=True,size=30,font='Tears in Rain',align='left')
endLinesText = Label("LINES: " + str(app.linesCleared),endPanel.left + 50,500,fill='white',bold=True,size=30,font='Tears in Rain',align='left')
endLevelText = Label("LEVEL: " + str(app.level),endPanel.left + 50,550,fill='white',bold=True,size=30,font='Tears in Rain',align='left')
endHighScoreText = Label("HIGH SCORE: 0",app.width/2,450,fill='white',bold=True,size=23,font='Tears in Rain',align='left')
endNewHighScoreText = Label("NEW HIGH SCORE!",app.width/2,500,fill='gold',bold=True,size=26,font='Tears in Rain')
endNewHighScoreText.visible = False
endTimeText = Label(timeLabel.value,app.width/2,600,fill='white',bold=True,size=30,font='Tears in Rain')
endRestartText = Label('PRESS "R" TO RESTART',app.width/2,650,fill='white',bold=True,size=30,font='Tears in Rain')
endGroup = Group(endBG, endPanel, endIcon, endText,endScoreText, endLinesText, endLevelText,endTimeText, endRestartText,endHighScoreText, endNewHighScoreText)
endGroup.visible=False


def updateUI():
    scoreLabel.value = f"Score: {app.score}"
    linesLabel.value = f"Lines: {app.linesCleared}"
    levelLabel.value = f"Level: {app.level}"


def updateSelectionLabels():
    selectionDifficultyText.value = f'Difficulty: {app.selectedDifficulty}'
    selectionLevelText.value = f'Level: {app.selectedLevel}'

def changeSelectionDifficulty():
    if app.selectedDifficulty == 'Normal':
        app.selectedDifficulty = 'Hard'
    else:
        app.selectedDifficulty = 'Normal'
    updateSelectionLabels()

def changeSelectionLevel(delta):
    app.selectedLevel = max(1, min(15, app.selectedLevel + delta))
    updateSelectionLabels()

def createBlock(x, y, fillColor, borderColor):
    g = Group()

    base = Rect(x, y, app.blockSize, app.blockSize,
                fill=fillColor, border=borderColor, borderWidth=3)

    shade = Rect(x, y+app.blockSize/2, app.blockSize, app.blockSize/2,
                 fill='black', opacity=15)

    highlight = Rect(x+3, y+3, 20, 10, fill='white', opacity=30)

    inner = Rect(x+4, y+4, app.blockSize-8, app.blockSize-8,
                 fill=None, border='white', borderWidth=1, opacity=40)

    g.fillColor = fillColor
    g.borderColor = borderColor

    g.add(base, shade, highlight, inner)
    return g

def getPieceData(t):
    if t == 'Z':
        return [(0,0),(1,0),(1,1),(2,1)], ('red', 'darkRed')
    if t == 'S':
        return [(1,0),(2,0),(0,1),(1,1)], ('lime', 'limeGreen')
    if t == 't':
        return [(0,0),(1,0),(2,0),(1,1)], ('magenta', 'darkViolet')
    if t == 'O':
        return [(0,0),(1,0),(0,1),(1,1)], ('yellow', 'gold')
    if t == 'I':
        return [(0,0),(0,1),(0,2),(0,3)], ('skyBlue', 'deepSkyBlue')
    if t == 'L':
        return [(0,0),(0,1),(0,2),(1,2)], ('orange', 'tomato')
    if t == 'J':
        return [(1,0),(1,1),(1,2),(0,2)], ('blue', 'midnightBlue')
    if t == 'U':
        return [(0,0),(0,1),(1,1),(2,1),(2,0)], ('turquoise', 'darkTurquoise')
    if t == 'T':
        return [(0,0),(1,0),(2,0),(1,1),(1,2)], ('purple', 'indigo')

def refillBag():
    if app.hardMode == False:
        app.pieceBag = pieceList.copy()
    else:
        app.pieceBag = pieceListHardMode.copy()
    random.shuffle(app.pieceBag)

def getNextPiece():
    if len(app.pieceBag) == 0:
        refillBag()
    return app.pieceBag.pop()

def newPiece(t, mode):
    coords, color = getPieceData(t)

    if mode == 'cur':
        curPiece.clear()

        startX = 550
        startY = 20

        for (x, y) in coords:
            block = createBlock(
                startX + x * app.blockSize,
                startY + y * app.blockSize,
                color[0],
                color[1]
            )
            curPiece.add(block)

    elif mode == 'next':
        previewBlocks.clear()

        previewStartX = 1050
        previewStartY = 140

        for (x, y) in coords:
            block = createBlock(
                previewStartX + x * app.blockSize,
                previewStartY + y * app.blockSize,
                color[0],
                color[1]
            )
            previewBlocks.add(block)

refillBag()

app.currentType = getNextPiece()
app.nextType = getNextPiece()

newPiece(app.currentType, 'cur')
newPiece(app.nextType, 'next')

#checks if the current block can move
def canMove(dx, dy):
    for block in curPiece:
        newX = block.centerX + dx
        newY = block.centerY + dy

        col = int((newX - app.offsetX) // app.blockSize)
        row = int((newY - app.offsetY) // app.blockSize)

        if col < 0 or col >= app.cols:
            return False

        if newY > 720:
            return False

        for placed in placedPieces:
            if placed.centerX == newX and placed.centerY == newY:
                return False

    
    return True

def rotatePiece(direction):
    if len(curPiece) == 0:
        return

    pivot = next(iter(curPiece))

    newPositions = []

    for block in curPiece:
        dx = (block.centerX - pivot.centerX) // app.blockSize
        dy = (block.centerY - pivot.centerY) // app.blockSize

        if direction == "right":
            rx, ry = -dy, dx
        else:
            rx, ry = dy, -dx

        newX = pivot.centerX + rx * app.blockSize
        newY = pivot.centerY + ry * app.blockSize

        newPositions.append([newX, newY])

    def isValid(positions):
        for (x, y) in positions:
            if x < app.offsetX or x > app.offsetX + (app.cols-1)*app.blockSize:
                return False
            if y > 720:
                return False
            for placed in placedPieces:
                if placed.centerX == x and placed.centerY == y:
                    return False
        rotateSound.play(restart=True)        
        return True

    if not isValid(newPositions):

        for dy in [app.blockSize, 2*app.blockSize, 3*app.blockSize]:
            shifted = [(x, y + dy) for (x, y) in newPositions]
            if isValid(shifted):
                newPositions = shifted
                break

        if not isValid(newPositions):
            for dx in [-app.blockSize, app.blockSize, -2*app.blockSize, 2*app.blockSize]:
                shifted = [(x + dx, y) for (x, y) in newPositions]
                if isValid(shifted):
                    newPositions = shifted
                    break

    if not isValid(newPositions):
        return

    for i, block in enumerate(curPiece):
        block.centerX, block.centerY = newPositions[i]

def onKeyPress(key):
    if key == '-':
        if (app.volume > 0):
            app.volume -= 0.1
        setVolume()
        
    if key == '=':
        if (app.volume < 0.5):
            app.volume += 0.1
        setVolume()
        
    if key == 'p':
        restart_program()
        
    if key == 'r':
        if app.playing == 'end':
            # Save high score BEFORE resetting
            currentHigh = app.highScoreHard if app.hardMode else app.highScoreNormal
            if app.score > currentHigh:
                if app.hardMode:
                    app.highScoreHard = app.score
                else:
                    app.highScoreNormal = app.score
                app.highScore = app.score
                save_high_score()

            # Reset game state
            app.score = 0
            app.linesCleared = 0
            app.level = 1   # start at 1, not 0
            app.startTime = None
            app.timerThing = 0

            # Reset pieces
            placedPieces.clear()
            curPiece.clear()
            previewBlocks.clear()
            ghostPiece.clear()

            refillBag()
            app.currentType = getNextPiece()
            app.nextType = getNextPiece()

            newPiece(app.currentType, 'cur')
            newPiece(app.nextType, 'next')

            # Reset UI
            updateUI()
            timeLabel.value = "Time: 00:00"

            # Switch screens
            app.playing = False
            endGroup.visible = False
            titleGroup.visible = True

            # Music handling
            tetrisEndMusic.pause()
            tetrisMusic.pause()
            tetrisTitleMusic.play(loop=True, restart=True)

            app.newHighScore = False
            endNewHighScoreText.visible = False

    if key == 'z':
        if (app.playing == True):
            rotatePiece("left")

    if key == 'x':
        if (app.playing == True):
            rotatePiece("right")
    if key == 'tab':
        if (app.playing == False):
            app.playing = 'controls'
            titleGroup.visible=False
            controlsGroup.visible=True
    if key == 'escape':
        if app.playing == 'controls':
            app.playing = False
            titleGroup.visible=True
            controlsGroup.visible=False
        elif app.playing == 'startMenu':
            app.playing = False
            selectionGroup.visible=False
            titleGroup.visible=True

    if key == 'space':
        if (app.playing == True):    
            dropDistance = 0

            while canMove(0, app.blockSize):
                for b in curPiece:
                    b.centerY += app.blockSize
                dropDistance += 1

            app.score += dropDistance * 2
            lockPiece()
        elif app.playing == 'startMenu':
            app.hardMode = (app.selectedDifficulty == 'Hard')
            app.startLevel = app.selectedLevel
            app.level = app.startLevel
            app.linesCleared = 0
            app.score = 0
            app.startTime = time.time()
            app.timerThing = 0

            placedPieces.clear()
            curPiece.clear()
            previewBlocks.clear()
            ghostPiece.clear()

            refillBag()
            app.currentType = getNextPiece()
            app.nextType = getNextPiece()

            newPiece(app.currentType, 'cur')
            newPiece(app.nextType, 'next')

            updateUI()
            timeLabel.value = "Time: 00:00"

            app.playing = True
            selectionGroup.visible=False
            titleGroup.visible=False
            tetrisTitleMusic.pause()
            tetrisMusic.play(loop=True,restart=True)
        elif (app.playing == False):
            app.playing = 'startMenu'
            titleGroup.visible=False
            selectionGroup.visible=True
            updateSelectionLabels()

    if app.playing == 'startMenu' and key in ['left', 'right', 'a', 'd']:
        changeSelectionDifficulty()
    if app.playing == 'startMenu' and key in ['up']:
        changeSelectionLevel(1)
    if app.playing == 'startMenu' and key in ['down']:
        changeSelectionLevel(-1)

    if key in ['a','left']:
        if (app.playing == True):    
            if canMove(-app.blockSize, 0):
                moveSound.play(restart=True)
                for b in curPiece:
                    b.centerX -= app.blockSize

    if key in ['d','right']:
        if (app.playing == True):
            if canMove(app.blockSize, 0):
                moveSound.play(restart=True)
                for b in curPiece:
                    b.centerX += app.blockSize

    if key in ['s','down']:
        if (app.playing == True):
            if canMove(0, app.blockSize):
                moveSound.play(restart=True)
                for b in curPiece:
                    b.centerY += app.blockSize
                app.score += 1

#Clears the rows if the row is full
def clearRows():
    if (app.playing == True):
        rows = {}

        for block in placedPieces:
            row = int((block.centerY - app.offsetY) // app.blockSize)

            if row not in rows:
                rows[row] = []

            rows[row].append(block)

        fullRows = []

        for row in rows:
            if len(rows[row]) == app.cols:
                fullRows.append(row)

        if len(fullRows) == 0:
            return

        # remove blocks
        for row in fullRows:
            for block in rows[row]:
                placedPieces.remove(block)
                rowClearSound.play(restart=True)

        # drop remaining blocks
        for block in placedPieces:
            row = int((block.centerY - app.offsetY) // app.blockSize)
            drop = 0

            for cleared in fullRows:
                if row < cleared:
                    drop += 1

            block.centerY += drop * app.blockSize

        
        lines = len(fullRows)
        app.linesCleared += lines

        # scoring
        levelMultiplier = app.level + 1

        if lines == 1:
            app.score += 40 * levelMultiplier
        elif lines == 2:
            app.score += 100 * levelMultiplier
        elif lines == 3:
            app.score += 300 * levelMultiplier
        elif lines == 4:
            app.score += 1200 * levelMultiplier

        app.level = app.startLevel + (app.linesCleared // 10)

        # update labels
        scoreLabel.value = f"Score: {app.score}"
        linesLabel.value = f"Lines: {app.linesCleared}"
        levelLabel.value = f"Level: {app.level}"

#locks pieces in place when they can no longer move
def gameOver():
    app.playing = 'end'
    tetrisMusic.pause()
    endGroup.visible = True
    tetrisEndMusic.play(restart=True, loop=True)

    currentHigh = app.highScoreHard if app.hardMode else app.highScoreNormal
    if app.score > currentHigh:
        if app.hardMode:
            app.highScoreHard = app.score
        else:
            app.highScoreNormal = app.score
        app.highScore = app.score
        app.newHighScore = True
        save_high_score()
    else:
        app.highScore = currentHigh
        app.newHighScore = False

    endHighScoreText.value = f"HIGH SCORE: {app.highScore}"
    endNewHighScoreText.visible = app.newHighScore


def lockPiece():
    if (app.playing == True):
        for block in curPiece:
            placedPieces.add(block)

        curPiece.clear()

        clearRows()

        app.currentType = app.nextType
        app.nextType = getNextPiece()

        newPiece(app.currentType, 'cur')
        newPiece(app.nextType, 'next')

        if not canMove(0, 0):
            gameOver()
            return


def updateGhost():
    if (app.playing == True):
        ghostPiece.clear()

        if len(curPiece) == 0:
            return

        maxDrop = 40
        drop = 0

        while drop < maxDrop:
            canDrop = True

            for block in curPiece:
                newX = block.centerX
                newY = block.centerY + (drop + 1) * app.blockSize

                col = int((newX - app.offsetX) // app.blockSize)
                row = int((newY - app.offsetY) // app.blockSize)

                if col < 0 or col >= app.cols:
                    canDrop = False
                    break

                if newY > 720:
                    canDrop = False
                    break

                for placed in placedPieces:
                    if placed.centerX == newX and placed.centerY == newY:
                        canDrop = False
                        break

            if not canDrop:
                break

            drop += 1

        
        for block in curPiece:
            # convert block position → grid
            col = int((block.centerX - app.offsetX) // app.blockSize)
            row = int((block.centerY - app.offsetY) // app.blockSize)

            # apply drop to row
            ghostRow = row + drop

            # convert grid → pixel (THIS is the important fix)
            ghostX = app.offsetX + col * app.blockSize + app.blockSize / 2
            ghostY = app.offsetY + ghostRow * app.blockSize + app.blockSize / 2

            ghostBlock = createBlock(
                ghostX-25,
                ghostY-25,
                block.fillColor,
                block.borderColor
            )

            ghostBlock.opacity = 25
            ghostBlock.children[0].opacity = 10
            ghostBlock.children[1].opacity = 5
            ghostBlock.children[2].opacity = 10
            ghostBlock.children[3].opacity = 10

            ghostPiece.add(ghostBlock)

def onStep():
    if (app.playing == True):
        updateUI()
        endScoreText.left = endPanel.left + 50
        endLinesText.left = endPanel.left + 50
        endLevelText.left = endPanel.left + 50
        endTimeText.left = endPanel.left + 50
        endHighScoreText.right = endPanel.right - 50
        endNewHighScoreText.right = endPanel.right - 50

        if (curPiece.top < 20):
            curPiece.top = 20
        if (placedPieces.top == 20):
            app.playing = 'end'
            tetrisMusic.pause()
            endGroup.visible = True
            tetrisEndMusic.play(restart=True, loop=True)

            # Check high score
            currentHigh = app.highScoreHard if app.hardMode else app.highScoreNormal
            if app.score > currentHigh:
                if app.hardMode:
                    app.highScoreHard = app.score
                else:
                    app.highScoreNormal = app.score
                app.highScore = app.score
                app.newHighScore = True
                save_high_score()
            else:
                app.highScore = currentHigh
                app.newHighScore = False

            # Update end screen text
            endHighScoreText.value = f"HIGH SCORE: {app.highScore}"
            endNewHighScoreText.visible = app.newHighScore

        endLinesText.value = 'LINES: ' + str(app.linesCleared)
        endScoreText.value = 'SCORE: ' + str(app.score)
        endLevelText.value = 'LEVEL: ' + str(app.level)
        previewBlocks.centerX=1100
        app.timerThing += 1
        updateGhost()

        if app.startTime != None:
            elapsedSeconds = int(time.time() - app.startTime)
        else:
            elapsedSeconds = 0

        minutes = elapsedSeconds // 60
        seconds = elapsedSeconds % 60

        timeLabel.value = f"Time: {minutes:02}:{seconds:02}"
        endTimeText.value = f"Time: {minutes:02}:{seconds:02}".upper()
        speed = max(3, 18 - app.level * 2)

        if app.timerThing >= speed:
            app.timerThing = 0

            if canMove(0, app.blockSize):
                for b in curPiece:
                    b.centerY += app.blockSize
            else:
                lockPiece()
    if app.playing == 'end' and app.newHighScore:
        app.steps += 1
        endNewHighScoreText.opacity = 50 + 50 * abs(math.sin(app.steps * 0.15))

cmu_graphics.run()
