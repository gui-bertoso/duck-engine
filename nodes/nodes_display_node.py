import pygame

from enums import LogType
from main import INSPECTOR_LEFT_PANEL_WIDTH, print_log
from settings import DEFAULT_FONT, DEFAULT_MAIN_FONT_SIZE


class NodesDisplayNode:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.icon = None
        self.node = None
        self.click_event = None
        self.position = pygame.math.Vector2(0, 0)
        self.size = pygame.math.Vector2(((INSPECTOR_LEFT_PANEL_WIDTH - 20) / 5) - 10,
                                        ((INSPECTOR_LEFT_PANEL_WIDTH - 20) / 5) - 10)
        self.base_color = (90, 90, 0)
        self.hover_color = (120, 120, 0)
        self.click_color = (60, 60, 250)
        self.rect = None
        self.parent = None
        self.font = pygame.font.SysFont(DEFAULT_FONT, DEFAULT_MAIN_FONT_SIZE)
        self.window = None
        self.is_preview_only = False

        self.image_render = None

    def render(self):
        if self.image_render is None and self.node is not None and hasattr(self.node, 'icon'):
            self.image_render = pygame.image.load(self.node.icon)
        if self.is_preview_only:
            self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
            pygame.draw.rect(self.window, self.base_color, self.rect)

            text = self.font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            if self.image_render is not None:
                self.window.blit(self.image_render, text_rect)
            else:
                self.window.blit(text, text_rect)
        else:

            self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)

            color = self.base_color

            if self.rect.collidepoint(pygame.mouse.get_pos()):

                if self.click_event is not None:
                    if self.click_event.is_set():
                        color = self.click_color

                        t_node = self.get_copy()
                        t_node.is_preview_only = True
                        self.parent.inspector_selected_node = t_node

                        print_log("node clicked", LogType.Detail, 3)
                    else:
                        color = self.hover_color

            pygame.draw.rect(self.window, color, self.rect)

            text = self.font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            if self.image_render is not None:
                self.window.blit(self.image_render, text_rect)
            else:
                self.window.blit(text, text_rect)

    def get_copy(self):
        copy = NodesDisplayNode()
        copy.name = self.name
        copy.icon = self.icon
        copy.description = self.description
        copy.node = self.node
        copy.rect = self.rect
        copy.position = self.position
        copy.window = self.window
        copy.parent = self.parent
        return copy
