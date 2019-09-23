class Animation(object):
    def __init__(self, name):
        self.name = name
        self.frames = []
        self.col = 0
        self.forward = True
        self.speed = 0
        self.dt = 0
        self.finished = False

    def addFrame(self, frame):
        self.frames.append(frame)

    def getFrame(self):
        return self.frames[self.col]

    def nextFrame(self, dt):
        self.dt += dt
        if self.dt >= 1.0 / self.speed:
            if self.forward:
                self.col += 1
            else:
                self.col -= 1
            self.dt = 0

    def loop(self, dt):
        self.nextFrame(dt)
        if self.forward:
            if self.col == len(self.frames):
                self.col = 0
        else:
            if self.col == -1:
                self.col = len(self.frames) - 1


    def onePass(self, dt):
        self.nextFrame(dt)
        if self.forward:
            if self.col == len(self.frames):
                self.col = len(self.frames) - 1
                self.finished = True
        else:
            if self.col == -1:
                self.col = 0
                self.finished = True

    def ping(self, dt):
        self.nextFrame(dt)
        if self.col == len(self.frames):
            self.forward = False
            self.col -= 2
        elif self.col == -1:
            self.forward = True
            self.col = 1


class AnimationGroup(object):
    def __init__(self):
        self.animations = []
        self.animation = None
        self.col = 0

    def add(self, animation):
        self.animations.append(animation)

    def setAnimation(self, name, col):
        self.animation = self.getAnimation(name)
        self.animation.col = col

    def getAnimation(self, name):
        for anim in self.animations:
            if anim.name == name:
                return anim
        return None

    def getImage(self, frame):
        return self.animation.frames[frame]

    def loop(self, dt):
        self.animation.loop(dt)
        return self.animation.getFrame()

    def onePass(self, dt):
        self.animation.onePass(dt)
        return self.animation.getFrame()

    def ping(self, dt):
        self.animation.ping(dt)
        return self.animation.getFrame()
