from game import Directions
import random
from vars import *
import math
from collections import Counter


def scoreEvaluationFunction(currentGameState):
    pos = currentGameState.getPlayerPosition()
    enemies = currentGameState.getEnemies()
    projs = currentGameState.getProjectiles()
    enemyPos = currentGameState.getEnemyPositions()
    projPos = currentGameState.getProjPositions()

    def getSquaredDistance(pos1, pos2):
        return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2

    def getManhattanDistance(pos1, pos2):
    	return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # enemyPosDiff = [getSquaredDistance(pos, enemy) for enemy in enemyPos if enemy[1] < pos[1] + PLAYER_SIZE]
    # projPosDiff = [getSquaredDistance(pos, proj) for proj in projPos if proj[1] < pos[1] + PLAYER_SIZE]
    pCenter = pos[0] + PLAYER_SIZE / 2, pos[1] + PLAYER_SIZE / 2
    enemyPosDiff = [getSquaredDistance(pCenter, (enemy[0] + ENEMY_WIDTH / 2, enemy[1] + ENEMY_HEIGHT / 2)) for enemy in enemyPos]
    projPosDiff = [getSquaredDistance(pCenter, (proj[0] + PROJECTILE_SIZE / 2, proj[1] + PROJECTILE_SIZE / 2)) for proj in projPos]

    projHorizontalDiff = [abs(proj[0] + PROJECTILE_SIZE / 2 - pCenter[0]) for proj in projPos]

    # calculate the number of threats in a range centered at player's position
    closestEnemyWeight, closestProjWeight = -50, -100
    radius = 256
    closestEnemy = 0
    for diff in enemyPosDiff:
        if diff < (2 * radius) ** 2:
            closestEnemy += radius ** 2 / diff
    closestEnemyScore = closestEnemyWeight * closestEnemy

    closestProj = 0
    for diff in projPosDiff:
        if diff < (2 * radius) ** 2:
            closestProj += radius ** 2 / diff
    closestProjScore = closestProjWeight * closestProj

    # punish the score if flying too wide
    xDeviationWeight, yDeviationWeight = -1.0 / 25, -1.0 / 50
    xDeviation = abs(pos[0] - (SCREEN_WIDTH - PLAYER_SIZE) / 2) ** 2
    yDeviation = abs(int(0.6 * SCREEN_HEIGHT) - pos[1])
    distToCenterScore = int(xDeviationWeight * xDeviation) + int(yDeviationWeight * yDeviation)

    # current game score
    gameScoreWeight = 1
    game = currentGameState.getScore()
    gameScore = gameScoreWeight * game

    # horizontal distances to enemies
    horizontalDistWeight = 1.0 / 4
    horizontalDist = [abs(pos[0] - enemy[0]) for enemy in enemyPos if enemy[1] < pos[1] + PLAYER_SIZE]
    if len(horizontalDist) == 0:
        horizontalDist = [4 * SCREEN_WIDTH]
    horizontalScore = int(horizontalDistWeight * sum(horizontalDist))

    # divide the screen into 4 pieces
    W, H = SCREEN_WIDTH, SCREEN_HEIGHT
    topleft = [(0, 0), (W / 2, 0), (0, H / 2), (W / 2, H / 2)]
    bottomright = [(W / 2, H / 2), (W, H / 2), (W / 2, H), (W, H)]
    center = []
    for i in range(len(topleft)):
    	ctr = 0.5 * (bottomright[i][0] - topleft[i][0]), 0.8 * (bottomright[i][1] - topleft[i][1])
    	center.append(ctr)
    enemyCenterOffset = ENEMY_WIDTH / 2, ENEMY_HEIGHT / 2
    projCenterOffset = PROJECTILE_SIZE / 2, PROJECTILE_SIZE / 2
    count = [0] * len(topleft)
    for enemy in enemies:
    	x, y = enemy.x + ENEMY_WIDTH, enemy.y + ENEMY_HEIGHT
    	for i in range(len(topleft)):
    		xIn = x > topleft[i][0] and x <= bottomright[i][0]
    		yIn = y > topleft[i][1] and y <= bottomright[i][1]
    		if xIn and yIn:
    			count[i] += 1
    for proj in projs:
    	x, y = proj.x + PROJECTILE_SIZE, proj.y + PROJECTILE_SIZE
    	for i in range(len(topleft)):
    		xIn = x > topleft[i][0] and x <= bottomright[i][0]
    		yIn = y > topleft[i][1] and y <= bottomright[i][1]
    		if xIn and yIn:
    			count[i] += 1
    chosenArea = min(enumerate(count))[0]
    playerCenter = pos[0] + PLAYER_SIZE / 2, pos[1] + PLAYER_SIZE / 2
    distToChosenArea = getManhattanDistance(center[chosenArea], playerCenter)
    distToAreaScore = -int(0.25 * distToChosenArea)

    minProjDist = 0
    if len(projPos) == 0:
        minProjDist = SCREEN_WIDTH
    else:
        minProjDist = min([abs(pos[0] - proj[0]) for proj in projPos])
    horizontalProjScore = minProjDist

    totalScore = [gameScore, closestEnemyScore, closestProjScore, distToCenterScore, horizontalScore, distToAreaScore]
    return sum(totalScore)


