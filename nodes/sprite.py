import pygame

from nodes import Node
from settings import NONE_ICON_PATH


class Sprite(Node):
    def __init__(self):
        super().__init__()
        self.texture = None
        self.icon = pygame.image.load(NONE_ICON_PATH)

    def update(self):
        pass

    def render(self):
        super().render()

    def set_texture(self, path):
        self.texture = pygame.image.load(path)

    def set_alpha(self, alpha):
        self.texture.set_alpha(alpha)