#Goofy tetris code :3
#This code is for my final project for my advanced coding class.
#The final project was going to be a fnf remake, but that would take way too long to work on, so I am choosing this :3
#IDK how long this dang thing will take to finish, but I don't care. As long as I can finish it before the end of the school year lol
#If you make the screen size larger than 1280x740, it may look wrong, soooooo keep it like it is currently :3
#I'm too lazy to add good comments, so don't expect super organized comments lol

from cmu_graphics import *
from cmu_graphics import pygameEvent
from cmu_graphics.libs import pygame_loader as pygame
import os
import sys
import random
import time
import math
import json
import subprocess


# Use python versions v3.10.8 - v3.12.0
# Optionally terminate other Python processes at startup (use with caution)
try:
    from kill_other_pythons import kill_other_python_processes
    try:
        # Set dry_run=True to only list targets without terminating them
        kill_other_python_processes(dry_run=False)
    except Exception as _e:
        print('Warning: could not kill other Python processes:', _e)
except Exception:
    # If helper or psutil not available, continue silently
    pass
# Helper to launch other python scripts without showing a console window
try:
    from launch_hidden import launch_python_hidden
except Exception:
    launch_python_hidden = None

#Restarts program so I don't have to mess with closing and opening the exe thing again
def restart_program():
    script = os.path.abspath(__file__)
    subprocess.Popen([sys.executable, script], cwd=os.path.dirname(script))
    os._exit(0)

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
app.heldType = None
app.canHold = True
app.unlockedAchievements = set()
app.achievementQueue = []
app.achievementPopupPhase = 'hidden'
app.achievementPopupTimer = 0
app.konamiProgress = 0
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
app.layoutOffsetY = 0
app.previousWindowWidth = app.width
app.previousWindowHeight = app.height
app.fullscreen = False
app.windowedSize = (app.width, app.height)
app.cols = 10
app.timerThing = 0

MAX_SELECTABLE_LEVEL = 15
CLASSIC_TETRIS_MAX_LEVEL = 29
KONAMI_CODE = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right', 'b', 'a']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, 'data', 'Tetris', 'save.txt')

def save_high_score():
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, 'w') as file:
        json.dump({
            'easy': app.highScoreEasy,
            'normal': app.highScoreNormal,
            'hard': app.highScoreHard
        }, file)

def load_high_score():
    try:
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)

            if isinstance(data, dict):
                easy = int(data.get('easy', 0))
                normal = int(data.get('normal', 0))
                hard = int(data.get('hard', 0))
            elif isinstance(data, int):
                easy = 0
                normal = data
                hard = 0
            else:
                easy = 0
                normal = 0
                hard = 0

            return {'easy': easy, 'normal': normal, 'hard': hard}
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"Note: High score not loaded ({e})")
        return {'normal': 0, 'hard': 0}

scores = load_high_score()
app.highScoreEasy = scores['easy']
app.highScoreNormal = scores['normal']
app.highScoreHard = scores['hard']
app.highScore = app.highScoreNormal
app.newHighScore = False
app.currentDifficulty = app.selectedDifficulty

