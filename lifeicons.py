import pygame
from constants import *

class Lives(object):
    def __init__(self, spritesheet):
        self.width, self.height = 32, 32
        self.image = spritesheet.getImage(0, 0, self.width, self.height)
        self.gap = 10

    def render(self, screen, num):
        for i in range(num):
            x = self.gap + (self.width + self.gap) * i
            y = HEIGHT * NROWS - self.height
            screen.blit(self.image, (x, y))
