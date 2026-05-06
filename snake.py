from cmu_graphics import *
import random
import os
import sys

app.width = 1280
app.height = 740

CELL_SIZE = 30
MARGIN_X = 20
MARGIN_Y = 20
GRID_COLS = 35
GRID_ROWS = 23
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
PANEL_X = MARGIN_X + GRID_WIDTH + 30

snake = []
snakeShapes = []
foodShape = None
food = None
direction = (1, 0)
nextDirection = (1, 0)
score = 0
gameOver = False
paused = False
stepCounter = 0
speed = 8

bg = Rect(0, 0, app.width, app.height, fill='black')
board = Rect(MARGIN_X - 2, MARGIN_Y - 2, GRID_WIDTH + 4, GRID_HEIGHT + 4,
            fill=None, border='white', borderWidth=4)
scoreLabel = Label('Score: 0', PANEL_X + 120, 100, fill='white', size=30, bold=True, align='center')
helpLabel = Label('Use arrows or WASD to move\nP = Pause\nR = Restart', PANEL_X + 120, 170,
                  fill='white', size=22, align='center')
gameOverLabel = Label('', PANEL_X + 120, 260, fill='red', size=34, bold=True, visible=False, align='center')
controlsLabel = Label('Eat apples to grow.\nAvoid walls and your tail.', PANEL_X + 120, 230,
                      fill='lightGreen', size=22, align='center')


def gridToPixels(cell):
    col, row = cell
    x = MARGIN_X + col * CELL_SIZE
    y = MARGIN_Y + row * CELL_SIZE
    return x, y


def randomFoodPosition():
    available = [(col, row)
                 for col in range(GRID_COLS)
                 for row in range(GRID_ROWS)
                 if (col, row) not in snake]
    if not available:
        return None
    return random.choice(available)


def createFoodShape():
    global foodShape
    if foodShape is None:
        foodShape = Rect(0, 0, CELL_SIZE, CELL_SIZE, fill='red', border='darkred', borderWidth=2)
    if food:
        foodShape.left, foodShape.top = gridToPixels(food)
        foodShape.visible = True
    else:
        foodShape.visible = False


def createSnakeShape(index, cell):
    rect = Rect(0, 0, CELL_SIZE, CELL_SIZE, fill='springGreen', border='darkgreen', borderWidth=2)
    rect.left, rect.top = gridToPixels(cell)
    return rect


def resetGame():
    global snake, snakeShapes, food, direction, nextDirection, score, gameOver, paused, stepCounter
    snake = [(GRID_COLS // 2, GRID_ROWS // 2),
             (GRID_COLS // 2 - 1, GRID_ROWS // 2),
             (GRID_COLS // 2 - 2, GRID_ROWS // 2)]
    direction = (1, 0)
    nextDirection = (1, 0)
    score = 0
    gameOver = False
    paused = False
    stepCounter = 0
    if len(snakeShapes) < len(snake):
        for i in range(len(snake) - len(snakeShapes)):
            snakeShapes.append(createSnakeShape(i, snake[i]))
    for i, cell in enumerate(snake):
        if i < len(snakeShapes):
            snakeShapes[i].left, snakeShapes[i].top = gridToPixels(cell)
            snakeShapes[i].visible = True
    for extra in snakeShapes[len(snake):]:
        extra.visible = False
    updateScore()
    spawnFood()
    gameOverLabel.visible = False
    createFoodShape()


def updateScore():
    scoreLabel.value = f'Score: {score}'


def spawnFood():
    global food
    food = randomFoodPosition()
    if food is None:
        gameWon()
    createFoodShape()


def gameWon():
    global gameOver
    gameOver = True
    gameOverLabel.value = 'You win! Press R to restart.'
    gameOverLabel.fill = 'lightGreen'
    gameOverLabel.visible = True


def moveSnake():
    global snake, food, score, gameOver
    if gameOver or paused:
        return
    head = snake[0]
    dx, dy = direction
    nextHead = (head[0] + dx, head[1] + dy)
    if (nextHead[0] < 0 or nextHead[0] >= GRID_COLS or
        nextHead[1] < 0 or nextHead[1] >= GRID_ROWS or
        nextHead in snake):
        gameOverLabel.value = 'Game Over! Press R to restart.'
        gameOverLabel.fill = 'red'
        gameOverLabel.visible = True
        gameOver = True
        return
    snake.insert(0, nextHead)
    if food is not None and nextHead == food:
        score += 1
        updateScore()
        spawnFood()
    else:
        snake.pop()
    syncSnakeShapes()


def syncSnakeShapes():
    global snakeShapes
    if len(snakeShapes) < len(snake):
        for i in range(len(snake) - len(snakeShapes)):
            snakeShapes.append(createSnakeShape(i, snake[i]))
    for i, cell in enumerate(snake):
        snakeShapes[i].left, snakeShapes[i].top = gridToPixels(cell)
        snakeShapes[i].visible = True
    for extra in snakeShapes[len(snake):]:
        extra.visible = False


def onStep():
    global stepCounter, direction
    if gameOver or paused:
        return
    stepCounter += 1
    if stepCounter >= speed:
        stepCounter = 0
        direction = nextDirection
        moveSnake()


def onKeyPress(key):
    global nextDirection, paused
    key = key.lower()
    if key in ['up', 'w'] and direction != (0, 1):
        nextDirection = (0, -1)
    elif key in ['down', 's'] and direction != (0, -1):
        nextDirection = (0, 1)
    elif key in ['left', 'a'] and direction != (1, 0):
        nextDirection = (-1, 0)
    elif key in ['right', 'd'] and direction != (-1, 0):
        nextDirection = (1, 0)
    elif key == 'p':
        if not gameOver:
            paused = not paused
            gameOverLabel.value = 'Paused. Press P to resume.' if paused else ''
            gameOverLabel.fill = 'yellow'
            gameOverLabel.visible = paused
    elif key == 'r':
        resetGame()

resetGame()
cmu_graphics.run()
