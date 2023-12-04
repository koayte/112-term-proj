from cmu_graphics import *
from PIL import Image
import math
import random
from classes import * 

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
              (3,8), (3,9), (3,10), (3,11)], # brown Blocks 
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
        
        # collision check with obstacles 
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

        # hide in grass 
        item = app.board[playerCurrRow][playerCurrCol]
        if isinstance(item, MapItem) and item.blocked == False: 
            player.hidden = True 
        else:
            player.hidden = False 