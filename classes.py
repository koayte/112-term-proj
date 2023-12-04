from cmu_graphics import *
from PIL import Image
import math
import random

class Player:
    def __init__(self, name, app, x, y, radius, aimLength, aimAngle, aimDirection, 
                 charSpeed, healSpeed, normalDamage, superDamage, damageNeeded):
        # gif 
        self.name = name
        self.charGif = Image.open('images/jessie.gif')
        self.spriteListRight = []
        self.spriteDirection = 'right'
        self.spriteListLeft = []
        for frame in range(self.charGif.n_frames):
            self.charGif.seek(frame)
            fr = self.charGif.resize((self.charGif.size[0]//2, self.charGif.size[1]//2))
            right = CMUImage(fr)
            left = fr.transpose(Image.FLIP_LEFT_RIGHT)
            left = CMUImage(left)
            self.spriteListRight.append(right)
            self.spriteListLeft.append(left)
        self.spriteCounterRight = 0
        self.spriteCounterLeft = 0
        
        # location
        self.playerX = x
        self.playerY = y 
        self.radius = radius
        self.moving = False 

        ### CHARACTER STATISTICS 
        self.charSpeed = charSpeed
        
        # aim 
        self.maxAimLength = aimLength 
        self.aimLength = aimLength # current aim length 
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
        # bullets
        self.bullets = []

        # damage caused 
        self.normalDamage = normalDamage
        self.superDamage = superDamage
        self.totalDamage = 0.1
        self.damageNeeded = damageNeeded
        self.super = Super(app, self)
        self.isSuperMode = False 

        # health bar 
        self.maxHealth = 1500
        self.currHealth = 800
        self.healthUnitLen = self.radius*2/self.maxHealth
        self.healthX = self.playerX - self.radius # left  
        self.healthY = self.playerY - self.radius*2.2
        self.healSpeed = healSpeed

        self.hidden = False 
        self.opacity = 100

        self.hiding = False 
        self.coordsList = []

    def __repr__(self):
        return f'{self.name}'
        
    def drawPlayer(self, app):
        if self.spriteDirection == 'right':
            drawImage(self.spriteListRight[self.spriteCounterRight], self.playerX, self.playerY, align='center', opacity=self.opacity)
        else:
            drawImage(self.spriteListLeft[self.spriteCounterLeft], self.playerX, self.playerY, align='center', opacity=self.opacity)

    def drawRange(self, app):
        drawPolygon(*self.rangeCoords, fill=rgb(240,209,106), opacity=80)

    def healthBarColor(self):
        red = (255,14,14)
        yellow = (248,251,46) # at halfHealth
        green = (20,255,0)
        halfHealth = self.maxHealth / 2
        if 0 <= self.currHealth <= halfHealth:
            r = (yellow[0] - red[0]) / halfHealth * self.currHealth + red[0]
            g = (yellow[1] - red[1]) / halfHealth * self.currHealth + red[1]
            b = (yellow[2] - red[2]) / halfHealth * self.currHealth + red[2]
        elif halfHealth < self.currHealth <= self.maxHealth:
            r = (green[0] - yellow[0]) / halfHealth * (self.currHealth - halfHealth) + yellow[0]
            g = (green[1] - yellow[1]) / halfHealth * (self.currHealth - halfHealth) + yellow[1]
            b = (green[2] - yellow[2]) / halfHealth * (self.currHealth - halfHealth) + yellow[2]
        return rgb(r,g,b)

    def drawHealthBar(self, app):
        # max health bar
        drawRect(self.healthX, self.healthY, self.radius*2, 16, align='left', fill='black', opacity=self.opacity) 
        # current health bar  DO THIS 
        healthColor = self.healthBarColor()
        drawRect(self.healthX, self.healthY, self.currHealth*self.healthUnitLen, 16, align='left', fill=healthColor, opacity=self.opacity)

    def drawAmmoBar(self, app):
        # max ammo bar 
        drawRect(self.ammoX, self.ammoY, self.radius*2, 16, align='left', fill='black', opacity=self.opacity)
        # curr ammo bar 
        drawRect(self.ammoX, self.ammoY, self.currAmmo*self.ammoUnitLen, 16, align='left', fill='orange', opacity=self.opacity)
        # rectangles to show three shots 
        for i in range(self.maxShots):
            oneRectLen = self.maxAmmo/3*self.ammoUnitLen
            leftX = self.ammoX + i*oneRectLen
            drawRect(leftX, self.ammoY, oneRectLen, 16, align='left', fill=None, border='grey', borderWidth=0.7, opacity=self.opacity)

class Bullet:
    def __init__(self, player):
        # calculate radius of bullet circle inscribed within triangle range: A = rs
        self.playerRangeOppLen = distance(player.rangeLineOneX, player.rangeLineOneY, player.rangeLineTwoX, player.rangeLineTwoY)
        self.playerRangeSideLen = distance(player.playerX, player.playerY, player.rangeLineOneX, player.rangeLineOneY)
        self.playerRangeHeight = distance(player.playerX, player.playerY, player.aimLineX, player.aimLineY)
        self.playerRangeArea = 0.5 * self.playerRangeOppLen * self.playerRangeHeight
        self.playerRangeSemiPeri = 0.5 * (self.playerRangeSideLen * 2 + self.playerRangeOppLen)
        self.radius = self.playerRangeArea / self.playerRangeSemiPeri

        ### bullet location (direction of aim)
        # initial location
        distXFromPlayer = player.radius * math.cos(player.aimDirection)
        distYFromPlayer = player.radius * math.sin(player.aimDirection)
        self.originalBulletX = player.playerX 
        self.originalBulletY = player.playerY 
        self.bulletX = player.playerX + distXFromPlayer
        self.bulletY = player.playerY - distYFromPlayer
        # direction captured at point in time of bullet instance creation (when player shoots)
        self.bulletDirection = player.aimDirection
        
        # which player
        self.playerOrigin = player 
        self.playerHit = None 

        # is normal or super 
        self.isNormalOrSuper = "normal"
    
    def drawBullet(self, app):
        color = 'cyan' if self.playerOrigin == app.player else rgb(255,14,14)
        drawCircle(self.bulletX, self.bulletY, self.radius, fill=color)

class Super:
    def __init__(self, app, player):
        self.innerRadius = 40
        self.outerRadius = 50
        self.superX = app.width-150
        self.superY = app.height-150
        self.activated = False 
        self.damageNeeded = player.damageNeeded # to activate Super 
        self.degreePerDamage = 360 / self.damageNeeded
    
    def drawSuper(self, player):
        angle = self.degreePerDamage*player.totalDamage
        if angle >= 360:
            angle = 360 
        drawCircle(self.superX, self.superY, self.outerRadius, fill=rgb(18,24,50))
        drawArc(self.superX, self.superY, self.outerRadius*2-4, self.outerRadius*2-4, 0, angle, fill=rgb(240,209,106))
        if self.activated == True:
            drawCircle(self.superX, self.superY, self.innerRadius, fill=rgb(246,196,73))
            image = Image.open('images/skull-activated.png')
            image = image.resize((image.size[0]//8, image.size[1]//8))
            image = CMUImage(image)
            drawImage(image, self.superX, self.superY, align='center')
        else:
            drawCircle(self.superX, self.superY, self.innerRadius, fill=rgb(61,98,150), border=rgb(18,24,50))
            image = Image.open('images/skull-unactivated.png')
            image = image.resize((image.size[0]//8, image.size[1]//8))
            image = CMUImage(image)
            drawImage(image, self.superX, self.superY, align='center')

class MapItem:
    def __init__(self, app, item):
        self.item = item
        if item == 'p': # plant
            self.image = Image.open('images/plant.png')
            self.blocked = False 
            sizeScaleFactor = self.image.size[0] // app.gridSize
        elif item == 'b': # block
            self.image = Image.open('images/block.png')
            self.blocked = True
            sizeScaleFactor = self.image.size[0] // app.gridSize
        elif item == 'w': 
            self.image = Image.open('images/water.png')
            self.blocked = True
            sizeScaleFactor = self.image.size[0] // app.gridSize
        self.image = self.image.resize((self.image.size[0]//sizeScaleFactor, self.image.size[1]//sizeScaleFactor))
        self.image = CMUImage(self.image)

    def drawMapItem(self, app, x, y):
        topLeftX, topLeftY = app.gridSize*y, app.gridSize*x
        drawImage(self.image, topLeftX, topLeftY, align='left-top')

class Button:
    def __init__(self, cx, cy, text, width, height, size):
        self.cx = cx 
        self.cy = cy
        self.text = text
        self.width = width
        self.height = height
        self.size = size
        self.clicked = False 
    
    def drawButton(self):
        drawRect(self.cx, self.cy, self.width, self.height, align='center', fill=None, border='white')
        drawLabel(self.text, self.cx, self.cy, align='center', size=self.size, font='orbitron', fill='white')

    def buttonClick(self, mouseX, mouseY):
        rectLeft = self.cx - self.width / 2
        rectRight = self.cx + self.width / 2
        rectTop = self.cy - self.height / 2
        rectBot = self.cy + self.height / 2
        if rectLeft <= mouseX <= rectRight and rectTop <= mouseY <= rectBot:
            self.clicked = True 