import pygame

from enums import ButtonState
from nodes import *


class Button(Node):
    def __init__(self):
        super().__init__()

        self.base_color = pygame.Color(200, 0, 0)
        self.hover_color = pygame.Color(200, 100, 100)
        self.pressed_color = pygame.Color(70, 0, 0)
        self.disabled_color = pygame.Color(70, 50, 50)

        self.text_base_color = pygame.Color(255, 255, 255)
        self.text_hover_color = pygame.Color(100, 255, 100)
        self.text_pressed_color = pygame.Color(100, 255, 100)
        self.text_disabled_color = pygame.Color(100, 255, 100)

        self.font_size = 20
        self.l_font_size = 0

        self.font = pygame.font.SysFont("Arial", self.font_size)

        self.size = pygame.math.Vector2(32, 32)
        self.l_size = pygame.math.Vector2(0, 0)

        self.l_pos = pygame.math.Vector2(0, 0)

        self.action = None
        self.action_parameter = None

        self.state = ButtonState.Standard

        self.disabled = False

        self.click_event = None

        self.text = "ButtonName"

        self.locked = False

        self.l_text = ""

        self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)

    def render(self):
        super().render()

        color = self.base_color
        match self.state:
            case ButtonState.Standard:
                color = self.base_color
            case ButtonState.Disabled:
                color = self.disabled_color
            case ButtonState.Clicked:
                color = self.pressed_color
            case ButtonState.Hovered:
                color = self.hover_color


        pygame.draw.rect(self.window, color, self.rect)
        text = self.font.render(self.text, True, self.text_base_color)
        rect_pos = self.rect.center
        self.window.blit(text, (rect_pos[0]-text.get_width()/2, rect_pos[1]-text.get_height()/2))

    def update(self):
        super().update()


        if self.disabled:
            self.state = ButtonState.Disabled

        if self.l_size != self.size or self.position != self.l_pos or self.l_text != self.text or self.font_size != self.l_font_size:
            self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
            self.font = pygame.font.SysFont("Arial", self.font_size)
            self.l_size = self.size
            self.l_pos = self.position
            self.l_text = self.text

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.state = ButtonState.Hovered
            if self.click_event is not None:
                if self.click_event.is_set():
                    self.state = ButtonState.Clicked
                    if self.action is not None:
                        if self.action_parameter is not None:
                            self.action(self.action_parameter)
                        else:
                            self.action()
        else:
            self.state = ButtonState.Standard


        if self.locked:
            self.state = ButtonState.Clicked