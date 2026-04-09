#Goofy tetris code :3
#This code is for my final project for my advanced coding class.
#The final project was going to be a fnf remake, but that would take way too long to work on, so I am choosing this :3
#IDK how long this dang thing will take to finish, but I don't care. As long as I can finish it before the end of the school year lol
#If you make the screen size larger than 1280x740, it may look wrong, soooooo just keep it like it is currently :3
#I'm too lazy to add good comments so don't expext super orginized comments lol

from cmu_graphics import *
import os
import sys
import random
import time

#Restarts program so I dont have to mess with closing and opening the exe thing again
def restart_program():
    python = sys.executable
    os.execv(python, [python] + sys.argv)

#vars
app.width = 1280
app.height = 740

app.level = 1
app.playing = False
app.steps = 0
app.stepCount = 0
app.score = 0
app.linesCleared = 0
app.startTime = time.time()
app.moveDelay = 0
app.moveCooldown = 5
app.blockSize = 50
app.offsetX = 400
app.offsetY = 20
app.cols = 10
app.timerThing = 0

pieceList = ['Z', 'S', 'T', 'O', 'I', 'L', 'J', 'U', '+','b','d']

tetrisTitleMusic = Sound('assets\\tetris\\sounds\\title.mp3')
tetrisTitleMusic.play(loop=True)
tetrisEndMusic = Sound('assets\\tetris\\sounds\\gameOver.mp3')
tetrisMusic = Sound('assets\\tetris\\sounds\\music.mp3')
rotateSound = Sound('assets\\tetris\\sounds\\rotateSound.wav')
moveSound = Sound('assets\\tetris\\sounds\\move.wav')
rowClearSound = Sound('assets\\tetris\\sounds\\lineClear.wav')

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


Label("Next Piece:", 1050, 100, size=20, fill="white", bold=True,font='tetris')
scoreLabel = Label("Score: 0", 1100, 260 + 100, size=18, fill="white", bold=True,font='tetris')
linesLabel = Label("Lines: 0", 1100, 290 + 100, size=18, fill="white", bold=True,font='tetris')
timeLabel = Label("Time: 00:00", 1100, 320 + 100, size=18, fill="white", bold=True,font='tetris')

titleBG = Rect(0,0,app.width,app.height)
titleIcon = Image(tetrisInGameIconImage,0,0)
titleIcon.width=titleIcon.width*0.5
titleIcon.height=titleIcon.height*0.5
titleIcon.centerX=app.width/2
titleIcon.centerY=200
titleStartText = Label('PRESS "SPACE" TO START!',app.width/2,500,fill='white',bold=True,size=30,font='tetris')
titleGroup = Group(titleBG,titleIcon,titleStartText)
titleGroup.visible=True

endBG = Rect(0,0,app.width,app.height)
endIcon = Image(tetrisInGameIconImage,0,0)
endIcon.width=endIcon.width*0.5
endIcon.height=endIcon.height*0.5
endIcon.centerX=app.width/2
endIcon.centerY=200
endText = Label('GAME OVER',app.width/2,400,fill='white',bold=True,size=30,font='tetris')
endScoreText = Label("SCORE: " + str(app.score),app.width/2,450,fill='white',bold=True,size=30,font='tetris')
endLinesText = Label("LINES: " + str(app.linesCleared),app.width/2,500,fill='white',bold=True,size=30,font='tetris')
endTimeText = Label(timeLabel.value,app.width/2,550,fill='white',bold=True,size=30,font='tetris')
endRestartText = Label('PRESS "P" TO RESTART',app.width/2,650,fill='white',bold=True,size=30,font='tetris')

endGroup = Group(endBG,endIcon,endText,endScoreText,endLinesText,endTimeText,endRestartText)
endGroup.visible=False

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
        return [(0,0),(1,0),(1,1),(2,1)], ('red','darkRed')
    if t == 'S':
        return [(1,0),(2,0),(0,1),(1,1)], ('lime','limeGreen')
    if t == 'T':
        return [(0,0),(1,0),(2,0),(1,1)], ('magenta','darkViolet')
    if t == 'O':
        return [(0,0),(1,0),(0,1),(1,1)], ('yellow','gold')
    if t == 'I':
        return [(0,0),(0,1),(0,2),(0,3)], ('skyBlue','deepSkyBlue')
    if t == 'L':
        return [(0,0),(0,1),(0,2),(1,2)], ('orange','tomato')
    if t == 'J':
        return [(1,0),(1,1),(1,2),(0,2)], ('blue','midnightBlue')
    if t == 'U':
        return [(0,0),(0,1),(1,1),(2,1),(2,0)], ('darkOrange','orangeRed')
    if t == '+':
        return [(0,1),(1,0),(1,1),(2,1),(1,2)], (None,'black')
    if t == 'b':
        return [(0,0),(0,1),(0,2),(1,1),(1,2)], ('darkTurquoise','royalBlue')
    if t == 'd':
        return [(0,1),(0,2),(1,0),(1,1),(1,2)], (None,'black')

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

app.rand1 = random.randint(0, 10)
app.rand2 = random.randint(0, 10)

newPiece(pieceList[app.rand1], 'cur')
newPiece(pieceList[app.rand2], 'next')

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
    if key == 'p':
        restart_program()

    if key == 'z':
        if (app.playing == True):
            rotatePiece("left")

    if key == 'x':
        if (app.playing == True):
            rotatePiece("right")
    if key == 'space':
        if (app.playing == True):    
            while canMove(0, app.blockSize):
                for b in curPiece:
                    b.centerY += app.blockSize
            lockPiece()
        if (app.playing == False):
            app.playing = True
            titleGroup.visible=False
            tetrisTitleMusic.pause()
            tetrisMusic.play(loop=True,restart=True)

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
        if lines == 1:
            app.score += 100
        elif lines == 2:
            app.score += 300
        elif lines == 3:
            app.score += 500
        elif lines == 4:
            app.score += 800

        # update labels
        scoreLabel.value = f"Score: {app.score}"
        linesLabel.value = f"Lines: {app.linesCleared}"

#locks pieces in place when they can no longer move
def lockPiece():
    if (app.playing == True):
        for block in curPiece:
            placedPieces.add(block)

        curPiece.clear()

        app.rand1 = app.rand2
        if (app.level)
        app.rand2 = random.randint(0, 10)

        newPiece(pieceList[app.rand1], 'cur')
        newPiece(pieceList[app.rand2], 'next')

        clearRows()

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
        if (curPiece.top < 20):
            curPiece.top = 20
        if (placedPieces.top == 20):
            app.playing = 'end'
            tetrisMusic.pause()
            endGroup.visible=True
            tetrisEndMusic.play(restart=True,loop=True)

        endLinesText.value = 'LINES: ' + str(app.linesCleared)
        endScoreText.value = 'SCORE: ' + str(app.score)
        previewBlocks.centerX=1100
        app.timerThing += 1
        updateGhost()

        elapsedSeconds = int(time.time() - app.startTime)

        minutes = elapsedSeconds // 60
        seconds = elapsedSeconds % 60

        timeLabel.value = f"Time: {minutes:02}:{seconds:02}"
        endTimeText.value = f"Time: {minutes:02}:{seconds:02}".upper()

        if app.timerThing >= 20:
            app.timerThing = 0

            if canMove(0, app.blockSize):
                for b in curPiece:
                    b.centerY += app.blockSize
            else:
                lockPiece()

cmu_graphics.run()
