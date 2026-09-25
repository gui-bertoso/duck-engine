import pygame.math

from nodes import *

class Rect(Node):
    def __init__(self):
        super().__init__()
        self.resizable = True
        self.size = pygame.math.Vector2(100, 100)
        self.color = pygame.Color(255, 0, 0)
        self.border_color = pygame.Color(0, 0, 0)
        self.border_width = 3

    def draw(self):
        pygame.draw.rect(self.window, self.color, (self.size.x-self.border_width*2, self.size.y-self.border_width*2, self.position.x, self.position.y))
        pygame.draw.rect(self.window, self.color, (self.size.x, self.size.y, self.size.x, self.size.y), self.border_width)

    def update(self):
        if self.resizable:
            pass