pieceListEasyMode = [
    't', 'I','L', 'J'
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
app.background = gradient('black', 'midnightBlue', start='top')

playfieldWidth = app.cols * app.blockSize
playfieldHeight = int((app.height - app.offsetY) // app.blockSize) * app.blockSize
PLAYFIELD_BOTTOM = 720

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
holdPieceBlocks = Group()

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

holdBox = Rect(app.offsetX - 380, app.offsetY + 80, 260, 210, fill='black', opacity=35, border='white', borderWidth=2)
holdTitle = Label('HOLD (C)', app.offsetX - 250, app.offsetY + 115, size=22, fill='white', bold=True, font='Tears in Rain')
holdEmptyText = Label('EMPTY', app.offsetX - 250, app.offsetY + 205, size=18, fill='grey', bold=True, font='Tears in Rain')
holdUIGroup = Group(holdBox, holdTitle, holdEmptyText, holdPieceBlocks)
holdUIGroup.visible = False

pauseBG = Rect(0, 0, app.width, app.height, fill='black', opacity=65)
pausePanel = Rect(app.width / 2 - 250, app.height / 2 - 110, 500, 220, fill=gradient('dimGrey', 'black'), opacity=95, border='white', borderWidth=2)
pauseTitle = Label('PAUSED', app.width / 2, app.height / 2 - 45, fill='gold', bold=True, size=38, font='Tears in Rain')
pauseInstructions = Label('PRESS ENTER TO RESUME', app.width / 2, app.height / 2 + 30, fill='white', bold=True, size=22, font='Tears in Rain')
pauseGroup = Group(pauseBG, pausePanel, pauseTitle, pauseInstructions)
pauseGroup.visible = False

titleBG = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))
titlePanel = Rect(app.width/2 - 350,30,700,680,fill=gradient('dimGrey', 'black'),opacity=85,border='white',borderWidth=2)
titleIcon = Image(tetrisInGameIconImage,0,0)
titleIcon.width=titleIcon.width*0.5
titleIcon.height=titleIcon.height*0.5
titleIcon.centerX=app.width/2
titleIcon.centerY=265
titleAltPlay = Label('NOW AVALABLE ON ARCADE OUTSIDE!',app.width/2,505,fill='yellow',bold=True,size=30,font='Tears in Rain')
titleStartText = Label('PRESS "SPACE" TO SELECT MODE',app.width/2,565,fill='white',bold=True,size=30,font='Tears in Rain')
titleControlsText = Label('PRESS "TAB" FOR CONTROLS!',app.width/2,615,fill='white',bold=True,size=30,font='Tears in Rain')
titleFullscreenText = Label('F11: TOGGLE FULLSCREEN',app.width/2,660,fill='white',bold=True,size=18,font='Tears in Rain')
titleContentGroup = Group(titlePanel,titleIcon,titleStartText,titleControlsText,titleAltPlay,titleFullscreenText)
titleGroup = Group(titleBG,titleContentGroup)
titleGroup.visible=True

selectionBG = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))
selectionPanel = Rect(app.width/2 - 350,90,700,560,fill=gradient('dimGrey', 'black'),opacity=85,border='white',borderWidth=2)
selectionTitle = Label('SELECT DIFFICULTY & LEVEL',app.width/2,150,fill='white',bold=True,size=34,font='Tears in Rain')
selectionDifficultyText = Label(f'Difficulty: {app.selectedDifficulty}',app.width/2,250,fill='white',bold=True,size=28,font='Tears in Rain')
selectionLevelText = Label(f'Level: {app.selectedLevel}',app.width/2,330,fill='white',bold=True,size=28,font='Tears in Rain')
selectionHelpText = Label('LEFT / RIGHT = Difficulty | UP / DOWN = Level | SPACE = Start',app.width/2,430,fill='white',bold=True,size=17,font='Tears in Rain')
selectionNoteText = Label('Press ESC to go back to title',app.width/2,500,fill='white',bold=True,size=18,font='Tears in Rain')
selectionContentGroup = Group(
    selectionPanel, selectionTitle, selectionDifficultyText, selectionLevelText,
    selectionHelpText, selectionNoteText
)
selectionGroup = Group(selectionBG, selectionContentGroup)
selectionGroup.visible=False

