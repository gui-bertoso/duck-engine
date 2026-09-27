import pygame

from nodes import *

class Rect(Node):
    def __init__(self):
        super().__init__()
        self.resizable = True
        self.size = pygame.math.Vector2(100, 100)
        self.color = pygame.Color(255, 0, 0)
        self.border_color = pygame.Color(0, 0, 0)
        self.border_width = 3

        self.l_size = pygame.math.Vector2(0, 0)
        self.l_pos = pygame.math.Vector2(0, 0)
        self.l_border_width = 0

        self.rect = pygame.rect.Rect(self.position.x, self.position.y, self.size.x, self.size.y)

    def render(self):
        if self.l_size != self.size or self.l_pos != self.position:
            self.l_size = self.size
            self.l_pos = self.position

            self.rect = pygame.rect.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
        pygame.draw.rect(self.window, self.color, self.rect)
        super().render()


    def update(self):
        if self.resizable:
            pass