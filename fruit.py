import pygame
from entities import MazeMouse
from constants import *

class CollectedFruit(MazeMouse):
    def __init__(self, nodes, level, displayedLevel, spritesheet):
        MazeMouse.__init__(self, nodes, level, spritesheet)
        self.name = "fruit"
        #self.sheet = sheet
        self.width, self.height = 32, 32
        self.color = (0, 200, 0)
        self.chooser(displayedLevel)
        self.setStartPosition()
        self.value = 100

    def setStartPosition(self):
        pos = MAZEDATA[self.level]["fruit"]
        self.node = self.nodes.getNode(*pos, nodeList=self.nodes.nodeList)
        self.target = self.node.neighbors[LEFT]
        self.setPosition()
        halfway = (self.node.position.x - self.target.position.x) / 2
        self.position.x -= halfway

    def chooser(self, level):
        level %= 6
        if level == 0:
            self.name = "cherry"
            self.color = RED
            self.value = 100
            self.image = self.spritesheet.getImage(8, 2, self.width, self.height)

        elif level == 1:
            self.name = "banana"
            self.color = YELLOW
            self.value = 200
            self.image = self.spritesheet.getImage(9, 2, self.width, self.height)

        elif level == 2:
            self.name = "apple"
            self.color = MAROON
            self.value = 500
            self.image = self.spritesheet.getImage(10, 2, self.width, self.height)

        elif level == 3:
            self.name = "strawberry"
            self.color = MAROON
            self.value = 700
            self.image = self.spritesheet.getImage(8, 3, self.width, self.height)

        elif level == 4:
            self.name = "orange"
            self.color = ORANGE
            self.value = 1000
            self.image = self.spritesheet.getImage(9, 3, self.width, self.height)

        elif level == 5:
            self.name = "watermelon"
            self.color = GREEN
            self.value = 1500
            self.image = self.spritesheet.getImage(10, 3, self.width, self.height)


class DisplayedFruit(object):
    def __init__(self, fruit):
        self.name = fruit.name
        self.color = fruit.color
        self.radius = fruit.radius
        self.image = fruit.image
        self.width = fruit.width

    def setPosition(self, index):
        x = WIDTH*NCOLS - (5 + self.width) * (index + 1)
        y = HEIGHT*(NROWS - 2)
        #x = WIDTH*NCOLS - (5 + self.radius + (2*self.radius + 5) * index)
        #y = HEIGHT*(NROWS - 1)
        self.position = Vector2D(x, y)

    def render(self, screen):
        #x, y = self.position.toTuple()
        x = int(self.position.x)
        y = int(self.position.y)
        if self.image is not None:
            screen.blit(self.image, (x, y))
        else:
            pygame.draw.circle(screen, self.color, (x, y), self.radius)
