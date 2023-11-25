mapItemsDict = {
        'p': [(1,0), (1,1), (1,2),
              (2,0), (2,1), (2,2),
              (3,0), (3,1), (3,2),
              (4,0), (4,1),
              (5,1), (5,2),
              (2,7), (2,8), (2,9), (2,10), (2,11),
              (3,7)], # green Plants
        'b': [(2,4), (2,5),
              (3,8), (3,9), (3,10), (3,11),
              (2,15)], # brown Blocks 
        'w': [(2,12), (2,13), (2,14)] # blue Water 
    }

def fillInBoard():
    # since grid is symmetric, need to add coordinates of items for bottom half of map
    # by taking (8-x, 15-y) for each coordinate tuple 
    for key in mapItemsDict:
        listOfCoords = mapItemsDict[key]
        for (x,y) in listOfCoords:
            bottomCoords = (8-x, 15-y)
            print(bottomCoords)
            mapItemsDict[key].append(bottomCoords)
    print(mapItemsDict)

fillInBoard()