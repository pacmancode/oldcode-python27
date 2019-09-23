import pygame
from entities import MazeMouse
from constants import *
from vectors import Vector2D
from random import randint
from stacks import Stack

class Mode(object):
    def __init__(self, name="", time=None, speedMult=1):
        self.name = name
        self.time = time
        self.speedMult = speedMult


class Ghost(MazeMouse):
    def __init__(self, nodes, level, spritesheet):
        MazeMouse.__init__(self, nodes, level, spritesheet)
        self.name = "ghost"
        self.goal = Vector2D()
        self.modeStack = self.setupModeStack()
        self.mode = self.modeStack.pop()
        self.modeTimer = 0
        self.homeNode = None
        self.startDirection = UP
        self.exitHome = True
        self.guideDog = False
        self.leftHome = True
        self.previousDirection = None

    def setGuideStack(self):
        self.guideStack = Stack()
        self.guideStack.push(LEFT)
        self.guideStack.push(UP)

    def getStartNode(self):
        node = MAZEDATA[self.level]["start"]["ghost"]
        return self.nodes.getNode(*node, nodeList=self.nodes.homeList)

    def setStartPosition(self):
        self.setHomeNode()
        self.direction = self.startDirection
        self.target = self.node.neighbors[self.direction]
        self.setPosition()
        self.checkDirectionChange()

    def checkDirectionChange(self):
        if self.direction != self.previousDirection:
            self.previousDirection = self.direction
            row = self.imageRow
            col = 0 
            if self.mode.name == "SPAWN":
                row, col = self.setSpawnImages()
            elif self.mode.name != "FREIGHT":
                if self.direction == LEFT:
                    col = 4
                elif self.direction == RIGHT:
                    col = 6
                elif self.direction == DOWN:
                    col = 2
                elif self.direction == UP:
                    col = 0

            self.setImage(row, col)

    def setImage(self, row, col):
        self.image = self.spritesheet.getImage(col, row, 32, 32)

    def setSpawnImages(self):
        row = 6
        if self.direction == LEFT:
            col = 6
        elif self.direction == RIGHT:
            col = 7
        elif self.direction == DOWN:
            col = 4
        elif self.direction == UP:
            col = 5
        return row, col

    def getClosestDirection(self, validDirections):
        distances = []
        for direction in validDirections:
            diffVec = self.node.position + direction*WIDTH - self.goal
            distances.append(diffVec.magnitudeSquared())
        index = distances.index(min(distances))
        return validDirections[index]

    def getValidDirections(self):
        validDirections = []
        for key in self.node.neighbors.keys():
            if self.node.neighbors[key] is not None:
                if not key == self.direction * -1:
                    validDirections.append(key)
        if len(validDirections) == 0:
            validDirections.append(self.forceBacktrack())

        if (self.node.home and DOWN in validDirections and self.mode.name != "SPAWN"):
            validDirections.remove(DOWN)

        if self.node.nowayUp and UP in validDirections:
            validDirections.remove(UP)

        if not self.leftHome:
            if self.exitHome:
                validDirections = self.guideOutOfHome(validDirections)
            else:
                validDirections = self.trapInHome(validDirections)

        return validDirections

    def randomDirection(self, validDirections):
        index = randint(0, len(validDirections) - 1)
        return validDirections[index]

    def moveBySelf(self):
        if self.overshotTarget():
            self.node = self.target
            self.portal()
            validDirections = self.getValidDirections()
            self.direction = self.getClosestDirection(validDirections)
            self.target = self.node.neighbors[self.direction]
            self.setPosition()
            if self.mode.name == "SPAWN":
                if self.position == self.goal:
                    self.mode = self.modeStack.pop()

    def forceBacktrack(self):
        if self.direction * -1 == UP:
            return UP
        if self.direction * -1 == DOWN:
            return DOWN
        if self.direction * -1 == LEFT:
            return LEFT
        if self.direction * -1 == RIGHT:
            return RIGHT

    def setupModeStack(self):
        modes = Stack()
        modes.push(Mode(name="CHASE"))
        modes.push(Mode(name="SCATTER", time=5))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        return modes

    def setScatterGoal(self):
        self.goal = Vector2D()

    def setChaseGoal(self, pacman):
        self.goal = pacman.position

    def modeUpdate(self, dt):
        self.modeTimer += dt
        if self.mode.time is not None:
            if self.modeTimer >= self.mode.time:
                self.reverseGhostDirection()
                self.mode = self.modeStack.pop()
                self.modeTimer = 0

    def update(self, dt, pacman, blinky):
        speedMod = self.modifySpeed()
        self.position += self.direction*speedMod*dt
        self.modeUpdate(dt)
        if self.mode.name == "CHASE":
            self.setChaseGoal(pacman, blinky)
        elif self.mode.name == "SCATTER":
            self.setScatterGoal()
        elif self.mode.name == "FREIGHT":
            self.setRandomGoal()
        elif self.mode.name == "SPAWN":
            self.setSpawnGoal()
        self.moveBySelf()
        if self.mode.name != "FREIGHT":
            self.checkDirectionChange()
        else:
            if (self.mode.time - self.modeTimer) < 1:
                self.setImage(6, 2)

                
    def modifySpeed(self):
        if (self.node.portalNode is not None or self.target.portalNode is not None):
            return self.speed / 2.0
        return self.speed * self.mode.speedMult

    def setFreightMode(self):
        if self.mode.name != "SPAWN":
            if self.mode.name != "FREIGHT":
                if self.mode.time is not None:
                    dt = self.mode.time - self.modeTimer
                    self.modeStack.push(Mode(name=self.mode.name, time=dt))
                else:
                    self.modeStack.push(Mode(name=self.mode.name))
                self.reverseGhostDirection()
                self.mode = Mode("FREIGHT", time=7, speedMult=0.5)
                self.modeTimer = 0
            
            else:
                self.mode = Mode("FREIGHT", time=7, speedMult=0.5)
                self.modeTimer = 0
            self.setImage(6, 0)

    def setRandomGoal(self):
        x = randint(0, NCOLS*WIDTH)
        y = randint(0, NROWS*HEIGHT)
        self.goal = Vector2D(x, y)

    def setRespawnMode(self):
        self.mode = Mode("SPAWN", speedMult=2)
        self.modeTimer = 0
        self.setGuideStack()
        self.leftHome = False

    def setSpawnGoal(self):
        self.goal = self.homeNode.position

    def trapInHome(self, validDirections):
        if LEFT in validDirections:
            validDirections.remove(LEFT)
        if RIGHT in validDirections:
            validDirections.remove(RIGHT)
        return validDirections

    def guideOutOfHome(self, validDirections):
        if not self.guideDog:
            if self.target == self.homeNode:
                self.guideDog = True
                validDirections = []
                validDirections.append(self.guideStack.pop())
        else:
            validDirections = []
            validDirections.append(self.guideStack.pop())
            if self.guideStack.isEmpty():
                self.guideDog = False
                self.leftHome = True
        return validDirections

    def reverseGhostDirection(self):
        if self.leftHome:
            self.reverseDirection()


