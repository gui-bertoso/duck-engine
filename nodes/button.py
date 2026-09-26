import pygame

from enums import ButtonState
from nodes import Node


class Button(Node):
    def __init__(self):
        super().__init__()

        self.base_color = pygame.Color(0, 255, 0)
        self.hover_color = pygame.Color(100, 255, 100)
        self.pressed_color = pygame.Color(0, 100, 0)
        self.disabled_color = pygame.Color(0, 100, 0)

        self.size = pygame.math.Vector2(32, 32)
        self.l_size = pygame.math.Vector2(0, 0)

        self.l_pos = pygame.math.Vector2(0, 0)

        self.action = None

        self.state = ButtonState

        self.disabled = False

        self.click_event = None

        self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)

    def render(self):
        match self.state:
            case ButtonState.Standard:
                pygame.draw.rect(self.window, self.base_color, self.rect)
            case ButtonState.Disabled:
                pygame.draw.rect(self.window, self.disabled_color, self.rect)
            case ButtonState.Clicked:
                pygame.draw.rect(self.window, self.pressed_color, self.rect)
            case ButtonState.Hovered:
                pygame.draw.rect(self.window, self.hover_color, self.rect)

    def update(self):
        if self.disabled:
            self.state = ButtonState.Disabled
            return

        if self.l_size != self.size or self.position != self.l_pos:
            self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
            self.l_size = self.size
            self.l_pos = self.position

        if self.rect.colliderect(pygame.mouse.get_pos()):
            self.state = ButtonState.Hovered
            if self.click_event == None:
                return
            if self.click_event.is_set():
                self.state = ButtonState.Clicked