def getFeatureVector(currentGameState):
    enemyPos = currentGameState.getEnemyPositions()
    projPos = currentGameState.getProjPositions()
    pos = currentGameState.getPlayerPosition()

    def getSquaredDistance(pos1, pos2):
        return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2

    enemyPosDiff = [getSquaredDistance(pos, enemy) for enemy in enemyPos if enemy[1] < pos[1] + PLAYER_SIZE]
    projPosDiff = [getSquaredDistance(pos, proj) for proj in projPos if proj[1] < pos[1] + PLAYER_SIZE]

    features = {}
    # calculate the number of threats in a range centered at player's position
    features['radius'] = 256
    features['closestEnemy'] = 0
    for diff in enemyPosDiff:
        if diff < (2 * features['radius']) ** 2:
            features['closestEnemy'] += features['radius'] ** 2 / diff
    features['closestProj'] = 0
    for diff in projPosDiff:
        if diff < (2 * features['radius']) ** 2:
            features['closestProj'] += features['radius'] ** 2 / diff

    # punish the score if flying too wide
    features['xDeviation'] = abs(pos[0] - (SCREEN_WIDTH - PLAYER_SIZE) / 2) ** 2
    features['yDeviation'] = abs(int(0.85 * SCREEN_HEIGHT) - pos[1])

    # current game score
    features['game'] = currentGameState.getScore()

    # horizontal distances to enemies
    horizontalDist = [abs(pos[0] - enemy[0]) for enemy in enemyPos if enemy[1] < pos[1] + PLAYER_SIZE]
    if len(horizontalDist) == 0:
        horizontalDist = [4 * SCREEN_WIDTH]
    features['horizontalDist'] = sum(horizontalDist)

    return Counter(features)


def learningEvaluationFunction(currentGameState):
    enemyPos = currentGameState.getEnemyPositions()
    projPos = currentGameState.getProjPositions()
    pos = currentGameState.getPlayerPosition()
    weight = currentGameState.learner.getWeight()

    def getSquaredDistance(pos1, pos2):
        return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2

    enemyPosDiff = [getSquaredDistance(pos, enemy) for enemy in enemyPos if enemy[1] < pos[1] + PLAYER_SIZE]
    projPosDiff = [getSquaredDistance(pos, proj) for proj in projPos if proj[1] < pos[1] + PLAYER_SIZE]

    features = {}
    # calculate the number of threats in a range centered at player's position
    features['radius'] = 256
    features['closestEnemy'] = 0
    for diff in enemyPosDiff:
        if diff < (2 * features['radius']) ** 2:
            features['closestEnemy'] += features['radius'] ** 2 / diff
    features['closestProj'] = 0
    for diff in projPosDiff:
        if diff < (2 * features['radius']) ** 2:
            features['closestProj'] += features['radius'] ** 2 / diff

    # punish the score if flying too wide
    features['xDeviation'] = abs(pos[0] - (SCREEN_WIDTH - PLAYER_SIZE) / 2) ** 2
    features['yDeviation'] = abs(int(0.85 * SCREEN_HEIGHT) - pos[1])

    # current game score
    features['game'] = currentGameState.getScore()

    # horizontal distances to enemies
    horizontalDist = [abs(pos[0] - enemy[0]) for enemy in enemyPos if enemy[1] < pos[1] + PLAYER_SIZE]
    if len(horizontalDist) == 0:
        horizontalDist = [4 * SCREEN_WIDTH]
    features['horizontalDist'] = sum(horizontalDist)

    features = Counter(features)
    totalScore = 0
    for k in features:
    	if k == 'radius':
    		continue
    	totalScore += features[k] * weight[k]
    return totalScore


