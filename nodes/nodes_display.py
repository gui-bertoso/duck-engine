import pygame

from enums import LogType
from nodes.nodes_display_node import NodesDisplayNode

from main import INSPECTOR_LEFT_PANEL_WIDTH


class NodesDisplay:
    def __init__(self):
        global INSPECTOR_LEFT_PANEL_WIDTH

        self.nodes = []
        self.scroll_y = 0
        self.window = None
        self.rect = None
        self.click_event = None

        self.color = (30, 30, 30)

        self.position = pygame.math.Vector2(0, 0)
        self.size = pygame.math.Vector2(120, 120)
        self.node_size = pygame.math.Vector2((self.size.x / 5), (self.size.y / 5))

    def update_rect_data(self):
        self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)

    def render(self):
        if self.click_event is not None:
            self.click_event.clear()
        for ev in pygame.event.get():
            if ev.type == pygame.MOUSEBUTTONDOWN:

                if self.click_event is not None:
                    self.click_event.set()
        pygame.draw.rect(self.window, self.color, self.rect)
        for i in self.nodes:
            i.click_event = self.click_event
            i.render()

    def add_node(self, _node: NodesDisplayNode):
        i = len(self.nodes)
        column = i % 5
        row = i // 5

        x = self.rect.left + (column * self.node_size.x) + 2.5
        y = self.rect.top + (row * self.node_size.y) + 2.5

        _node.size = self.node_size

        _node.position.x = x
        _node.position.y = y

        _node.window = self.window

        self.nodes.append(_node)
