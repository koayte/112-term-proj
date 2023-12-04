from cmu_graphics import *
from PIL import Image
import math
import random
from classes import * 

def enemyMovesTowardsPlayer(app, enemy):
    # get coordsList
    enemyRow = math.floor(enemy.playerY / app.gridSize)
    enemyCol = math.floor(enemy.playerX / app.gridSize)
    playerRow = math.floor(app.player.playerY / app.gridSize)
    playerCol = math.floor(app.player.playerX / app.gridSize)
    if (enemyRow, enemyCol) != (playerRow, playerCol):
        coordsList = dijkstra(app, enemyRow, enemyCol, playerRow, playerCol)[0]
    else:
        coordsList = []
    enemy.coordsList = coordsList 
    # move 
    if coordsList != []:
        enemyMoves(app, enemy, coordsList)

def enemyMovesTowardsBush(app, enemy):
    enemyRow = math.floor(enemy.playerY / app.gridSize)
    enemyCol = math.floor(enemy.playerX / app.gridSize)
    coordsList = [] # to nearest bush 
    shortestDistance = 100000
    for row in range(app.rows):
        for col in range(app.cols):
            item = app.board[row][col]
            if isinstance(item, MapItem) and item.blocked == False: # item is bush
                if (enemyRow, enemyCol) != (row, col): # move towards grass if not there yet
                    currCoordsList, distance = dijkstra(app, enemyRow, enemyCol, row, col)
                    if distance < shortestDistance: 
                        coordsList = currCoordsList
                        shortestDistance = distance 
                else:
                    coordsList = [] # stop moving 
    enemy.coordsList = coordsList 
    # if coordsList != []:
    #     enemyMoves(app, enemy, coordsList)

def whereEnemyMoves(app, enemy):
    # MOVES 
    threshold = enemy.maxHealth // 2
    enemyRow = math.floor(enemy.playerY / app.gridSize)
    enemyCol = math.floor(enemy.playerX / app.gridSize)
    playerRow = math.floor(app.player.playerY / app.gridSize)
    playerCol = math.floor(app.player.playerX / app.gridSize)
    if enemy.currHealth > threshold:
        # move towards player if not there yet
        if (enemyRow, enemyCol) != (playerRow, playerCol):
            coordsList = dijkstra(app, enemyRow, enemyCol, playerRow, playerCol)[0]
        else:
            coordsList = [] # stop moving 
    else:
        # move towards nearest bush to regenerate 
        coordsList = None # to nearest bush 
        
        shortestDistance = 100000
        for row in range(app.rows):
            for col in range(app.cols):
                item = app.board[row][col]
                if isinstance(item, MapItem) and item.blocked == False: # item is bush
                    if (enemyRow, enemyCol) != (row, col): # move towards grass if not there yet
                        currCoordsList, distance = dijkstra(app, enemyRow, enemyCol, row, col)
                        if distance < shortestDistance: 
                            coordsList = currCoordsList
                            shortestDistance = distance 
                    else:
                        coordsList = [] # stop moving 
    return coordsList

def enemyMoves(app, enemy, coordsList):
    # navigation (moving to coords specified by Dijkstra's)
    enemyRow = math.floor(enemy.playerY / app.gridSize)
    enemyCol = math.floor(enemy.playerX / app.gridSize)
    nextRow, nextCol = coordsList[0][0], coordsList[0][1]
    if (enemyRow, enemyCol) != (nextRow, nextCol):
        drow = nextRow - enemyRow 
        dcol = nextCol - enemyCol 
        enemy.spriteDirection = 'right' if dcol > 0 else 'left'
        enemy.playerX += (enemy.charSpeed * dcol) 
        enemy.playerY += (enemy.charSpeed * drow)
        # update location of ammo and health bars 
        enemy.ammoY = enemy.playerY - enemy.radius*1.5
        enemy.healthY = enemy.playerY - enemy.radius*2.2
        enemy.ammoX = enemy.healthX = enemy.playerX - enemy.radius
    else: 
        coordsList.pop(0) # go to next (nextRow, nextCol)
    
    # enemy animation 
    if enemy.spriteDirection == 'right':
        enemy.spriteCounterRight = (enemy.spriteCounterRight + 1) % len(enemy.spriteListRight)
    else:
        enemy.spriteCounterLeft = (enemy.spriteCounterLeft + 1) % len(enemy.spriteListLeft)

