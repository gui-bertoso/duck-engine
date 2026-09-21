import sys
import pygame
from nodes.node import Node


class LoadingBar(Node):
    def __init__(self):
        Node.__init__(self)
        self.size = pygame.math.Vector2(10, 10)
        self.max_value = 100
        self.value = 50

        self.base_color = (50, 50, 50)
        self.fill_color = (150, 150, 150)
        self.ram_usage_kb = sys.getsizeof(self) / 1024

    def draw(self):
        percentage = self.value / self.max_value
        fill_size = self.size.x * percentage
        pygame.draw.rect(self.window, self.base_color, (self.position.x, self.position.y, self.size.x, self.size.y))
        pygame.draw.rect(self.window, self.fill_color, (self.position.x, self.position.y, fill_size, self.size.y))

    def update(self):
        pass