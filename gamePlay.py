from cmu_graphics import *
import math

class Player:
    def __init__(self, x, y, radius, aimLength, aimAngle, aimDirection, charSpeed):
        # location
        self.playerX = x
        self.playerY = y 
        self.radius = radius

        ### CHARACTER STATISTICS 
        self.charSpeed = charSpeed
        
        # aim 
        self.aimLength = aimLength
        self.aimAngle = aimAngle 
        self.aimDirection = aimDirection 
        self.aimLineX = self.aimLength + self.playerX
        self.aimLineY = 0
        self.rangeLineOneX = self.rangeLineOneY = self.rangeLineTwoX = self.rangeLineTwoY = 0
        self.rangeCoords = [self.playerX, self.playerY, self.rangeLineOneX, self.rangeLineOneY, self.rangeLineTwoX, self.rangeLineTwoY]

        # ammo and shoot 
        self.maxAmmo = 1500 
        self.currAmmo = self.maxAmmo 
        self.ammoUnitLen = self.radius*2/self.maxAmmo
        self.ammoX = self.playerX - self.radius # left 
        self.ammoY = self.playerY - self.radius*1.5
        self.maxShots = 3

        # health bar 
        self.maxHealth = 1500
        self.currHealth = self.maxHealth 
        self.healthUnitLen = self.radius*2/self.maxHealth
        self.healthX = self.playerX - self.radius # left  
        self.healthY = self.playerY - self.radius*2.2


    def drawPlayer(self, app):
        drawCircle(self.playerX, self.playerY, self.radius, fill='black')

    def drawRange(self, app):
        drawPolygon(*self.rangeCoords, fill='yellow', opacity=80)

    def drawHealthBar(self, app):
        # max health bar
        drawRect(self.healthX, self.healthY, self.radius*2, 16, align='left', fill='black') 
        # current health bar  DO THIS 
        drawRect(self.healthX, self.healthY, self.currHealth*self.healthUnitLen, 16, align='left', fill='green')

    def drawAmmoBar(self, app):
        # max ammo bar 
        drawRect(self.ammoX, self.ammoY, self.radius*2, 16, align='left', fill='black')
        # curr ammo bar 
        drawRect(self.ammoX, self.ammoY, self.currAmmo*self.ammoUnitLen, 16, align='left', fill='orange')
        # rectangles to show three shots 
        for i in range(self.maxShots):
            oneRectLen = self.maxAmmo/3*self.ammoUnitLen
            leftX = self.ammoX + i*oneRectLen
            drawRect(leftX, self.ammoY, oneRectLen, 16, align='left', fill=None, border='grey', borderWidth=0.7)
    

def onAppStart(app):
    # general 
    app.width = 1300
    app.height = 720 
    app.gridSize = 80
    app.stepsPerSecond = 50
    app.mouseX = 0
    app.mouseY = 0

    # player
    app.radius = app.gridSize/2 
    app.player = Player(app.width/2, app.height/2, app.radius, aimLength=150, aimAngle=0.4, aimDirection=0, charSpeed=1.5)


def redrawAll(app):
    app.player.drawRange(app)
    app.player.drawPlayer(app)
    app.player.drawHealthBar(app)
    app.player.drawAmmoBar(app)
    
    
def onKeyPress(app, key):
    # shoot 
    ammoPerShot = app.player.maxAmmo / app.player.maxShots
    if key == 'space' and app.player.currAmmo >= ammoPerShot:
        app.player.currAmmo -= ammoPerShot
        if app.player.currAmmo <= 0:
            app.player.currAmmo = 0.1

def onKeyHold(app, keys):
    # navigation
    if 'w' in keys and 's' not in keys:
        app.player.playerY -= app.player.charSpeed
        boundaryCorrection(app)
    elif 'w' not in keys and 's' in keys:
        app.player.playerY += app.player.charSpeed
        boundaryCorrection(app)
    if 'a' in keys and 'd' not in keys:
        app.player.playerX -= app.player.charSpeed
        boundaryCorrection(app)
    elif 'a' not in keys and 'd' in keys:
        app.player.playerX += app.player.charSpeed
        boundaryCorrection(app)
    
    app.player.ammoY = app.player.playerY - app.player.radius*1.5
    app.player.healthY = app.player.playerY - app.player.radius*2.2
    app.player.ammoX = app.player.healthX = app.player.playerX - app.player.radius


def boundaryCorrection(app):
    if app.player.playerX > app.width - app.player.radius:
        app.player.playerX = app.width - app.player.radius
    if app.player.playerX < app.player.radius: 
        app.player.playerX = app.player.radius 
    if app.player.playerY > app.height - app.player.radius:
        app.player.playerY = app.height - app.player.radius
    if app.player.playerY < app.player.radius: 
        app.player.playerY = app.player.radius 

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
    # ammo recharges 
    if app.player.currAmmo < app.player.maxAmmo:
        app.player.currAmmo += 2

def onMouseMove(app, mouseX, mouseY):
    # aim 
    app.mouseX = mouseX
    app.mouseY = mouseY


def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

def main():
    runApp()

main()