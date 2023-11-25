from cmu_graphics import *
import math
from PIL import Image

class Player:
    def __init__(self, x, y, radius, aimLength, aimAngle, aimDirection, charSpeed, healSpeed):
        # gif 
        self.charGif = Image.open('characters/jessie.gif')
        self.spriteList = []
        self.spriteDirection = 'right'
        for frame in range(self.charGif.n_frames):
            self.charGif.seek(frame)
            fr = self.charGif.resize((self.charGif.size[0]//2, self.charGif.size[1]//2))
            fr = CMUImage(fr)
            self.spriteList.append(fr)
        self.spriteCounter = 0
        
        # location
        self.playerX = x
        self.playerY = y 
        self.radius = radius
        self.moving = False 

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
        self.currHealth = 1400
        self.healthUnitLen = self.radius*2/self.maxHealth
        self.healthX = self.playerX - self.radius # left  
        self.healthY = self.playerY - self.radius*2.2
        self.healSpeed = healSpeed

        # bullets
        self.bullets = []


    def drawPlayer(self, app):
        # drawCircle(self.playerX, self.playerY, self.radius, fill='black')
        drawImage(self.spriteList[self.spriteCounter], self.playerX, self.playerY, align='center')

    def drawRange(self, app):
        drawPolygon(*self.rangeCoords, fill='yellow', opacity=80)

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
        drawRect(self.healthX, self.healthY, self.radius*2, 16, align='left', fill='black') 
        # current health bar  DO THIS 
        healthColor = self.healthBarColor()
        drawRect(self.healthX, self.healthY, self.currHealth*self.healthUnitLen, 16, align='left', fill=healthColor)

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
    app.stepsPerSecond = 30
    app.mouseX = 0
    app.mouseY = 0

    # player (user)
    app.radius = app.gridSize/2 
    app.player = Player(app.width/2, app.height/2, app.radius, aimLength=250, aimAngle=0.1, aimDirection=0, charSpeed=1.5, healSpeed=0.7)

    # enemy player 
    app.enemy = Player(app.width/2+200, app.height/2, app.radius, aimLength=300, aimAngle=0.1, aimDirection=0, charSpeed=1.5, healSpeed=0.7)

class Bullet:
    def __init__(self, player):
        # calculate radius of bullet circle inscribed within triangle range: A = rs
        self.playerRangeOppLen = distance(player.rangeLineOneX, player.rangeLineOneY, player.rangeLineTwoX, player.rangeLineTwoY)
        self.playerRangeSideLen = distance(player.playerX, player.playerY, player.rangeLineOneX, player.rangeLineOneY)
        self.playerRangeHeight = distance(player.playerX, player.playerY, player.aimLineX, player.aimLineY)
        self.playerRangeArea = 0.5 * self.playerRangeOppLen * self.playerRangeHeight
        self.playerRangeSemiPeri = 0.5 * (self.playerRangeSideLen * 2 + self.playerRangeOppLen)
        self.radius = self.playerRangeArea / self.playerRangeSemiPeri

        # bullet location (direction of aim)
        # initial location
        distXFromPlayer = (player.radius + self.radius) * math.cos(player.aimDirection)
        distYFromPlayer = (player.radius + self.radius) * math.sin(player.aimDirection)
        self.bulletX = player.playerX + distXFromPlayer
        self.bulletY = player.playerY - distYFromPlayer
        # direction at that point in time 
        self.bulletDirection = player.aimDirection
        
        # which player
        self.playerOrigin = player 
        self.playerHit = None 


    
    def drawBullet(self):
        # rint(self.playerRangeOppLen)
        drawCircle(self.bulletX, self.bulletY, self.radius)

############################### EVENTS 

def redrawAll(app):
    drawEachPlayer(app, app.player)
    drawEachPlayer(app, app.enemy)
    for i in range(len(app.player.bullets)):
        bullet = app.player.bullets[i]
        bullet.drawBullet()
    

def drawEachPlayer(app, character):
    character.drawRange(app)
    character.drawPlayer(app)
    character.drawHealthBar(app)
    character.drawAmmoBar(app)
    
def onKeyPress(app, key):
    # shoot 
    if key == 'space':
        shoot(app.player)
        

def onKeyHold(app, keys):
    # navigation
    app.player.spriteCounter = (app.player.spriteCounter + 1) % len(app.player.spriteList)
    if 'w' in keys and 's' not in keys:
        app.player.playerY -= app.player.charSpeed
        boundaryCorrection(app)
    elif 'w' not in keys and 's' in keys:
        app.player.playerY += app.player.charSpeed
        boundaryCorrection(app)
    if 'a' in keys and 'd' not in keys:
        app.player.playerX -= app.player.charSpeed
        boundaryCorrection(app)
        app.player.spriteList.clear()
        for frame in range(app.player.charGif.n_frames):
            app.player.charGif.seek(frame)
            fr = app.player.charGif.resize((app.player.charGif.size[0]//2, app.player.charGif.size[1]//2))
            fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
            fr = CMUImage(fr)
            app.player.spriteList.append(fr)
    elif 'a' not in keys and 'd' in keys:
        app.player.playerX += app.player.charSpeed
        boundaryCorrection(app)
        app.player.spriteList.clear()
        for frame in range(app.player.charGif.n_frames):
            app.player.charGif.seek(frame)
            fr = app.player.charGif.resize((app.player.charGif.size[0]//2, app.player.charGif.size[1]//2))
            fr = CMUImage(fr)
            app.player.spriteList.append(fr)

    app.player.ammoY = app.player.playerY - app.player.radius*1.5
    app.player.healthY = app.player.playerY - app.player.radius*2.2
    app.player.ammoX = app.player.healthX = app.player.playerX - app.player.radius

def onStep(app):
    mouseToAim(app)
    rechargeHealthAndAmmo(app.player)
    rechargeHealthAndAmmo(app.enemy)
    
    # bullets
    bulletsMove(app.player)
    bulletsHit(app.player, app.enemy)

def onMouseMove(app, mouseX, mouseY):
    # aim 
    app.mouseX = mouseX
    app.mouseY = mouseY

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

############################### MAP 

def boundaryCorrection(app):
    if app.player.playerX > app.width - app.player.radius:
        app.player.playerX = app.width - app.player.radius
    if app.player.playerX < app.player.radius: 
        app.player.playerX = app.player.radius 
    if app.player.playerY > app.height - app.player.radius:
        app.player.playerY = app.height - app.player.radius
    if app.player.playerY < app.player.radius: 
        app.player.playerY = app.player.radius 

############################### HEALTH 
def rechargeHealthAndAmmo(player):
    if player.currHealth < player.maxHealth: 
        player.currHealth += player.healSpeed
        if player.currHealth > player.maxHealth:
            player.currHealth = player.maxHealth
    
    if player.currAmmo < player.maxAmmo:
        player.currAmmo += 6

############################### AIM AND SHOOT  

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

def bulletsMove(player):
    for i in range(len(player.bullets)):
        bullet = player.bullets[i]
        dx = 3*math.cos(bullet.bulletDirection)
        dy = 3*math.sin(bullet.bulletDirection)
        bullet.bulletX += dx
        bullet.bulletY -= dy

def shoot(player):
    ammoPerShot = player.maxAmmo / player.maxShots
    if player.currAmmo >= ammoPerShot: # if there is enough ammo 
        # ammo bar
        player.currAmmo -= ammoPerShot
        if player.currAmmo <= 0:
            player.currAmmo = 0.1

        # bullets 
        bullet = Bullet(player)
        player.bullets.append(bullet)

def getBulletIndex(player, enemy):
    for i in range(len(player.bullets)):
        bullet = player.bullets[i]
        if distance(bullet.bulletX, bullet.bulletY, enemy.playerX, enemy.playerY) <= (bullet.radius + enemy.radius):
            bullet.playerHit = enemy 
            enemy.currHealth -= 100
            return i 
    return None 

def bulletsHit(player, enemy):
    i = getBulletIndex(player, enemy)
    if i != None: 
        player.bullets.pop(i)

def main():
    runApp()

main()