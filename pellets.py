import pygame
from vectors import Vector2D
from constants import *
from numpy import loadtxt

class Pellet(object):
    def __init__(self, x, y):
        self.name = "pellet"
        self.position = Vector2D(x, y)
        self.color = YELLOW
        self.radius = 2
        self.value = 10
        self.draw = True

    def render(self, screen):
        if self.draw:
            px = int(self.position.x + 8)
            py = int(self.position.y + 8)
            pygame.draw.circle(screen, self.color, (px, py), self.radius)


class PowerPellet(Pellet):
    def __init__(self, x, y):
        Pellet.__init__(self, x, y)
        self.name = "powerpellet"
        self.radius = 8
        self.value = 50
        self.flashTime = 0.5
        self.dt = 0

    def update(self, dt):
        self.dt += dt
        if self.dt >= self.flashTime:
            self.dt = 0
            self.draw = not self.draw


class PelletGroup(object):
    def __init__(self, level):
        self.pelletList = []
        self.powerPellets = []
        self.createPelletList(level)
        self.numEaten = 0

    def isEmpty(self):
        if len(self.pelletList) == 0:
            return True
        return False

    def createPelletList(self, level):
        grid = loadtxt(MAZEDATA[level]["file"], dtype=str)
        rows, cols = grid.shape
        for row in range(rows):
            for col in range(cols):
                if (grid[row][col] == "p" or grid[row][col] == "n"):
                    self.pelletList.append(Pellet(col*WIDTH, row*HEIGHT))
                if (grid[row][col] == "P" or grid[row][col] =="N"):
                    pellet = PowerPellet(col*WIDTH, row*HEIGHT)
                    self.pelletList.append(pellet)
                    self.powerPellets.append(pellet)

    def render(self, screen):
        for pellet in self.pelletList:
            pellet.render(screen)
