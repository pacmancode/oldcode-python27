import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from ghosts import GhostGroup
from pellets import PelletGroup
from fruit import CollectedFruit, DisplayedFruit
from lifeicons import Lives
from spritesheet import SpriteSheet
from maze import Maze
from text import TextGroup

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.level = 0
        self.setBackGround()
        self.clock = pygame.time.Clock()
        self.score = 0
        self.ghostScore = 200
        self.lives = 5
        self.idleTimer = 0
        self.displayedLevel = 0
        self.maxLevels = 2
        self.displayedFruits = []
        self.sheet = SpriteSheet()
        self.lifeIcons = Lives(self.sheet)
        self.maze = Maze(self.level, self.sheet)
        self.maze.fillMaze(self.background)
        self.allText = TextGroup()
        self.allText.add("hi_score_label", "HI SCORE", align="left")
        self.allText.add("score_label", "SCORE", align="center")
        self.allText.add("level_label", "LEVEL", align="right")
        self.allText.add("score", self.score, y=HEIGHT, align = "center")
        self.allText.add("level", self.displayedLevel, y=2*HEIGHT, align = "right")
        self.levelFlashTime = 0.3
        self.levelFlashTimer = 0
        self.drawBackgroundFlash = False
        self.flashLevel = False
        self.fruitScoreTimer = 0
        self.fruitEaten = False

    def setBackGround(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)
        self.backgroundFlash = pygame.surface.Surface(SCREENSIZE).convert()
        self.backgroundFlash.fill(BLACK)

    def commonSetup(self):
        self.pacman = Pacman(self.nodes, self.level, self.sheet)
        self.ghosts = GhostGroup(self.nodes, self.level, self.sheet)
        self.paused = True
        self.fruit = None
        self.fruitTimer = 0
        self.pauseTimer = 0
        self.pauseTime = 5
        self.playerPaused = False
        self.startDelay = False
        self.restartDelay = False
        self.scoreAccumulator = 0
        self.maxLives = 5
        self.allText.add("start_label", "BEGIN", y=20*HEIGHT, align="center", color=YELLOW)
        self.flashLevel = False
        self.drawBackgroundFlash = False
        self.levelFlashTimer = 0
        self.fruitScoreTimer = 0

    def startGame(self):
        self.setBackGround()
        self.maze = Maze(self.level, self.sheet)
        self.maze.fillMaze(self.background)
        self.mazeFlash = Maze(self.level, self.sheet, startcol=11)
        self.mazeFlash.fillMaze(self.backgroundFlash)
        
        self.nodes = NodeGroup(self.level)
        self.pellets = PelletGroup(self.level)
        self.commonSetup()

    def restartLevel(self):
        self.commonSetup()

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        if not self.paused:
            self.pacman.update(dt)
            self.ghosts.update(dt, self.pacman)
            self.checkPelletEvents(dt)
            self.checkGhostEvents(dt)
            self.checkFruitEvents(dt)
            self.applyScore()
        else:
            if not self.playerPaused:
                if not self.pacman.alive:
                    self.pacman.update(dt)
                    if self.pacman.deathSequenceFinished:
                        if self.lives > 0:
                            self.restartLevel()
                        else:
                            self.allText.add("game_over_label", 
                                             "GAME OVER", y=20*HEIGHT, 
                                             align="center", color=RED)

                else:
                    self.pauseTimer += dt
                    if self.pauseTimer >= self.pauseTime:
                        self.paused = False
                        self.allText.remove("ghost_score")
                        self.allText.remove("start_label")
                        self.pacman.draw = True
                        for ghost in self.ghosts:
                            ghost.draw = True
                        if self.startDelay == True:
                            self.startGame()
                        if self.restartDelay == True:
                            self.restartLevel()

        if self.flashLevel:
            self.levelFlashTimer += dt
            if self.levelFlashTimer >= self.levelFlashTime:
                self.levelFlashTimer = 0
                self.drawBackgroundFlash = not self.drawBackgroundFlash
                
        if self.fruitEaten:
            self.fruitScoreTimer += dt
            if self.fruitScoreTimer >= self.fruitScoreTime:
                self.allText.remove("fruit_score")
                self.fruitScoreTimer = 0
                self.fruitEaten = False

        self.checkEvents()
        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.allText.remove("start_label")
                    self.allText.remove("fruit_score")
                    if self.paused:
                        self.playerPaused = False
                        self.allText.remove("paused_label")
                    else:
                        self.playerPaused = True
                        self.allText.add("paused_label", "PAUSED", y=20*HEIGHT, 
                                         align="center", color=GREEN)
                    self.paused = not self.paused

    def checkPelletEvents(self, dt):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            if (self.pellets.numEaten == 70 or self.pellets.numEaten == 140):
                self.fruit = CollectedFruit(self.nodes, self.level, self.displayedLevel, self.sheet)
            self.idleTimer = 0
            self.scoreAccumulator += pellet.value
            self.pellets.pelletList.remove(pellet)
            if pellet.name == "powerpellet":
                self.pellets.powerPellets.remove(pellet)
                self.ghosts.setFreightMode()
                self.ghostScore = 200

            if (self.ghosts.anyInFreightOrSpawn()):
                self.pacman.boostSpeed()
            else:
                self.pacman.reduceSpeed()

            if self.pellets.isEmpty():
                self.paused = True
                self.pauseTime = 3
                self.pauseTimer = 0
                self.startDelay = True
                self.flashLevel = True
                self.increaseLevel()

        else:
            self.idleTimer += dt
            if (self.ghosts.anyInFreightOrSpawn()):
                self.pacman.boostSpeed()
            else:
                if self.idleTimer >= 0.5:
                    self.pacman.normalSpeed()

        for pellet in self.pellets.powerPellets:
            pellet.update(dt)

    def checkGhostEvents(self, dt):
        ghost = self.pacman.eatGhost(self.ghosts)
        if ghost is not None:
            if ghost.mode.name == "FREIGHT":
                self.allText.add("ghost_score", self.ghostScore, 
                                 x=ghost.position.x, y=ghost.position.y, size=0.5)

                ghost.setRespawnMode()
                self.scoreAccumulator += self.ghostScore
                self.ghostScore *= 2
                self.paused = True
                self.pauseTime = 0.5
                self.pauseTimer = 0
                self.pacman.draw = False
                ghost.draw = False
            elif ghost.mode.name != "SPAWN":
                self.paused = True
                #self.pauseTime = 1
                self.pauseTimer = 0
                self.restartDelay = True
                self.lives -= 1
                if self.lives == 0:
                    self.lives = 5
                    self.startDelay = True
                self.pacman.alive = False
                self.ghosts.noDraw()
                #ghost.draw = False
                self.pacman.animate.setAnimation("death", 0)

        if self.pellets.numEaten >= 30 or self.idleTimer >= 10:
            self.ghosts.release("inky")
        if self.pellets.numEaten >= 60 or self.idleTimer >= 10:
            self.ghosts.release("clyde")

    def checkFruitEvents(self, dt):
        if self.fruit is not None:
            if self.pacman.eatFruit(self.fruit):
                self.allText.add("fruit_score", self.fruit.value, 
                                 x=self.fruit.position.x, y=self.fruit.position.y, size=0.5)
                self.scoreAccumulator += self.fruit.value
                self.addDisplayedFruit()
                self.fruitTimer = 0
                self.fruit = None
                self.fruitScoreTime = 1
                self.fruitScoreTimer = 0
                self.fruitEaten = True
            else:
                self.fruitTimer += dt
                if self.fruitTimer >= 10:
                    self.fruitTimer = 0
                    self.fruit = None

    def applyScore(self):
        if self.scoreAccumulator > 0:
            newScore = self.score + self.scoreAccumulator
            if ((newScore % 10000 - self.score % 10000) < 0 or newScore - self.score >= 10000):
                if self.lives < self.maxLives:
                    self.lives += 1
            self.score += self.scoreAccumulator
            self.scoreAccumulator = 0
            self.allText.remove("score")
            self.score = newScore
            self.allText.add("score", self.score, y=HEIGHT, align="center")


    def addDisplayedFruit(self):
        fruitNames = [n.name for n in self.displayedFruits]
        if self.fruit.name not in fruitNames:
            fruit = DisplayedFruit(self.fruit)
            fruit.setPosition(len(self.displayedFruits))
            self.displayedFruits.append(fruit)

    def increaseLevel(self):
        self.level += 1
        self.displayedLevel += 1
        self.level %= self.maxLevels

    def render(self):
            
        if self.drawBackgroundFlash:
            self.screen.blit(self.backgroundFlash, (0, 0))
        else:
            self.screen.blit(self.background, (0, 0))
            
        #self.nodes.render(self.screen)
        self.pellets.render(self.screen)


        for fruit in self.displayedFruits:
            fruit.render(self.screen)

        if not self.playerPaused:
            if self.fruit is not None:
                self.fruit.render(self.screen)
            self.ghosts.render(self.screen)
            self.pacman.render(self.screen)

        self.lifeIcons.render(self.screen, self.lives-1)
        self.allText.render(self.screen)

        pygame.display.update()

        
if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()