class Blinky(Ghost):
    def __init__(self, nodes, level, spritesheet):
        Ghost.__init__(self, nodes, level, spritesheet)
        self.name = "blinky"
        self.color = RED
        self.startDirection = LEFT
        self.imageRow = 2
        #self.imageCol = 0
        self.setStartPosition()
        #self.image = spritesheet.getImage(0, 2, 32, 32)

    def setHomeNode(self):
        node = self.getStartNode()
        self.homeNode = node
        self.node = self.homeNode.neighbors[UP]

    def setScatterGoal(self):
        self.goal = Vector2D(WIDTH * (NCOLS-6), 0)

    def setChaseGoal(self, pacman, blinky=None):
        self.goal = pacman.position


class Pinky(Ghost):
    def __init__(self, nodes, level, spritesheet):
        Ghost.__init__(self, nodes, level, spritesheet)
        self.name = "pinky"
        self.color = PINK
        self.imageRow = 3
        self.imageCol = 0
        self.setStartPosition()
        #self.image = spritesheet.getImage(0, 3, 32, 32)

    def setHomeNode(self):
        node = self.getStartNode()
        self.homeNode = node
        self.node = node

    def setScatterGoal(self):
        self.goal = Vector2D()

    def setChaseGoal(self, pacman, blinky=None):
        self.goal = pacman.position + pacman.direction * WIDTH * 4


