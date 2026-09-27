import sys
import pygame
from nodes.node import Node
from settings import LOADING_ICON_PATH


class LoadingBar(Node):
    def __init__(self):
        super().__init__()
        self.size = pygame.math.Vector2(10, 10)
        self.max_value = 100
        self.value = 50

        self.base_color = (50, 50, 50)
        self.fill_color = (150, 150, 150)
        self.icon = pygame.image.load(LOADING_ICON_PATH)

    def render(self):
        super().render()
        percentage = self.value / self.max_value
        fill_size = self.size.x * percentage
        pygame.draw.rect(self.window, self.base_color, (self.position.x, self.position.y, self.size.x, self.size.y))
        pygame.draw.rect(self.window, self.fill_color, (self.position.x, self.position.y, fill_size, self.size.y))

    def update(self):
        pass