controlsBG = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))
controlsPanel = Rect(app.width/2 - 350,90,700,560,fill=gradient('dimGrey', 'black'),opacity=85,border='white',borderWidth=2)
controlsText = Label("CONTROLS",app.width/2,140,fill='white',bold=True,size=40,font='Tears in Rain')
controlsleft = Label("Left / A : Move Left", app.width/2, 210,fill='white', bold=True, size=24, font='Tears in Rain')
controlsright = Label("Right / D : Move Right", app.width/2, 250,fill='white', bold=True, size=24, font='Tears in Rain')
controlsdown = Label("Down / S : Soft Drop", app.width/2, 290,fill='white', bold=True, size=24, font='Tears in Rain')
controlsdrop = Label("SPACE : Hard Drop", app.width/2, 330,fill='white', bold=True, size=24, font='Tears in Rain')
controlsrotateleft = Label("Z : Rotate Left", app.width/2, 390,fill='white', bold=True, size=24, font='Tears in Rain')
controlsrotateright = Label("X : Rotate Right", app.width/2, 430,fill='white', bold=True, size=24, font='Tears in Rain')
controlshold = Label("C : Hold Piece (once per piece)", app.width/2, 470,fill='white', bold=True, size=24, font='Tears in Rain')
controlspause = Label("ENTER : Pause / Resume", app.width/2, 510,fill='white', bold=True, size=24, font='Tears in Rain')
controlsrestart = Label("R : Restart Game", app.width/2, 550,fill='white', bold=True, size=24, font='Tears in Rain')
controlsback = Label("ESC : Back", app.width/2, 590,fill='white', bold=True, size=24, font='Tears in Rain')
controlsContentGroup = Group(
    controlsPanel, controlsText, controlsleft, controlsright, controlsdown,
    controlsdrop, controlsrotateleft, controlsrotateright, controlsrestart,
    controlshold, controlspause, controlsback
)
controlsGroup = Group(controlsBG, controlsContentGroup)
controlsGroup.visible = False


endBG = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))
endPanel = Rect(app.width/2 - 350,30,700,680,fill=gradient('dimGrey', 'black'),opacity=85,border='white',borderWidth=2)
endIcon = Image(tetrisInGameIconImage,0,0)
endIcon.width=endIcon.width*0.5
endIcon.height=endIcon.height*0.5
endIcon.centerX=app.width/2
endIcon.centerY=215
endText = Label('GAME OVER',app.width/2,415,fill='white',bold=True,size=30,font='Tears in Rain')
endScoreText = Label("SCORE: " + str(app.score),endPanel.left + 50,465,fill='white',bold=True,size=30,font='Tears in Rain',align='left')
endLinesText = Label("LINES: " + str(app.linesCleared),endPanel.left + 50,515,fill='white',bold=True,size=30,font='Tears in Rain',align='left')
endLevelText = Label("LEVEL: " + str(app.level),endPanel.left + 50,565,fill='white',bold=True,size=30,font='Tears in Rain',align='left')
endHighScoreText = Label("HIGH SCORE: 0",app.width/2,465,fill='white',bold=True,size=23,font='Tears in Rain',align='left')
endNewHighScoreText = Label("NEW HIGH SCORE!",app.width/2,515,fill='gold',bold=True,size=26,font='Tears in Rain')
endNewHighScoreText.visible = False
endTimeText = Label(timeLabel.value,app.width/2,615,fill='white',bold=True,size=30,font='Tears in Rain')
endRestartButton = Rect(285, 640, 300, 55, fill=gradient('dimGrey', 'black'), border='white', borderWidth=2)
endRestartText = Label('PRESS "R" TO RESTART',435,667,fill='white',bold=True,size=20,font='Tears in Rain')
endAchievementsButton = Rect(625, 640, 370, 55, fill=gradient('darkSlateBlue', 'black'), border='gold', borderWidth=2)
endAchievementsText = Label('ACHIEVEMENTS',810,667,fill='gold',bold=True,size=22,font='Tears in Rain')
endContentGroup = Group(
    endPanel, endIcon, endText, endScoreText, endLinesText, endLevelText,
    endTimeText, endRestartButton, endRestartText, endAchievementsButton,
    endAchievementsText, endHighScoreText, endNewHighScoreText
)
endGroup = Group(endBG, endContentGroup)
endGroup.visible=False