class Inky(Ghost):
    def __init__(self, nodes, level, spritesheet):
        Ghost.__init__(self, nodes, level, spritesheet)
        self.name = "inky"
        self.color = TEAL
        self.startDirection = DOWN
        self.imageRow = 4
        self.imageCol = 0
        self.setStartPosition()
        self.setGuideStack()
        self.leftHome = False
        self.exitHome = False
        #self.image = spritesheet.getImage(0, 4, 32, 32)

    def setGuideStack(self):
        self.guideStack = Stack()
        self.guideStack.push(LEFT)
        self.guideStack.push(UP)
        self.guideStack.push(RIGHT)

    def setHomeNode(self):
        node = self.getStartNode()
        self.homeNode = node.neighbors[LEFT]
        self.node = node.neighbors[LEFT]

    def setScatterGoal(self):
        self.goal = Vector2D(WIDTH*NCOLS, HEIGHT*NROWS)

    def setChaseGoal(self, pacman, blinky=None):
        vec1 = pacman.position + pacman.direction * WIDTH * 2
        vec2 = (vec1 - blinky.position) * 2
        self.goal = blinky.position + vec2


class Clyde(Ghost):
    def __init__(self, nodes, level, spritesheet):
        Ghost.__init__(self, nodes, level, spritesheet)
        self.name = "clyde"
        self.color = ORANGE
        self.startDirection = DOWN
        self.imageRow = 5
        self.imageCol = 0
        self.setStartPosition()
        self.setGuideStack()
        self.leftHome = False
        self.exitHome = False
        #self.image = spritesheet.getImage(0, 5, 32, 32)

    def setGuideStack(self):
        self.guideStack = Stack()
        self.guideStack.push(LEFT)
        self.guideStack.push(UP)
        self.guideStack.push(LEFT)

    def setHomeNode(self):
        node = self.getStartNode()
        self.homeNode = node.neighbors[RIGHT]
        self.node = node.neighbors[RIGHT]

    def setScatterGoal(self):
        self.goal = Vector2D(0, HEIGHT*NROWS)

    def setChaseGoal(self, pacman, blinky=None):
        d = pacman.position - self.position
        ds = d.magnitudeSquared()
        if ds <= (WIDTH * 8)**2:
            self.setScatterGoal()
        else:
            self.goal = pacman.position


class GhostGroup(object):
    def __init__(self, nodes, level, spritesheet):
        self.nodes = nodes
        self.level = level
        self.ghosts = []
        self.ghosts.append(Blinky(nodes, level, spritesheet))
        self.ghosts.append(Pinky(nodes, level, spritesheet))
        self.ghosts.append(Inky(nodes, level, spritesheet))
        self.ghosts.append(Clyde(nodes, level, spritesheet))

    def __iter__(self):
        return iter(self.ghosts)

    def update(self, dt, pacman):
        blinky = self.getGhost("blinky")
        for ghost in self:
            ghost.update(dt, pacman, blinky)

    def setFreightMode(self):
        for ghost in self:
            ghost.setFreightMode()

    def anyInFreight(self):
        for ghost in self:
            if ghost.mode.name == "FREIGHT":
                return True
        return False

    def anyInSpawn(self):
        for ghost in self:
            if ghost.mode.name == "SPAWN":
                return True
        return False

    def anyInFreightOrSpawn(self):
        for ghost in self:
            if ghost.mode.name == "FREIGHT" or ghost.mode.name == "SPAWN":
                return True
        return False

    def getGhost(self, name):
        for ghost in self:
            if ghost.name == name:
                return ghost
        return None

    def release(self, name):
        ghost = self.getGhost(name)
        if ghost is not None:
            ghost.exitHome = True

    def noDraw(self):
        for ghost in self:
            ghost.draw = False

    def render(self,screen):
        for ghost in self:
            ghost.render(screen)
