import sys

import pygame

from nodes.node import Node
from settings import ENTITY_ICON_PATH


class Entity(Node):
    def __init__(self):
        super().__init__()
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 2
        self.icon = pygame.image.load(ENTITY_ICON_PATH)

    def render(self):
        super().render()

    def update(self):
        pass