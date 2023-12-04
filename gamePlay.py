from cmu_graphics import *
import math
from PIL import Image
import random
from classes import *
from map import *
from bot import *

############################### EVENTS 

def newRound(app):
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
    app.onStepCounter = 0
    app.mouseX = 0
    app.mouseY = 0
    app.gameOver = False 

    # player (user)
    app.radius = app.gridSize/2 
    app.player = Player('player', app, 7.5*app.gridSize, 8.5*app.gridSize, app.radius, aimLength=250, aimAngle=0.1, aimDirection=0, 
                        charSpeed=3, healSpeed=0.7, normalDamage=150, superDamage=400, damageNeeded=2000)

    # enemy player 
    app.enemy1 = Player('enemy1', app, 7.5*app.gridSize, 0.5*app.gridSize, app.radius, aimLength=250, aimAngle=0.1, aimDirection=0, 
                        charSpeed=2.5, healSpeed=0.7, normalDamage=150, superDamage=400, damageNeeded=2000)
    # app.enemy2 = Player(app, app.width/2-200, app.height/2, app.radius, aimLength=300, aimAngle=0.1, aimDirection=0, 
    #                     charSpeed=2, healSpeed=0.7, normalDamage=150, superDamage=400, damageNeeded=2000)

    app.allChars = [app.player, app.enemy1]
    app.enemies = [app.enemy1]

    app.roundLoser = None 
    app.newRoundButton = Button(app.width/2, app.height/2, 'NEXT ROUND', width=400, height=60, size=30)
    # app.roundWinner = None 
    # app.newGameButton.clicked = False 

def newMatch(app):
    newRound(app)
    app.roundLosers = []
    app.playerRoundOutcomes = [None, None, None]
    app.roundNum = 0
    app.matchWinner = None 
    app.startMatchButton = Button(app.width/2, app.height/2, 'START GAME', width=400, height=60, size=30)
    app.isNewMatch = True 
    app.newMatchButton = Button(app.width/2, app.height/2, 'NEW GAME', width=400, height=60, size=30)

def onAppStart(app):
    newMatch(app)

def redrawAll(app):
    drawMapBackground(app)
    drawItemInMap(app)
    if app.isNewMatch == False:
        drawEachPlayer(app, app.player)
        drawEachPlayer(app, app.enemy1)
        app.player.super.drawSuper(app.player)
        if app.player.isSuperMode: 
            mode = 'SUPER'
        else:
            mode = 'NORMAL'
        drawLabel(f'{mode}', app.width-150, app.height-80, size=16, font='orbitron')

        for i in range(len(app.allChars)):
            char = app.allChars[i]
            for j in range(len(char.bullets)):
                bullet = char.bullets[j]
                bullet.drawBullet(app)

        # scores 
        drawRounds(app)

    # match start 
    
    if app.isNewMatch and app.roundNum == 0:
        drawStartScreen(app)

    # game over 
    if app.gameOver:  
        drawEndScreen(app)
        
def drawEachPlayer(app, character):
    if character not in app.enemies:
        character.drawRange(app)
    
    # if character is hidden in grass
    if character.hidden == True:
        character.opacity = 60 if character == app.player else 0
    else:
        character.opacity = 100
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
    if app.gameOver == False:
        shoot(app.player)
    
    # start match (round 1) button
    if app.isNewMatch and app.roundNum == 0:
        app.startMatchButton.buttonClick(mouseX, mouseY)
        if app.startMatchButton.clicked:
            newRound(app)
            app.isNewMatch = False 

    # end of each round screen
    if app.gameOver and app.roundNum < 3: 
        app.newRoundButton.buttonClick(mouseX, mouseY)
        if app.newRoundButton.clicked: 
            newRound(app)
    
    # end of round 3 screen
    if app.gameOver and app.roundNum == 3: 
        app.newMatchButton.buttonClick(mouseX, mouseY)
        if app.newMatchButton.clicked: 
            newMatch(app)
    
        
def onKeyHold(app, keys):
    # navigation
    if app.gameOver == False and app.isNewMatch == False:
        if 'w' in keys and 's' not in keys:
            app.player.playerY -= app.player.charSpeed
        elif 'w' not in keys and 's' in keys:
            app.player.playerY += app.player.charSpeed
        if 'a' in keys and 'd' not in keys:
            app.player.playerX -= app.player.charSpeed 
            app.player.spriteDirection = 'left'
        elif 'a' not in keys and 'd' in keys:
            app.player.playerX += app.player.charSpeed 
            app.player.spriteDirection = 'right'

        # sprite walking animation
        if app.player.spriteDirection == 'right':
            app.player.spriteCounterRight = (app.player.spriteCounterRight + 1) % len(app.player.spriteListRight)
        else:
            app.player.spriteCounterLeft = (app.player.spriteCounterLeft + 1) % len(app.player.spriteListLeft)
        
        # update location of ammo and health bars 
        app.player.ammoY = app.player.playerY - app.player.radius*1.5
        app.player.healthY = app.player.playerY - app.player.radius*2.2
        app.player.ammoX = app.player.healthX = app.player.playerX - app.player.radius