ACHIEVEMENTS = {
    'first-line': ('First Line', 'Clear your first line.'),
    'double-clear': ('Double Trouble', 'Clear two lines at once.'),
    'triple-clear': ('Triple Threat', 'Clear three lines at once.'),
    'tetris-clear': ('TETRIS!', 'Clear four lines at once.'),
    'score-1000': ('Getting Started', 'Reach 1,000 points.'),
    'score-5000': ('Five Grand', 'Reach 5,000 points.'),
    'score-10000': ('Five Digits', 'Reach 10,000 points.'),
    'level-10': ('Seasoned Stacker', 'Reach level 10.'),
    'level-20': ('High-Rise', 'Reach level 20.'),
    'classic-level-29': ('Classic Kill Screen', 'Reach the classic Tetris level 29.'),
    'high-score': ('Record Breaker', 'Beat the high score on any difficulty.'),
    'konami-code': ('Codebreaker', 'Enter the Konami code.'),
    'first-hold': ('Plan B', 'Use the hold slot for the first time.'),
    'hard-level-15-20000': ('Hardcore Climber', 'Score 20,000 in Hard, starting at level 15.')
}

achievementMenuBG = Rect(0, 0, app.width, app.height, fill=gradient('black', 'midnightBlue', start='top'))
achievementMenuPanel = Rect(120, 15, 1040, 710, fill=gradient('dimGrey', 'black'), opacity=90, border='gold', borderWidth=2)
achievementMenuTitle = Label('ACHIEVEMENTS', app.width / 2, 65, fill='gold', bold=True, size=38, font='Tears in Rain')
achievementMenuCount = Label('', app.width / 2, 115, fill='white', bold=True, size=20, font='Tears in Rain')
achievementMenuStatuses = {}
achievementMenuDetails = {}
achievementMenuItems = []
for achievementIndex, (achievementId, achievementData) in enumerate(ACHIEVEMENTS.items()):
    column = achievementIndex // 7
    row = achievementIndex % 7
    itemX = 145 + column * 500
    itemY = 150 + row * 68
    itemBG = Rect(itemX, itemY, 475, 58, fill='black', opacity=55, border='dimGrey')
    itemTitle = Label(achievementData[0], itemX + 12, itemY + 18, fill='white', bold=True, size=16, font='Tears in Rain', align='left')
    itemDescription = Label(achievementData[1], itemX + 12, itemY + 41, fill='lightGrey', size=12, font='Tears in Rain', align='left')
    itemStatus = Label('LOCKED', itemX + 462, itemY + 18, fill='grey', bold=True, size=11, font='Tears in Rain', align='right')
    achievementMenuStatuses[achievementId] = itemStatus
    achievementMenuDetails[achievementId] = (
        itemTitle, itemDescription, achievementData, itemX + 12
    )
    achievementMenuItems.extend([itemBG, itemTitle, itemDescription, itemStatus])

achievementMenuBackButton = Rect(475, 660, 330, 48, fill=gradient('dimGrey', 'black'), border='white', borderWidth=2)
achievementMenuBackText = Label('BACK TO GAME OVER', 640, 684, fill='white', bold=True, size=20, font='Tears in Rain')
achievementMenuContentGroup = Group(
    achievementMenuPanel, achievementMenuTitle,
    achievementMenuCount, achievementMenuBackButton, achievementMenuBackText
)
for achievementMenuItem in achievementMenuItems:
    achievementMenuContentGroup.add(achievementMenuItem)
achievementMenuGroup = Group(achievementMenuBG, achievementMenuContentGroup)
achievementMenuGroup.visible = False

