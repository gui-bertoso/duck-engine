import pygame

from enums import LogType
from logger import print_log
from nodes.nodes_display_node import NodesDisplayNode


class NodesDisplay:
    def __init__(self, rect):
        global INSPECTOR_LEFT_PANEL_WIDTH

        self.nodes = []
        self.scroll_y = 0
        self.window = None
        self.rect = rect
        self.click_event = None

        self.color = (30, 30, 30)

        self.position = pygame.math.Vector2(0, 0)
        self.size = pygame.math.Vector2(INSPECTOR_LEFT_PANEL_WIDTH - 20, INSPECTOR_LEFT_PANEL_WIDTH - 20)
        self.node_size = pygame.math.Vector2((self.size.x / 3) - 10, (self.size.y / 3) - 10)

    def render(self):
        self.click_event.clear()
        for ev in pygame.event.get():
            if ev.type == pygame.MOUSEBUTTONDOWN:
                self.click_event.set()
        pygame.draw.rect(self.window, self.color, self.rect)
        for i in self.nodes:
            i.click_event = self.click_event
            i.render()

    def add_node(self, _node: NodesDisplayNode):
        i = len(self.nodes)
        column = i % 3
        row = i // 3

        x = self.rect.left + (column * self.node_size.x) + 2.5
        y = self.rect.top + (row * self.node_size.y) + 2.5

        _node.position.x = x
        _node.position.y = y

        _node.window = self.window

        self.nodes.append(_node)

        print_log("new node added to nodes display", LogType.Info, 1)
        print_log(f"nodes list : {self.nodes}", LogType.Detail, 2)
