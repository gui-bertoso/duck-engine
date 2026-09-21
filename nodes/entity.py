import sys

import pygame

from nodes.node import Node
from settings import NONE_ICON_PATH


class Entity(Node):
    def __init__(self):
        Node.__init__(self)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 2
        self.icon = pygame.image.load(NONE_ICON_PATH)
    def draw(self):
        pass
    def update(self):
        pass