achievementPopupBG = Rect(
    10, 30, 380, 100,
    fill=gradient('darkSlateBlue', 'black', start='left'),
    border='gold', borderWidth=2, opacity=0
)
achievementPopupTitle = Label(
    'ACHIEVEMENT UNLOCKED!', 200, 60, fill='gold', bold=True, size=18,
    font='Tears in Rain', opacity=0
)
achievementPopupDescription = Label(
    '', 200, 98, fill='white', size=13,
    font='Tears in Rain', opacity=0
)
achievementPopup = Group(
    achievementPopupBG, achievementPopupTitle, achievementPopupDescription
)
achievementPopup.visible = False


def onResize():
    deltaX = (app.width - app.previousWindowWidth) / 2
    deltaY = (app.height - app.previousWindowHeight) / 2

    app.group.centerX += deltaX
    app.group.centerY += deltaY
    app.offsetX += deltaX
    app.offsetY += deltaY
    app.layoutOffsetY += deltaY

    for menuContent in (
            titleContentGroup, selectionContentGroup, controlsContentGroup,
            endContentGroup, achievementMenuContentGroup):
        menuContent.centerX = app.width / 2
        menuContent.centerY = app.height / 2

    for background in (
            bg, titleBG, selectionBG, controlsBG, endBG, achievementMenuBG):
        background.left = 0
        background.top = 0
        background.width = app.width
        background.height = app.height

    app.previousWindowWidth = app.width
    app.previousWindowHeight = app.height
    if not app.fullscreen:
        app.windowedSize = (app.width, app.height)


def toggleFullscreen(event, _callUserFn, _wrapper):
    if event.type != pygame.KEYDOWN or event.key != pygame.K_F11:
        return

    if app.fullscreen:
        width, height = app.windowedSize
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        app.fullscreen = False
    else:
        app.windowedSize = (app.width, app.height)
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        app.fullscreen = True

    app._app._screen = screen
    width, height = screen.get_size()
    pygame.event.post(pygame.event.Event(
        pygame.VIDEORESIZE,
        {'size': (width, height), 'w': width, 'h': height}
    ))


pygameEvent.connect(toggleFullscreen)


def unlockAchievement(achievementId):
    if achievementId in app.unlockedAchievements:
        return

    app.unlockedAchievements.add(achievementId)
    app.achievementQueue.append(achievementId)


def resetRunAchievements():
    app.unlockedAchievements.clear()
    app.achievementQueue.clear()
    app.konamiProgress = 0
    app.achievementPopupPhase = 'hidden'
    app.achievementPopupTimer = 0
    achievementPopup.visible = False
    achievementPopupBG.opacity = 0
    achievementPopupTitle.opacity = 0
    achievementPopupDescription.opacity = 0


def showAchievementMenu():
    for achievementId, statusLabel in achievementMenuStatuses.items():
        isUnlocked = achievementId in app.unlockedAchievements
        titleLabel, descriptionLabel, achievementData, descriptionLeft = achievementMenuDetails[achievementId]
        statusLabel.value = 'UNLOCKED' if isUnlocked else 'LOCKED'
        statusLabel.fill = 'limeGreen' if isUnlocked else 'grey'
        titleLabel.value = achievementData[0]
        descriptionLabel.value = achievementData[1] if isUnlocked else '???'
        descriptionLabel.left = descriptionLeft

    achievementMenuCount.value = (
        f'{len(app.unlockedAchievements)} / {len(ACHIEVEMENTS)} UNLOCKED'
    )
    endGroup.visible = False
    achievementMenuGroup.visible = True
    app.playing = 'achievements'


def hideAchievementMenu():
    achievementMenuGroup.visible = False
    endGroup.visible = True
    app.playing = 'end'