def shootScoreEvaluationFunction(currentGameState):
    enemyPos = currentGameState.getEnemyPositions()
    pos = currentGameState.getPlayerPosition()
    missilePos = currentGameState.getMissilePositions()
    enemies = currentGameState.getEnemies()
    projs = currentGameState.getProjectiles()
    numMissile = len(missilePos)
    numEnemy = len(enemyPos)

    playerCenter = pos[0] + PLAYER_SIZE / 2, pos[1] + PLAYER_SIZE / 2

    # missileScore = 0
    # for proj in projs:
    # 	px, py = proj.x + PROJECTILE_SIZE / 2 + proj.speed_x, proj.y + PROJECTILE_SIZE / 2 + proj.speed_y
    # 	if abs(playerCenter[0] - px) < (PLAYER_SIZE + PROJECTILE_SIZE) / 2 and abs(playerCenter[1] - py) < (PLAYER_SIZE + ENEMY_HEIGHT) / 2:
    # 		missileScore = -10000
    # 		break
    # for enemy in enemies:
    # 	ex, ey = enemy.x + ENEMY_HEIGHT / 2 + enemy.speed_x, enemy.y + ENEMY_WIDTH / 2 + enemy.speed_y
    # 	if abs(playerCenter[0] - ex) < (PLAYER_SIZE + ENEMY_WIDTH) / 2 and abs(playerCenter[1] - ey) < (PLAYER_SIZE + ENEMY_HEIGHT) / 2:
    # 		missileScore = -10000
    # 		break

    hitOffset = 0.5 * MISSILE_WIDTH, 0.5 * MISSILE_HEIGHT
    # if numMissile > 0 or pos[1] < 0.8 * SCREEN_HEIGHT:
    if numMissile > 0 or pos[1] < 0.1 * SCREEN_HEIGHT:
    	missileScore = -10000
    else:
    	missileScore = -10000
    	mx, my = playerCenter
    	for enemy in enemies:
	    	x, y = enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2
	    	if y < 0 or y > my - PLAYER_SIZE / 2 - ENEMY_HEIGHT / 2:
	    		continue
	        vx, vy = enemy.speed_x, enemy.speed_y
	        for t in range(1, my / MISSILE_SPEED):
	            newEnemyPos = x + vx * t, y + vy * t
	            newMislePos = mx, my - MISSILE_SPEED * t
	            checkX = abs(newEnemyPos[0] - newMislePos[0]) < (ENEMY_WIDTH + MISSILE_WIDTH) / 2 - hitOffset[0]
	            checkY = abs(newEnemyPos[1] - newMislePos[1]) < (ENEMY_HEIGHT + MISSILE_HEIGHT) / 2 - hitOffset[1]
	            if checkX and checkY:
	                missileScore = 10000
	                break

    # current game score
    gameScore = currentGameState.getScore()

    totalScore = [gameScore, missileScore]
    return sum(totalScore)


