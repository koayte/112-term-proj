from cmu_graphics import *
import math
from PIL import Image

class Player:
    def __init__(self, app, x, y, radius, aimLength, aimAngle, aimDirection, charSpeed, 
                 healSpeed, normalDamage, superDamage, damageNeeded):
        # gif 
        self.charGif = Image.open('images/jessie.gif')
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
        self.currHealth = self.maxHealth
        self.healthUnitLen = self.radius*2/self.maxHealth
        self.healthX = self.playerX - self.radius # left  
        self.healthY = self.playerY - self.radius*2.2
        self.healSpeed = healSpeed

        
        
    def drawPlayer(self, app):
        drawImage(self.spriteList[self.spriteCounter], self.playerX, self.playerY, align='center')

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
        # direction at that point in time 
        self.bulletDirection = player.aimDirection
        
        # which player
        self.playerOrigin = player 
        self.playerHit = None 

        # is normal or super 
        self.isNormalOrSuper = "normal"
    
    def drawBullet(self):
        drawCircle(self.bulletX, self.bulletY, self.radius)

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
        if item == 'p': # plant
            self.image = Image.open('images/plant.png')
            self.blocked = False 
            sizeScaleFactor = self.image.size[0] // (app.gridSize+5)
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

############################### EVENTS 

def onAppStart(app):
    # map 
    app.width = 1280
    app.height = 720 
    app.gridSize = 80
    app.rows = app.height // app.gridSize # 9
    app.cols = app.width // app.gridSize # 16
    app.board = [ [0]*app.cols for row in range(app.rows) ]
    app.mapItemsDict = {
        'p': [],
        'b': [],
        'w': []
    }
    fillInBoard(app)

    # general 
    app.stepsPerSecond = 30
    app.mouseX = 0
    app.mouseY = 0

    # player (user)
    app.radius = app.gridSize/2 
    app.player = Player(app, app.width/2, app.height/2, app.radius, aimLength=250, aimAngle=0.1, aimDirection=0, 
                        charSpeed=1.5, healSpeed=0.7, normalDamage=150, superDamage=400, damageNeeded=2000)

    # enemy player 
    app.enemy1 = Player(app, app.width/2+200, app.height/2, app.radius, aimLength=300, aimAngle=0.1, aimDirection=0, 
                        charSpeed=1.5, healSpeed=0.7, normalDamage=150, superDamage=400, damageNeeded=2000)
    app.enemy2 = Player(app, app.width/2-200, app.height/2, app.radius, aimLength=300, aimAngle=0.1, aimDirection=0, 
                        charSpeed=1.5, healSpeed=0.7, normalDamage=150, superDamage=400, damageNeeded=2000)

    app.allChars = [app.player, app.enemy1, app.enemy2]

def redrawAll(app):
    drawMapBackground(app)
    drawItemInMap(app)
    drawEachPlayer(app, app.player)
    drawEachPlayer(app, app.enemy1)
    drawEachPlayer(app, app.enemy2)
    app.player.super.drawSuper(app.player)
    if app.player.isSuperMode: 
        mode = 'SUPER'
    else:
        mode = 'NORMAL'
    drawLabel(f'{mode}', app.width-150, app.height-80, size=16, font='orbitron')

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
    if key == 'f' and app.player.super.activated == True:
        app.player.isSuperMode = not app.player.isSuperMode

def onMousePress(app, mouseX, mouseY):
    shoot(app.player)
        
