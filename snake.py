from cmu_graphics import *
import os
import random

app.width = 1280
app.height = 740
app.background = gradient('black', rgb(7, 24, 39), 'black', start='top')

CELL_SIZE = 30
MARGIN_X = 40
MARGIN_Y = 40
GRID_COLS = 28
GRID_ROWS = 22
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
PANEL_X = MARGIN_X + GRID_WIDTH + 60

snake = []
snakeShapes = []
obstacleShapes = []
obstacles = set()
foodShape = None
food = None
foodType = 'normal'
direction = (1, 0)
nextDirection = (1, 0)
score = 0
bestScore = 0
gameOver = False
paused = False
stepCounter = 0
speed = 8
gameState = 'ready'
bestScorePath = os.path.join('data', 'snake', 'best_score.txt')

def loadBestScore():
    try:
        os.makedirs(os.path.dirname(bestScorePath), exist_ok=True)
        if not os.path.exists(bestScorePath):
            return 0
        with open(bestScorePath, 'r', encoding='utf-8') as f:
            raw = f.read().strip()
            return int(raw) if raw else 0
    except:
        return 0

def saveBestScore():
    try:
        os.makedirs(os.path.dirname(bestScorePath), exist_ok=True)
        with open(bestScorePath, 'w', encoding='utf-8') as f:
            f.write(str(bestScore))
    except:
        pass

bestScore = loadBestScore()

bg = Rect(0, 0, app.width, app.height, fill=gradient('black', rgb(16, 26, 42), 'black', start='top'))
board = Rect(MARGIN_X - 2, MARGIN_Y - 2, GRID_WIDTH + 4, GRID_HEIGHT + 4,
             fill='black', border=rgb(223, 231, 255), borderWidth=4)

titleLabel = Label('SNAKE', PANEL_X + 110, 70,
                   fill=rgb(124, 231, 255), size=42, bold=True, align='center')
subtitleLabel = Label('Arcade Edition', PANEL_X + 110, 110,
                     fill='white', size=20, bold=True, align='center')

scoreLabel = Label('Score: 0', PANEL_X + 110, 190,
                  fill='white', size=28, bold=True, align='center')
bestScoreLabel = Label(f'Best: {bestScore}', PANEL_X + 110, 235,
                      fill='gold', size=22, bold=True, align='center')
speedLabel = Label('Level: 1', PANEL_X + 110, 280,
                   fill='lightGreen', size=20, bold=True, align='center')

statusLabel = Label('Press Enter to start\nArrow keys or WASD to move',
                   PANEL_X + 110, 360, fill='lightSkyBlue', size=21, align='center')
gameOverLabel = Label('', PANEL_X + 110, 315, fill='red', size=32, bold=True,
                     visible=False, align='center')

controlsLabel = Label('P = Pause   R = Restart\nEat apples to grow\nAvoid walls, obstacles, and your tail',
                     PANEL_X + 110, 470, fill='lightGreen', size=18, align='center')

def gridToPixels(cell):
    col, row = cell
    x = MARGIN_X + col * CELL_SIZE
    y = MARGIN_Y + row * CELL_SIZE
    return x, y

def updateScore():
    global bestScore
    scoreLabel.value = f'Score: {score}'
    bestScoreLabel.value = f'Best: {bestScore}'
    speedLabel.value = f'Level: {1 + score // 5}'

def createSnakeShape(index, cell):
    color = rgb(126, 242, 154) if index == 0 else rgb(74, 222, 128)
    border = rgb(15, 81, 50)
    rect = Rect(0, 0, CELL_SIZE, CELL_SIZE, fill=color, border=border, borderWidth=2)
    rect.left, rect.top = gridToPixels(cell)
    return rect