def updateAchievementPopup():
    phase = app.achievementPopupPhase
    timer = app.achievementPopupTimer

    if phase == 'hidden':
        if not app.achievementQueue:
            return

        title, description = ACHIEVEMENTS[app.achievementQueue.pop(0)]
        achievementPopupDescription.value = f'{title}: {description}'
        achievementPopup.visible = True
        app.achievementPopupPhase = 'fade-in'
        app.achievementPopupTimer = 0
        return

    timer += 1
    app.achievementPopupTimer = timer

    if phase == 'fade-in':
        opacity = min(100, timer * 10)
        if opacity == 100:
            app.achievementPopupPhase = 'hold'
            app.achievementPopupTimer = 0
    elif phase == 'hold':
        opacity = 100
        if timer >= 75:
            app.achievementPopupPhase = 'fade-out'
            app.achievementPopupTimer = 0
    else:
        opacity = max(0, 100 - timer * 10)
        if opacity == 0:
            achievementPopup.visible = False
            app.achievementPopupPhase = 'hidden'
            app.achievementPopupTimer = 0

    achievementPopupBG.opacity = opacity
    achievementPopupTitle.opacity = opacity
    achievementPopupDescription.opacity = opacity


def getHighScoreForDifficulty(difficulty):
    if difficulty == 'Easy':
        return app.highScoreEasy
    if difficulty == 'Hard':
        return app.highScoreHard
    return app.highScoreNormal


def checkAchievementProgress():
    if app.score >= 1000:
        unlockAchievement('score-1000')
    if app.score >= 5000:
        unlockAchievement('score-5000')
    if app.score >= 10000:
        unlockAchievement('score-10000')
    if app.level >= 10:
        unlockAchievement('level-10')
    if app.level >= 20:
        unlockAchievement('level-20')
    if app.level >= CLASSIC_TETRIS_MAX_LEVEL:
        unlockAchievement('classic-level-29')
    if app.score > getHighScoreForDifficulty(app.currentDifficulty):
        unlockAchievement('high-score')
    if (app.currentDifficulty == 'Hard'
            and app.startLevel == MAX_SELECTABLE_LEVEL
            and app.score >= 20000):
        unlockAchievement('hard-level-15-20000')


def updateUI():
    scoreLabel.value = f"Score: {app.score}"
    linesLabel.value = f"Lines: {app.linesCleared}"
    levelLabel.value = f"Level: {app.level}"
    checkAchievementProgress()


def updateSelectionLabels():
    selectionDifficultyText.value = f'Difficulty: {app.selectedDifficulty}'
    selectionLevelText.value = f'Level: {app.selectedLevel}'

def changeSelectionDifficulty(direction):
    difficulties = ['Easy', 'Normal', 'Hard']
    current_index = difficulties.index(app.selectedDifficulty)
    if direction == 'next':
        new_index = (current_index + 1) % len(difficulties)
    elif direction == 'prev':
        new_index = (current_index - 1) % len(difficulties)
    app.selectedDifficulty = difficulties[new_index]
    updateSelectionLabels()

def changeSelectionLevel(delta):
    app.selectedLevel = max(1, min(MAX_SELECTABLE_LEVEL, app.selectedLevel + delta))
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
    if app.currentDifficulty == 'Easy':
        app.pieceBag = pieceListEasyMode.copy()
    elif app.currentDifficulty == 'Hard':
        app.pieceBag = pieceListHardMode.copy()
    else:
        app.pieceBag = pieceList.copy()
    random.shuffle(app.pieceBag)

def getNextPiece():
    if len(app.pieceBag) == 0:
        refillBag()
    return app.pieceBag.pop()

def newPiece(t, mode):
    coords, color = getPieceData(t)

    if mode == 'cur':
        curPiece.clear()

        startX = app.offsetX + 150
        startY = app.offsetY

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

        previewStartX = app.offsetX + 650
        previewStartY = app.offsetY + 120

        for (x, y) in coords:
            block = createBlock(
                previewStartX + x * app.blockSize,
                previewStartY + y * app.blockSize,
                color[0],
                color[1]
            )
            previewBlocks.add(block)


