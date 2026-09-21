import sys

import pygame

from nodes.empty_node import EmptyNode
from settings import NONE_ICON_PATH


class Sprite(EmptyNode):
    def __init__(self):
        EmptyNode.__init__(self)
        self.texture = None
        self.icon = pygame.image.load(NONE_ICON_PATH)
    def update(self):
        pass
    def draw(self):
        pass

    def set_texture(self, path):
        self.texture = pygame.image.load(path)
    def set_alpha(self, alpha):
        self.texture.set_alpha(alpha)