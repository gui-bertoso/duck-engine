import pygame

from nodes import Node


class Label(Node):
    def __init__(self):
        super().__init__()

        self.text = ""
        self.l_text = "LabelText"

        self.font_size = 20
        self.l_font_size = 0

        self.color = (255, 255, 255)

        self.font = pygame.font.SysFont("Arial", self.font_size)
        self.text_rendered = self.font.render(self.text, True, self.color)

    def update(self):
        pass

    def render(self):
        if self.l_text != self.text or self.font_size != self.l_font_size:
            self.l_text = self.text
            self.l_font_size = self.font_size

            self.font = pygame.font.SysFont("Arial", self.font_size)

            self.text_rendered = self.font.render(self.text, True, self.color)

        self.window.blit(self.text_rendered, self.position)