def onStep(app):
    if app.gameOver == False and app.isNewMatch == False:
        app.onStepCounter += 1
        mouseToAim(app)
        for char in app.allChars:
            rechargeHealthAndAmmo(app, char)
            bulletsMove(char)
            bulletOutOfRange(char)
            bulletHitsObstacle(app, char)
        
        bulletsHit(app.player, app.enemy1)
        bulletsHit(app.enemy1, app.player)
    
        boundaryCorrection(app)
        collisionCheckWithMap(app)

        # bots 
        threshold = app.enemy1.maxHealth // 2
        if app.enemy1.currHealth > threshold:
            enemyMovesTowardsPlayer(app, app.enemy1)
        else:
            app.enemy1.hiding = True
            if app.onStepCounter % 60 == 0:
                enemyMovesTowardsBush(app, app.enemy1)
            if app.enemy1.coordsList != []:
                enemyMoves(app, app.enemy1, app.enemy1.coordsList)

        calculateAimDirection(app, app.enemy1, app.enemy1.playerX, app.enemy1.playerY, 
                                app.player.playerX, app.player.playerY)
        if app.onStepCounter % random.randrange(20,90) == 0: # make bots' shot timings arbitrary
            if app.enemy1.super.activated: 
                app.enemy1.isSuperMode = random.choice([True, False])
            shoot(app.enemy1)
        
        # win/lose condition 
        whoLosesRound(app)
    
    else:
        whoWinsMatch(app)


def onMouseMove(app, mouseX, mouseY):
    # aim 
    app.mouseX = mouseX
    app.mouseY = mouseY

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

############################### HEALTH 

def rechargeHealthAndAmmo(app, player):
    if app.gameOver == False:
        if player.currHealth < player.maxHealth: 
            player.currHealth += player.healSpeed
            if player.currHealth > player.maxHealth:
                player.currHealth = player.maxHealth
        
        if player.currAmmo < player.maxAmmo:
            player.currAmmo += 6

############################### AIM AND SHOOT  

def calculateAimDirection(app, player, playerX, playerY, targetX, targetY):
    # set aim direction (angle)
    straightDist = distance(playerX, playerY, targetX, targetY)
    adjOverHypFraction = (targetX - playerX) / straightDist if straightDist != 0 else 1
    if targetY > playerY: # target is below player
        player.aimDirection = -1*math.acos(adjOverHypFraction)
    else: 
        player.aimDirection = math.acos(adjOverHypFraction)
    
    # straight aim line angle 
    player.aimLineX = player.playerX + player.aimLength*math.cos(player.aimDirection)
    player.aimLineY = player.playerY - player.aimLength*math.sin(player.aimDirection)

    # triangular range 
    rangeSideLen = player.aimLength / math.cos(player.aimAngle / 2)
    rangeLineOneAngle = player.aimAngle/2 + player.aimDirection 
    player.rangeLineOneX = player.playerX + rangeSideLen*math.cos(rangeLineOneAngle)
    player.rangeLineOneY = player.playerY - rangeSideLen*math.sin(rangeLineOneAngle)
    rangeLineTwoAngle = player.aimDirection - player.aimAngle/2
    player.rangeLineTwoX = player.playerX + rangeSideLen*math.cos(rangeLineTwoAngle)
    player.rangeLineTwoY = player.playerY - rangeSideLen*math.sin(rangeLineTwoAngle)
    player.rangeCoords = [player.playerX, player.playerY, player.rangeLineOneX, 
                              player.rangeLineOneY, player.rangeLineTwoX, player.rangeLineTwoY]


def mouseToAim(app):
    calculateAimDirection(app, app.player, app.player.playerX, app.player.playerY, app.mouseX, app.mouseY)

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

        # check if bullet is within screen boundaries 
        if (bullet.bulletX < 0 or bullet.bulletX > app.width or 
        bullet.bulletY < 0 or bullet.bulletY > app.height):
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
        
        # check if bullet is spawned inside block/water
        item = app.board[bulletCurrRow][bulletCurrCol]
        if isinstance(item, MapItem) and item.blocked:
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

############################### WIN / LOSE / SCORING 

def whoLosesRound(app):
    for char in app.allChars: 
        if char.currHealth <= 0.1: 
            app.roundLoser = char 
            app.playerRoundOutcomes[app.roundNum] = 0 if app.roundLoser == app.player else 1
            app.roundNum += 1
            app.gameOver = True 
            

def drawRounds(app):
    for i in range(len(app.playerRoundOutcomes)):
        outcome = app.playerRoundOutcomes[i]
        if outcome == 1: 
            color = 'cyan'
        elif outcome == 0: 
            color = 'red'
        elif outcome == None: 
            color = 'white'
        radius = 20
        startX, startY = app.width / 2 - 50, 50
        drawCircle(startX + 50*i, startY, radius, fill=color)

def whoWinsMatch(app):
    if app.roundNum == 3: 
        numWins = app.playerRoundOutcomes.count(1)
        if numWins >= 2: 
            app.matchWinner = app.player 
        else:
            app.matchWinner = app.enemy1

def drawEndScreen(app):
    drawRect(0, 0, app.width, app.height, fill='black', opacity=80)
    # in between rounds
    if app.roundNum < 3: 
        if app.roundLoser == app.player:
            label = 'LOST'
        else:
            label = 'WON'
        drawLabel(f'ROUND {app.roundNum} {label}', app.width/2, app.height/2-80, 
                fill='white', size=50, font='orbitron', bold=True, align='center')
        app.newRoundButton.drawButton()
    
    # last round finished 
    elif app.roundNum == 3: 
        if app.matchWinner == app.player: 
            label = 'WON'
        else:
            label = 'LOST'
        drawLabel(f'MATCH {label}', app.width/2, app.height/2-80,
                fill='white', size=50, font='orbitron', bold=True, align='center')
        app.newMatchButton.drawButton()

############################### START GAME
def drawStartScreen(app):
    # start
    drawRect(0, 0, app.width, app.height, fill='black', opacity=80)
    drawLabel('WELCOME TO BRAWL BARS!', app.width/2, app.height/2-80, fill='white', align='center', size=50, 
                bold=True, font='orbitron')
    app.startMatchButton.drawButton()
        
def main():
    runApp()
    
main()
