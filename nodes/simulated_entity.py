import random

import pygame

from nodes.controller import Controller
from nodes.entity import Entity
from nodes.sprite import Sprite

from settings import SIMULATED_ENTITY_ICON_PATH


class SimulatedEntity(Entity):
    def __init__(self):
        Entity.__init__(self)
        self.sprite = Sprite()
        self.target_reference = None
        self.controller = Controller()
        self.controller.parent = self
        self.icon = pygame.image.load(SIMULATED_ENTITY_ICON_PATH)
    def update(self):
        self.controller.update()
    def draw(self):
        pygame.draw.circle(self.window, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), self.position, 30)
