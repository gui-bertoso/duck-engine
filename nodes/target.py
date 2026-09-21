import sys

import pygame

from nodes.node import Node
from settings import NONE_ICON_PATH


class Target(Node):
    def __init__(self):
        Node.__init__(self)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 0.0
        self.icon = pygame.image.load(NONE_ICON_PATH)
    def draw(self):
        pygame.draw.rect(self.window, (255, 0, 0), (self.position.x, self.position.y, 30, 30))
    def update(self):
        pass