def getShootFeatureVector(currentGameState):
    enemyPos = currentGameState.getEnemyPositions()
    pos = currentGameState.getPlayerPosition()
    missilePos = currentGameState.getMissilePositions()
    enemies = currentGameState.getEnemies()
    numMissile = len(missilePos)
    numEnemy = len(enemyPos)

    features = {}    
    features['heightPortion'] = 0.8
    offset = (PLAYER_SIZE - MISSILE_WIDTH) / 2, (PLAYER_SIZE - MISSILE_HEIGHT) / 2
    if numMissile >= 1 or pos[1] < features['heightPortion'] * SCREEN_HEIGHT:
    	features['missileScore'] = -10000
    else:
	    features['missileScore'] = -10000
	    rx = (ENEMY_WIDTH + MISSILE_WIDTH) / 2
	    mx, my = pos[0] + offset[0] + MISSILE_WIDTH / 2, pos[1] + offset[1] + MISSILE_HEIGHT / 2
	    for enemy in enemies:
	    	x, y = enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2
	    	if abs(x - mx) < rx and y >= 0 and y < my:
	    		features['missileScore'] = 1000
	    		break

    # current game score
    features['game'] = currentGameState.getScore()

    return Counter(features)


class Agent:
    def __init__(self, depth=1):
        self.index = 0
        self.depth = depth
        self.evaluationFunction = scoreEvaluationFunction
        # self.evaluationFunction = ultimateEvaluationFunction
        self.shootEvaluationFunction = shootScoreEvaluationFunction
        self.depth = int(depth)


class AlphaBetaAgent(Agent):
    def getAction(self, gameState):
        def recurse(state, index, depth, lowerBound, upperBound):
            # check if it's the terminal state
            if state.isWin() or state.isLose():
                return state.getScore(), Directions.STOP
            if len(state.getLegalActions(index)) == 0 or depth == 0:
                return self.evaluationFunction(state), Directions.STOP

            nextIndex = (index + 1) % state.getNumAgents()
            nextDepth = depth - 1 if nextIndex == (self.index - 1) % state.getNumAgents() else depth

            legalActions = state.getLegalActions(index)
            choices = []
            for legalAction in legalActions:
            	if legalAction == Directions.SHOOT:
            		value = self.shootEvaluationFunction(state)
            	else:
                	value, _ = recurse(state.generateSuccessor(index, legalAction), nextIndex, nextDepth, lowerBound, upperBound)
                choices.append((value, legalAction))
                if index == 0:
                    lowerBound = max(value, lowerBound)
                else:
                    upperBound = min(value, upperBound)
                if lowerBound > upperBound:
                    break
            # return max value if it's agent otherwise min if it's opponent
            chosenValue = max(choices) if index == 0 else min(choices)
            indices = [i for i in range(len(choices)) if choices[i][0] == chosenValue[0]]
            chosenIndex = random.choice(indices)  # Pick randomly among max
            action = legalActions[chosenIndex]
            return chosenValue[0], action

        value, action = recurse(gameState, self.index, self.depth, -INF, INF)
        return action


class ExpectimaxAgent(Agent):
    def getAction(self, gameState):
        def recurse(state, index, depth):
            # check if it's the terminal state
            # choices = [Directions.UP, Directions.DOWN, Directions.LEFT, Directions.RIGHT]
            if state.isWin() or state.isLose():
                return state.getScore(), Directions.STOP
            if len(state.getLegalActions(index)) == 0 or depth == 0:
                return self.evaluationFunction(state), Directions.STOP

            nextIndex = (index + 1) % state.getNumAgents()
            nextDepth = depth - 1 if nextIndex == state.getNumAgents() - 1 else depth
            # compute the recursion
            values = []
            choices = []
            legalActions = state.getLegalActions(index)
            for legalAction in legalActions:
            	if legalAction == Directions.SHOOT:
            		value = self.shootEvaluationFunction(state)
            	else:
                	value = recurse(state.generateSuccessor(index, legalAction), nextIndex, nextDepth)[0]
                choices.append((value, legalAction))
                values.append(value)
            maxValue = max(choices)[0]
            newChoices = [choice for choice in choices if choice[0] == maxValue]
            mean = sum(values) / len(values)
            # if Directions.LEFT in newChoices and Directions.RIGHT in newChoices and Directions.DOWN in choices:
            #     newChoices.remove(Directions.DOWN)
            return (mean, random.choice(legalActions)) if index != 0 else (maxValue, random.choice(newChoices)[1])

        value, action = recurse(gameState, self.index, self.depth)
        return action
