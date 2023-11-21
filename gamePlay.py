from cmu_graphics import *
import math

class Player:
    def __init__(self, x, y, radius, aimLength, aimAngle, aimDirection):
        # location
        self.playerX = x
        self.playerY = y 
        self.radius = radius
        
        # aim 
        self.aimLength = aimLength
        self.aimAngle = aimAngle 
        self.aimDirection = aimDirection 
        self.aimLineX = self.aimLength + self.playerX
        self.aimLineY = 0
        self.rangeLineOneX = self.rangeLineOneY = self.rangeLineTwoX = self.rangeLineTwoY = 0
        self.rangeCoords = [self.playerX, self.playerY, self.rangeLineOneX, self.rangeLineOneY, self.rangeLineTwoX, self.rangeLineTwoY]

    def drawPlayer(self, app):
        drawCircle(self.playerX, self.playerY, self.radius, fill='black')

    def drawRange(self, app):
        drawPolygon(*self.rangeCoords, fill='yellow', opacity=80)


def onAppStart(app):
    # map
    app.width = 1920
    app.height = 1080 
    app.gridSize = 40
    app.stepsPerSecond = 50
    

    # player
    app.radius = app.gridSize//2 
    app.player = Player(app.width/2, app.height/2, app.radius, 80, 0.4, 0)
    # app.playerX = app.width//2
    # app.playerY = app.height//2
    # app.radius = app.gridSize//2

    # aim 
    # app.aimLength = 80
    # app.aimAngle = 0.4
    # app.aimDirection = 0
    # app.aimLineX = app.aimLength + app.playerX
    # app.aimLineY = 0
    # app.rangeLineOneX = 0 
    # app.rangeLineOneY = 0
    # app.rangeLineTwoX = 0
    # app.rangeLineTwoY = 0
    # app.rangeCoords = [app.playerX, app.playerY, app.rangeLineOneX, app.rangeLineOneY, app.rangeLineTwoX, app.rangeLineTwoY]
    app.mouseX = 0
    app.mouseY = 0

    # shoot 


def redrawAll(app):
    # drawPolygon(*app.rangeCoords, fill='yellow', opacity=80)
    app.player.drawPlayer(app)
    app.player.drawRange(app)
    # drawCircle(app.playerX, app.playerY, app.radius, fill='black')
    # drawLine(app.playerX, app.playerY, app.aimLineX, app.aimLineY)
    # drawLine(app.playerX, app.playerY, app.rangeLineOneX, app.rangeLineOneY)
    # drawLine(app.playerX, app.playerY, app.rangeLineTwoX, app.rangeLineTwoY)

def onKeyPress(app, key):
    # shoot 
    if key == 'space':
        pass

def onKeyHold(app, keys):
    # navigation
    if 'w' in keys and 's' not in keys:
        app.player.playerY -= 1
    elif 'w' not in keys and 's' in keys:
        app.player.playerY += 1
    if 'a' in keys and 'd' not in keys:
        app.player.playerX -= 1
    elif 'a' not in keys and 'd' in keys:
        app.player.playerX += 1

def mouseToAim(app):
    # aim 
    straightDist = distance(app.player.playerX, app.player.playerY, app.mouseX, app.mouseY)
    fraction = (app.mouseX - app.player.playerX) / straightDist if straightDist != 0 else 1
    if app.mouseY > app.player.playerY: # mouseY is below player 
        app.player.aimDirection = -1*math.acos(fraction)
    else: # mouseY is above player 
        app.player.aimDirection = math.acos(fraction)
    app.player.aimLineX = app.player.playerX + app.player.aimLength*math.cos(app.player.aimDirection)
    app.player.aimLineY = app.player.playerY - app.player.aimLength*math.sin(app.player.aimDirection)

    # triangular range 
    rangeSideLen = app.player.aimLength / math.cos(app.player.aimAngle / 2)
    rangeLineOneAngle = app.player.aimAngle/2 + app.player.aimDirection 
    app.player.rangeLineOneX = app.player.playerX + rangeSideLen*math.cos(rangeLineOneAngle)
    app.player.rangeLineOneY = app.player.playerY - rangeSideLen*math.sin(rangeLineOneAngle)
    rangeLineTwoAngle = app.player.aimDirection - app.player.aimAngle/2
    app.player.rangeLineTwoX = app.player.playerX + rangeSideLen*math.cos(rangeLineTwoAngle)
    app.player.rangeLineTwoY = app.player.playerY - rangeSideLen*math.sin(rangeLineTwoAngle)
    app.player.rangeCoords = [app.player.playerX, app.player.playerY, app.player.rangeLineOneX, 
                              app.player.rangeLineOneY, app.player.rangeLineTwoX, app.player.rangeLineTwoY]

def onStep(app):
    mouseToAim(app)

def onMouseMove(app, mouseX, mouseY):
    # aim 
    app.mouseX = mouseX
    app.mouseY = mouseY


def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

def main():
    runApp()

main()