def syncSnakeShapes():
    global snakeShapes
    if len(snakeShapes) < len(snake):
        for i in range(len(snake) - len(snakeShapes)):
            snakeShapes.append(createSnakeShape(i, snake[i]))
    for i, cell in enumerate(snake):
        if i < len(snakeShapes):
            snakeShapes[i].left, snakeShapes[i].top = gridToPixels(cell)
            snakeShapes[i].visible = True
            if i == 0:
                snakeShapes[i].fill = rgb(126, 242, 154)
                snakeShapes[i].border = rgb(15, 81, 50)
            else:
                snakeShapes[i].fill = rgb(74, 222, 128)
                snakeShapes[i].border = rgb(15, 81, 50)
    for extra in snakeShapes[len(snake):]:
        extra.visible = False

def createObstacleShape(cell):
    rect = Rect(0, 0, CELL_SIZE, CELL_SIZE, fill=rgb(112, 128, 144),
                border=rgb(51, 65, 85), borderWidth=2)
    rect.left, rect.top = gridToPixels(cell)
    return rect

def syncObstacles():
    global obstacleShapes
    cells = sorted(obstacles)
    while len(obstacleShapes) < len(cells):
        obstacleShapes.append(createObstacleShape(cells[-1]))
    for i, cell in enumerate(cells):
        obstacleShapes[i].left, obstacleShapes[i].top = gridToPixels(cell)
        obstacleShapes[i].visible = True
    for extra in obstacleShapes[len(cells):]:
        extra.visible = False

def createFoodShape():
    global foodShape
    if foodShape is None:
        foodShape = Rect(0, 0, CELL_SIZE, CELL_SIZE, borderWidth=2)

    if food is None:
        foodShape.visible = False
        return

    foodShape.left, foodShape.top = gridToPixels(food)
    if foodType == 'bonus':
        foodShape.fill = rgb(255, 209, 102)
        foodShape.border = rgb(217, 119, 6)
    else:
        foodShape.fill = rgb(255, 90, 90)
        foodShape.border = rgb(139, 0, 0)
    foodShape.visible = True

def randomFoodPosition():
    available = [
        (col, row)
        for col in range(GRID_COLS)
        for row in range(GRID_ROWS)
        if (col, row) not in snake and (col, row) not in obstacles
    ]
    if not available:
        return None
    return random.choice(available)

