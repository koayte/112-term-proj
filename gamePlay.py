from cmu_graphics import *
import math

def onAppStart(app):
    # map
    app.width = 1920
    app.height = 1080 
    app.gridSize = 40

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

def redrawAll(app):
    drawCircle(app.playerX, app.playerY, app.radius, fill='cyan')
    drawLine(app.playerX, app.playerY, app.aimLineX, app.aimLineY)
    drawLine(app.playerX, app.playerY, app.rangeLineOneX, app.rangeLineOneY)
    drawLine(app.playerX, app.playerY, app.rangeLineTwoX, app.rangeLineTwoY)

def onKeyPress(app, key):
    # shoot 
    pass

def onKeyHold(app, keys):
    # navigation
    if 'w' in keys and 's' not in keys:
        app.playerY -= 3
    elif 'w' not in keys and 's' in keys:
        app.playerY += 3
    if 'a' in keys and 'd' not in keys:
        app.playerX -= 3
    elif 'a' not in keys and 'd' in keys:
        app.playerX += 3

def onMouseMove(app, mouseX, mouseY):
    ######## PROBLEM WITH IF MOUSE IS NOT MOVING, I DON'T WANT THE RANGE TO INCREASE
    # aim 
    straightDist = distance(app.playerX, app.playerY, mouseX, mouseY)
    fraction = (mouseX - app.playerX) / straightDist if straightDist != 0 else 1
    if mouseY > app.playerY: # mouseY is below player 
        app.aimDirection = -1*math.acos(fraction)
    else: # mouseY is above player 
        app.aimDirection = math.acos(fraction)
    app.aimLineX = app.playerX + app.aimLength*math.cos(app.aimDirection)
    app.aimLineY = app.playerY - app.aimLength*math.sin(app.aimDirection)

    # triangle range 
    rangeSideLen = app.aimLength / math.cos(app.aimAngle / 2)
    rangeLineOneAngle = app.aimAngle/2 + app.aimDirection 
    app.rangeLineOneX = app.playerX + rangeSideLen*math.cos(rangeLineOneAngle)
    app.rangeLineOneY = app.playerY - rangeSideLen*math.sin(rangeLineOneAngle)
    rangeLineTwoAngle = app.aimDirection - app.aimAngle/2
    app.rangeLineTwoX = app.playerX + rangeSideLen*math.cos(rangeLineTwoAngle)
    app.rangeLineTwoY = app.playerY - rangeSideLen*math.sin(rangeLineTwoAngle)

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

def main():
    runApp()

main()