############################### DIJKSTRA

def dijkstra(app, startCellRow, startCellCol, endCellRow, endCellCol):
    # unvisited set: all nodes except for obstacles 
    # dictionary of distance of node from start (infinity for everything, 0 for start)
    # dictionary of each node to its parent (empty at first. key is node, value is parent)
    # while len(unvisited) > 0:
        # choose unvisited with minimum distance (will be start initially)
        # if node == end:
            # while loop? while parent is not startCell?
                # get parent (value)
                # add into list? 
                # return list?
        # remove node from unvisited list
        # loop through all 8 directions dx,dy
            # add to startCellRow/Col
            # if valid (within boundaries, NOT mapitem, unvisited)
                # get distance from start to current node (from dictionary)
                # get distance (cost) from current node to neighbor 
                # add to get D
                # if D < dictionary.get(D):
                    # update distance dictionary 
                    # update parents dictionary 

    unvisited = initializeUnvisited(app)
    distFrStartDict = initializeDistDict(unvisited, startCellRow, startCellCol)
    parentDict = dict()
    for coords in unvisited:
        parentDict[coords] = None 

    while len(unvisited) > 0:
        currCell = min(unvisited, key=distFrStartDict.get) # might replace with a priority queue?
        if currCell == (endCellRow, endCellCol):
            path = []
            path.append((endCellRow, endCellCol))
            parentOfCurr = parentDict[currCell]
            path.append(parentOfCurr)
            i = 0 
            while parentOfCurr != (startCellRow, startCellCol):
                parentOfCurr = parentDict[parentOfCurr]
                path.append(parentOfCurr)
                i += 1
            path.pop() # remove (startCellRow, startCellCol)
            return (path[::-1], distFrStartDict[currCell])
        unvisited.remove(currCell)
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                nextCellRow, nextCellCol = currCell[0] + dx, currCell[1] + dy
                if validNextCell(app, unvisited, nextCellRow, nextCellCol):
                    distFrStartToCurr = distFrStartDict[currCell]
                    # cost is sqrt(2) for 4 diagonals, 1 for other directions 
                    costToNextCell = math.sqrt(2) if (dx != 0 and dy != 0) else 1 
                    distFrStartToNext = distFrStartToCurr + costToNextCell
                    if distFrStartToNext < distFrStartDict[(nextCellRow, nextCellCol)]:
                        distFrStartDict[(nextCellRow, nextCellCol)] = distFrStartToNext
                        parentDict[(nextCellRow, nextCellCol)] = currCell


def validNextCell(app, unvisited, nextCellRow, nextCellCol):
    # out of boundaries 
    if nextCellRow < 0 or nextCellRow >= app.rows or nextCellCol < 0 or nextCellCol >= app.cols:
        return False 
    
    # is an obstacle (water or brick)
    cell = app.board[nextCellRow][nextCellCol]
    if isinstance(cell, MapItem) and (cell.item == 'w' or cell.item == 'b'): 
        return False 

    # has already been visited 
    if (nextCellRow, nextCellCol) not in unvisited:
        return False
    
    return True 

def initializeUnvisited(app):
    unvisited = set()
    for row in range(app.rows):
        for col in range(app.cols):
            if not isinstance(app.board[row][col], MapItem): # empty space 
                unvisited.add((row, col))
            else:
                if app.board[row][col].item == 'p':
                    unvisited.add((row, col)) # bushes are not obstacles 
    return unvisited

def initializeDistDict(unvisited, startCellRow, startCellCol):
    distFrStartDict = dict()
    for coords in unvisited:
        distFrStartDict[coords] = 10000 # some large enough number 
    distFrStartDict[(startCellRow, startCellCol)] = 0
    return distFrStartDict