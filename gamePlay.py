from cmu_graphics import *
import math

def onAppStart(app):
    # map
    app.width = 1920
    app.height = 1080 
    app.gridSize = 40
    app.stepsPerSecond = 50

    # player
    app.playerX = app.width//2
    app.playerY = app.height//2
    app.radius = app.gridSize//2

    # aim and shoot 
    app.aimLength = 80
    app.aimAngle = 0.4
    app.aimDirection = 0
    app.aimLineX = app.aimLength + app.playerX
    app.aimLineY = 0
    app.rangeLineOneX = 0 
    app.rangeLineOneY = 0
    app.rangeLineTwoX = 0
    app.rangeLineTwoY = 0
    app.rangeCoords = [app.playerX, app.playerY, app.rangeLineOneX, app.rangeLineOneY, app.rangeLineTwoX, app.rangeLineTwoY]
    app.mouseX = 0
    app.mouseY = 0

def redrawAll(app):
    drawPolygon(*app.rangeCoords, fill='blue', opacity=80)
    drawCircle(app.playerX, app.playerY, app.radius, fill='black')
    # drawLine(app.playerX, app.playerY, app.aimLineX, app.aimLineY)
    # drawLine(app.playerX, app.playerY, app.rangeLineOneX, app.rangeLineOneY)
    # drawLine(app.playerX, app.playerY, app.rangeLineTwoX, app.rangeLineTwoY)

def onKeyPress(app, key):
    # shoot 
    pass

def onKeyHold(app, keys):
    # navigation
    if 'w' in keys and 's' not in keys:
        app.playerY -= 1
    elif 'w' not in keys and 's' in keys:
        app.playerY += 1
    if 'a' in keys and 'd' not in keys:
        app.playerX -= 1
    elif 'a' not in keys and 'd' in keys:
        app.playerX += 1

def mouseToAim(app):
    # aim 
    straightDist = distance(app.playerX, app.playerY, app.mouseX, app.mouseY)
    fraction = (app.mouseX - app.playerX) / straightDist if straightDist != 0 else 1
    if app.mouseY > app.playerY: # mouseY is below player 
        app.aimDirection = -1*math.acos(fraction)
    else: # mouseY is above player 
        app.aimDirection = math.acos(fraction)
    app.aimLineX = app.playerX + app.aimLength*math.cos(app.aimDirection)
    app.aimLineY = app.playerY - app.aimLength*math.sin(app.aimDirection)

    # triangular range 
    rangeSideLen = app.aimLength / math.cos(app.aimAngle / 2)
    rangeLineOneAngle = app.aimAngle/2 + app.aimDirection 
    app.rangeLineOneX = app.playerX + rangeSideLen*math.cos(rangeLineOneAngle)
    app.rangeLineOneY = app.playerY - rangeSideLen*math.sin(rangeLineOneAngle)
    rangeLineTwoAngle = app.aimDirection - app.aimAngle/2
    app.rangeLineTwoX = app.playerX + rangeSideLen*math.cos(rangeLineTwoAngle)
    app.rangeLineTwoY = app.playerY - rangeSideLen*math.sin(rangeLineTwoAngle)
    app.rangeCoords = [app.playerX, app.playerY, app.rangeLineOneX, app.rangeLineOneY, app.rangeLineTwoX, app.rangeLineTwoY]

def onStep(app):
    mouseToAim(app)

def onMouseMove(app, mouseX, mouseY):
    ######## PROBLEM WITH IF MOUSE IS NOT MOVING, I DON'T WANT THE RANGE TO INCREASE
    # aim 
    app.mouseX = mouseX
    app.mouseY = mouseY


def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

def main():
    runApp()

main()