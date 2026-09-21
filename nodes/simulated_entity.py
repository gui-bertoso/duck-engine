import random

import pygame

from nodes.controller import Controller
from nodes.entity import Entity
from nodes.sprite import Sprite


class SimulatedEntity(Entity):
    def __init__(self, target=None, window=None, best_weights=[]):
        Entity.__init__(self, window)
        self.sprite = Sprite()
        self.target_reference = target
        self.controller = Controller(best_weights)
        self.controller.parent = self
    def update(self):
        self.controller.update()
    def draw(self):
        pygame.draw.circle(self.window, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), self.position, 30)