def generateObstacles():
    global obstacles
    target = min(5 + score // 5, 12)
    obstacles = set()
    attempts = 0
    while len(obstacles) < target and attempts < 400:
        attempts += 1
        col = random.randint(1, GRID_COLS - 2)
        row = random.randint(1, GRID_ROWS - 2)
        cell = (col, row)
        if cell in snake:
            continue
        if cell == food:
            continue
        if abs(col - (GRID_COLS // 2)) + abs(row - (GRID_ROWS // 2)) < 4:
            continue
        obstacles.add(cell)
    syncObstacles()

def spawnFood():
    global food, foodType
    food = randomFoodPosition()
    if food is None:
        gameWon()
        return

    foodType = 'bonus' if random.random() < 0.18 and len(snake) >= 5 else 'normal'
    createFoodShape()

def gameWon():
    global gameOver, gameState
    gameOver = True
    gameState = 'gameover'
    gameOverLabel.value = 'You beat the board!'
    gameOverLabel.fill = rgb(138, 230, 176)
    gameOverLabel.visible = True
    statusLabel.value = 'Full board! Press R to restart.'
    statusLabel.fill = rgb(200, 247, 216)
    statusLabel.visible = True

def triggerGameOver():
    global gameOver, gameState
    gameOver = True
    gameState = 'gameover'
    gameOverLabel.value = 'Game Over!'
    gameOverLabel.fill = rgb(255, 107, 107)
    gameOverLabel.visible = True
    statusLabel.value = 'Press R to restart'
    statusLabel.fill = rgb(254, 202, 202)
    statusLabel.visible = True

def startGame():
    global gameState, paused
    if gameState == 'gameover':
        return
    paused = False
    gameState = 'playing'
    statusLabel.visible = False
    gameOverLabel.visible = False

def resetGame():
    global snake, snakeShapes, obstacles, food, foodType, direction, nextDirection
    global score, gameOver, paused, stepCounter, gameState

    snake = [
        (GRID_COLS // 2, GRID_ROWS // 2),
        (GRID_COLS // 2 - 1, GRID_ROWS // 2),
        (GRID_COLS // 2 - 2, GRID_ROWS // 2),
    ]
    direction = (1, 0)
    nextDirection = (1, 0)
    score = 0
    gameOver = False
    paused = False
    stepCounter = 0
    gameState = 'ready'
    obstacles = set()
    food = None

    if len(snakeShapes) < len(snake):
        for i in range(len(snake) - len(snakeShapes)):
            snakeShapes.append(createSnakeShape(i, snake[i]))
    for i, cell in enumerate(snake):
        if i < len(snakeShapes):
            snakeShapes[i].left, snakeShapes[i].top = gridToPixels(cell)
            snakeShapes[i].visible = True
            snakeShapes[i].fill = rgb(126, 242, 154) if i == 0 else rgb(74, 222, 128)
    for extra in snakeShapes[len(snake):]:
        extra.visible = False

    syncObstacles()
    spawnFood()
    updateScore()
    gameOverLabel.visible = False
    statusLabel.value = 'Press Enter to start\nArrow keys or WASD to move'
    statusLabel.fill = 'lightSkyBlue'
    statusLabel.visible = True

def moveSnake():
    global snake, food, score, bestScore, speed, gameOver, gameState

    if gameState != 'playing':
        return

    head = snake[0]
    dx, dy = direction
    nextHead = (head[0] + dx, head[1] + dy)

    willGrow = food is not None and nextHead == food

    if (
        nextHead[0] < 0 or nextHead[0] >= GRID_COLS or
        nextHead[1] < 0 or nextHead[1] >= GRID_ROWS or
        nextHead in obstacles or
        (nextHead in snake[:-1] and not willGrow)
    ):
        triggerGameOver()
        return

    snake.insert(0, nextHead)

    if willGrow:
        score += 3 if foodType == 'bonus' else 1
        if score > bestScore:
            bestScore = score
            saveBestScore()
        updateScore()
        if score % 5 == 0:
            generateObstacles()
        spawnFood()
    else:
        snake.pop()

    syncSnakeShapes()

def onStep():
    global stepCounter, direction, speed

    if gameState != 'playing':
        return

    stepCounter += 1
    if stepCounter >= speed:
        stepCounter = 0
        direction = nextDirection
        moveSnake()
        speed = max(4, 9 - score // 6)

def onKeyPress(key):
    global nextDirection, paused, gameState

    key = str(key).lower()

    if key in ['up', 'w'] and direction != (0, 1):
        nextDirection = (0, -1)
        if gameState == 'ready':
            startGame()
    elif key in ['down', 's'] and direction != (0, -1):
        nextDirection = (0, 1)
        if gameState == 'ready':
            startGame()
    elif key in ['left', 'a'] and direction != (1, 0):
        nextDirection = (-1, 0)
        if gameState == 'ready':
            startGame()
    elif key in ['right', 'd'] and direction != (-1, 0):
        nextDirection = (1, 0)
        if gameState == 'ready':
            startGame()

    elif key in ['enter', 'space']:
        if gameState == 'ready':
            startGame()
        elif gameState == 'paused':
            startGame()
        elif gameState == 'gameover':
            resetGame()
            startGame()

    elif key == 'p':
        if gameState == 'playing':
            paused = True
            gameState = 'paused'
            statusLabel.value = 'Paused. Press P or Enter to resume.'
            statusLabel.fill = 'gold'
            statusLabel.visible = True
        elif gameState == 'paused':
            paused = False
            gameState = 'playing'
            statusLabel.visible = False

    elif key == 'r':
        resetGame()

resetGame()
cmu_graphics.run()