def onKeyHold(app, keys):
    # navigation
    if 'w' in keys and 's' not in keys:
        app.player.playerY -= app.player.charSpeed
    elif 'w' not in keys and 's' in keys:
        app.player.playerY += app.player.charSpeed
    if 'a' in keys and 'd' not in keys:
        app.player.playerX -= app.player.charSpeed * 2
        app.player.spriteList.clear()
        for frame in range(app.player.charGif.n_frames):
            app.player.charGif.seek(frame)
            fr = app.player.charGif.resize((app.player.charGif.size[0]//2, app.player.charGif.size[1]//2))
            fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
            fr = CMUImage(fr)
            app.player.spriteList.append(fr)
    elif 'a' not in keys and 'd' in keys:
        app.player.playerX += app.player.charSpeed * 2
        app.player.spriteList.clear()
        for frame in range(app.player.charGif.n_frames):
            app.player.charGif.seek(frame)
            fr = app.player.charGif.resize((app.player.charGif.size[0]//2, app.player.charGif.size[1]//2))
            fr = CMUImage(fr)
            app.player.spriteList.append(fr)
    app.player.spriteCounter = (app.player.spriteCounter + 1) % len(app.player.spriteList)
    # update location of ammo and health bars 
    app.player.ammoY = app.player.playerY - app.player.radius*1.5
    app.player.healthY = app.player.playerY - app.player.radius*2.2
    app.player.ammoX = app.player.healthX = app.player.playerX - app.player.radius

def onStep(app):
    mouseToAim(app)
    for char in app.allChars:
        rechargeHealthAndAmmo(char)
    for enemy in app.allChars[1:]:
        bulletsHit(app.player, enemy)
    
    # bullets
    bulletsMove(app.player)
    bulletOutOfRange(app.player)

    boundaryCorrection(app)
    collisionCheckWithMap(app)

def onMouseMove(app, mouseX, mouseY):
    # aim 
    app.mouseX = mouseX
    app.mouseY = mouseY

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

############################### MAP 

def boundaryCorrection(app):
    for char in app.allChars:
        if char.playerX > app.width - char.radius:
            char.playerX = app.width - char.radius
        if char.playerX < char.radius: 
            char.playerX = char.radius 
        if char.playerY > app.height - char.radius:
            char.playerY = app.height - char.radius
        if char.playerY < char.radius: 
            char.playerY = char.radius 

def fillInBoard(app):
    # coordinates with plants/blocks/water for only the top half of grid
    mapTopHalfItemsDict = {
        'p': [(1,0), (1,1), (1,2),
              (2,0), (2,1), (2,2),
              (3,0), (3,1), (3,2),
              (4,0), (4,1),
              (5,0), (5,1),
              (2,7), (2,8), (2,9), (2,10), (2,11),
              (3,7)], # green Plants
        'b': [(2,4), (2,5),
              (3,8), (3,9), (3,10), (3,11),
              (2,15)], # brown Blocks 
        'w': [(2,12), (2,13), (2,14)] # blue Water 
    } 

    # since grid is symmetric, need to add coordinates of items for bottom half of map
    # by taking (8-x, 15-y) for each coordinate tuple 
    for key in mapTopHalfItemsDict:
        listOfCoords = mapTopHalfItemsDict[key]
        for (x,y) in listOfCoords:
            bottomCoords = (8-x, 15-y)
            app.mapItemsDict[key].append((x,y))
            app.mapItemsDict[key].append(bottomCoords)
    
    # now update app.board 
    for key in app.mapItemsDict:
        listOfCoords = app.mapItemsDict[key]
        for (x,y) in listOfCoords:
            app.board[x][y] = MapItem(app, key)

def drawMapBackground(app):
    for row in range(app.rows):
        for col in range(app.cols):
            if row % 2 == col % 2:
                color = rgb(219,156,116) # dark brown
            else:
                color = rgb(236,169,124) # light brown
            drawRect(col*app.gridSize, row*app.gridSize, app.gridSize, app.gridSize,
                         align='left-top', fill=color)

def drawItemInMap(app):
    for row in range(app.rows):
        for col in range(app.cols):
            item = app.board[row][col] 
            if isinstance(item, MapItem):
                item.drawMapItem(app, row, col)  
            
def collisionCheckWithMap(app):
    for player in app.allChars:
        playerCurrRow, playerCurrCol = math.floor(player.playerY / app.gridSize), math.floor(player.playerX / app.gridSize)
        bottomCellRow, bottomCellCol = playerCurrRow+1, playerCurrCol
        topCellRow, topCellCol = playerCurrRow-1, playerCurrCol
        leftCellRow, leftCellCol = playerCurrRow, playerCurrCol-1
        rightCellRow, rightCellCol = playerCurrRow, playerCurrCol+1
        if bottomCellRow < app.rows:
            item = app.board[bottomCellRow][bottomCellCol]
            topEdge = bottomCellRow*app.gridSize 
            if isinstance(item, MapItem) and item.blocked and player.playerY > topEdge - player.radius:
                player.playerY = topEdge - player.radius 

        if topCellRow >= 0: 
            item = app.board[topCellRow][topCellCol]
            bottomEdge = topCellRow*app.gridSize + app.gridSize
            if isinstance(item, MapItem) and item.blocked and player.playerY < bottomEdge + player.radius:
                player.playerY = bottomEdge + player.radius
        
        if leftCellCol >= 0: 
            item = app.board[leftCellRow][leftCellCol]
            rightEdge = leftCellCol*app.gridSize + app.gridSize 
            if isinstance(item, MapItem) and item.blocked and player.playerX < rightEdge + player.radius:
                player.playerX = rightEdge + player.radius 
        
        if rightCellCol < app.cols:
            item = app.board[rightCellRow][rightCellCol]
            leftEdge = rightCellCol*app.gridSize
            if isinstance(item, MapItem) and item.blocked and player.playerX > leftEdge - player.radius:
                player.playerX = leftEdge - player.radius

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

    # collision check
    bulletHitsObstacle(app, app.player)

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

# bullet animation 
def bulletsMove(player):
    for i in range(len(player.bullets)):
        bullet = player.bullets[i]
        dx = 4*math.cos(bullet.bulletDirection)
        dy = 4*math.sin(bullet.bulletDirection)
        bullet.bulletX += dx
        bullet.bulletY -= dy

def shoot(player):
    # super mode 
    if player.isSuperMode and player.super.activated:
        superBullet = Bullet(player)
        superBullet.radius *= 2
        superBullet.isNormalOrSuper = "super"
        player.bullets.append(superBullet)
        player.super.activated = False 
        player.isSuperMode = False 
        player.totalDamage = 0.1
   
    # normal mode 
    else:
        ammoPerShot = player.maxAmmo / player.maxShots
        if player.currAmmo >= ammoPerShot: # if there is enough ammo 
            # ammo bar
            player.currAmmo -= ammoPerShot
            if player.currAmmo <= 0:
                player.currAmmo = 0.1

            # bullets 
            bullet = Bullet(player)
            player.bullets.append(bullet)

# bullets collision check 
def getBulletHitObstacleIndex(app, player):
    for i in range(len(player.bullets)):
        bullet = player.bullets[i]
        bulletCurrRow, bulletCurrCol = math.floor(bullet.bulletY / app.gridSize), math.floor(bullet.bulletX / app.gridSize)
        bottomCellRow, bottomCellCol = bulletCurrRow+1, bulletCurrCol
        topCellRow, topCellCol = bulletCurrRow-1, bulletCurrCol
        leftCellRow, leftCellCol = bulletCurrRow, bulletCurrCol-1
        rightCellRow, rightCellCol = bulletCurrRow, bulletCurrCol+1

        # check if bullet is spawned inside block/water
        item = app.board[bulletCurrRow][bulletCurrCol]
        if isinstance(item, MapItem) and item.blocked:
            return i 
        
        # check if bullet hits block/water 
        if bottomCellRow < app.rows:
            item = app.board[bottomCellRow][bottomCellCol]
            topEdge = bottomCellRow*app.gridSize 
            if isinstance(item, MapItem) and item.blocked and bullet.bulletY > topEdge - bullet.radius:
                return i

        if topCellRow >= 0: 
            item = app.board[topCellRow][topCellCol]
            bottomEdge = topCellRow*app.gridSize + app.gridSize
            if isinstance(item, MapItem) and item.blocked and bullet.bulletY < bottomEdge + bullet.radius:
                return i
        
        if leftCellCol >= 0: 
            item = app.board[leftCellRow][leftCellCol]
            rightEdge = leftCellCol*app.gridSize + app.gridSize 
            if isinstance(item, MapItem) and item.blocked and bullet.bulletX < rightEdge + bullet.radius:
                return i
        
        if rightCellCol < app.cols:
            item = app.board[rightCellRow][rightCellCol]
            leftEdge = rightCellCol*app.gridSize
            if isinstance(item, MapItem) and item.blocked and bullet.bulletX > leftEdge - bullet.radius:
                return i
    return None 

def bulletHitsObstacle(app, player):
    i = getBulletHitObstacleIndex(app, player)
    if i != None:
        player.bullets.pop(i)

        
# bullets hit enemy 
def getBulletHitIndex(player, enemy):
    for i in range(len(player.bullets)):
        bullet = player.bullets[i]
        if distance(bullet.bulletX, bullet.bulletY, enemy.playerX, enemy.playerY) <= (bullet.radius + enemy.radius):
            bullet.playerHit = enemy 
            enemy.currHealth = (enemy.currHealth - player.normalDamage) if bullet.isNormalOrSuper == 'normal' else (enemy.currHealth - player.superDamage)
            return i 
    return None 

def bulletsHit(player, enemy):
    i = getBulletHitIndex(player, enemy)
    if i != None: 
        isNormalOrSuper = player.bullets[i].isNormalOrSuper
        player.totalDamage = (player.totalDamage + player.normalDamage) if isNormalOrSuper == 'normal' else (player.totalDamage + player.superDamage)
        player.bullets.pop(i) # make bullet disappear 
        superActivated(player)
        if enemy.currHealth <= 0:
            enemy.currHealth = 0.1

def superActivated(player):
    if player.totalDamage >= player.damageNeeded: # to activate Super 
        player.super.activated = True 

# make bullets disappear when they reach the end of player's aim range 
def getBulletOutOfRangeIndex(player):
    playerAimLength = player.aimLength
    for i in range(len(player.bullets)):
        bullet = player.bullets[i]
        if distance(bullet.bulletX, bullet.bulletY, bullet.originalBulletX, bullet.originalBulletY) >= playerAimLength: 
            return i 
    return None 

def bulletOutOfRange(player):
    i = getBulletOutOfRangeIndex(player)
    if i != None: 
        player.bullets.pop(i)

def main():
    # map_redrawAll()
    runApp()

main()