def updateHoldDisplay():
    holdPieceBlocks.clear()
    holdEmptyText.visible = app.heldType is None
    if app.heldType is None:
        return

    coords, color = getPieceData(app.heldType)
    startX = app.offsetX - 325
    startY = app.offsetY + 145
    for x, y in coords:
        holdPieceBlocks.add(createBlock(
            startX + x * app.blockSize,
            startY + y * app.blockSize,
            color[0],
            color[1]
        ))


def holdCurrentPiece():
    if app.playing != True or not app.canHold:
        return

    unlockAchievement('first-hold')
    app.canHold = False
    ghostPiece.clear()
    if app.heldType is None:
        app.heldType = app.currentType
        app.currentType = app.nextType
        app.nextType = getNextPiece()
        newPiece(app.nextType, 'next')
    else:
        app.currentType, app.heldType = app.heldType, app.currentType

    newPiece(app.currentType, 'cur')
    updateHoldDisplay()
    if not canMove(0, 0):
        gameOver()
        return
    updateGhost()


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

        if newY > PLAYFIELD_BOTTOM + app.layoutOffsetY:
            return False

        for placed in placedPieces:
            if placed.centerX == newX and placed.centerY == newY:
                return False

    
    return True

def rotatePiece(direction):
    if len(curPiece) == 0:
        return

    if app.currentType == 'O':
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
            if y > PLAYFIELD_BOTTOM + app.layoutOffsetY:
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

def onMousePress(mouseX, mouseY, button):
    if button != 0:
        return

    if app.playing == 'end':
        if (endAchievementsButton.left <= mouseX <= endAchievementsButton.right
                and endAchievementsButton.top <= mouseY <= endAchievementsButton.bottom):
            showAchievementMenu()
    elif app.playing == 'achievements':
        if (achievementMenuBackButton.left <= mouseX <= achievementMenuBackButton.right
                and achievementMenuBackButton.top <= mouseY <= achievementMenuBackButton.bottom):
            hideAchievementMenu()


def onKeyPress(key):
    normalizedKey = key.lower()
    if normalizedKey == KONAMI_CODE[app.konamiProgress]:
        app.konamiProgress += 1
        if app.konamiProgress == len(KONAMI_CODE):
            unlockAchievement('konami-code')
            app.konamiProgress = 0
    else:
        app.konamiProgress = 1 if normalizedKey == KONAMI_CODE[0] else 0

    if key == 'enter':
        if app.playing == True:
            app.playing = 'paused'
            pauseGroup.visible = True
            tetrisMusic.pause()
        elif app.playing == 'paused':
            app.playing = True
            pauseGroup.visible = False
            tetrisMusic.channel.unpause()
            updateGhost()
        return

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
            resetRunAchievements()

            # Save high score BEFORE resetting
            if app.currentDifficulty == 'Easy':
                currentHigh = app.highScoreEasy
            elif app.currentDifficulty == 'Hard':
                currentHigh = app.highScoreHard
            else:
                currentHigh = app.highScoreNormal

            if app.score > currentHigh:
                if app.currentDifficulty == 'Easy':
                    app.highScoreEasy = app.score
                elif app.currentDifficulty == 'Hard':
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
            app.heldType = None
            app.canHold = True
            updateHoldDisplay()
            holdUIGroup.visible = False

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
            updateGhost()

    if key == 'x':
        if (app.playing == True):
            rotatePiece("right")
            updateGhost()
    if key == 'c' and app.playing == True:
        holdCurrentPiece()

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
        elif app.playing == 'achievements':
            hideAchievementMenu()

    if key == 'e' and app.playing == 'end':
        showAchievementMenu()

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
            app.currentDifficulty = app.selectedDifficulty
            app.hardMode = (app.currentDifficulty == 'Hard')
            app.startLevel = app.selectedLevel
            app.level = app.startLevel
            app.linesCleared = 0
            app.score = 0
            app.heldType = None
            app.canHold = True
            updateHoldDisplay()
            holdUIGroup.visible = True
            pauseGroup.visible = False
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

    if app.playing == 'startMenu' and key in ['right', 'd']:
        changeSelectionDifficulty('next')
    if app.playing == 'startMenu' and key in ['left', 'a']:
        changeSelectionDifficulty('prev')
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
                app.moveDelay = app.moveCooldown
                updateGhost()
            return

    if key in ['d','right']:
        if (app.playing == True):
            if canMove(app.blockSize, 0):
                moveSound.play(restart=True)
                for b in curPiece:
                    b.centerX += app.blockSize
                app.moveDelay = app.moveCooldown
                updateGhost()
            return

    if key in ['s','down']:
        if (app.playing == True):
            if canMove(0, app.blockSize):
                moveSound.play(restart=True)
                for b in curPiece:
                    b.centerY += app.blockSize
                app.score += 1
                app.moveDelay = app.moveCooldown
                updateGhost()
            return

def onKeyHold(keys, modifiers):
    if app.playing != True:
        return

    if app.moveDelay > 0:
        app.moveDelay -= 1
        return

    lowerKeys = {k.lower() for k in keys}

    if 's' in lowerKeys or 'down' in lowerKeys:
        if canMove(0, app.blockSize):
            moveSound.play(restart=True)
            for b in curPiece:
                b.centerY += app.blockSize
            app.score += 1
            app.moveDelay = app.moveCooldown
            updateGhost()
        return

    if 'a' in lowerKeys or 'left' in lowerKeys:
        if canMove(-app.blockSize, 0):
            moveSound.play(restart=True)
            for b in curPiece:
                b.centerX -= app.blockSize
            app.moveDelay = app.moveCooldown
            updateGhost()
        return

    if 'd' in lowerKeys or 'right' in lowerKeys:
        if canMove(app.blockSize, 0):
            moveSound.play(restart=True)
            for b in curPiece:
                b.centerX += app.blockSize
            app.moveDelay = app.moveCooldown
            updateGhost()
        return


def onKeyRelease(key, modifiers):
    if key.lower() in ['a','left','d','right','s','down']:
        app.moveDelay = 0

    # Example: press 'o' to open `snake.py` without showing a console window while it loads
    if key == 'o':
        if launch_python_hidden is None:
            print('launch_hidden helper not available; install launch_hidden.py')
        else:
            try:
                script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snake.py')
                launch_python_hidden(script)
            except Exception as e:
                print('Failed to launch script:', e)

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
        if lines >= 1:
            unlockAchievement('first-line')
        if lines >= 2:
            unlockAchievement('double-clear')
        if lines >= 3:
            unlockAchievement('triple-clear')
        if lines >= 4:
            unlockAchievement('tetris-clear')

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
    checkAchievementProgress()
    app.playing = 'end'
    pauseGroup.visible = False
    holdUIGroup.visible = False
    tetrisMusic.pause()
    endGroup.visible = True
    tetrisEndMusic.play(restart=True, loop=True)

    if app.currentDifficulty == 'Easy':
        currentHigh = app.highScoreEasy
    elif app.currentDifficulty == 'Hard':
        currentHigh = app.highScoreHard
    else:
        currentHigh = app.highScoreNormal

    if app.score > currentHigh:
        if app.currentDifficulty == 'Easy':
            app.highScoreEasy = app.score
        elif app.currentDifficulty == 'Hard':
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
        app.canHold = True

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

                if newY > PLAYFIELD_BOTTOM + app.layoutOffsetY:
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

        if curPiece.top < app.offsetY:
            curPiece.top = app.offsetY
        if placedPieces.top == app.offsetY:
            gameOver()

        endLinesText.value = 'LINES: ' + str(app.linesCleared)
        endScoreText.value = 'SCORE: ' + str(app.score)
        endLevelText.value = 'LEVEL: ' + str(app.level)
        previewBlocks.centerX = app.offsetX + 700
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
    updateAchievementPopup()

cmu_graphics.run()
