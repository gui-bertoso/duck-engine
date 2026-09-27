import sys

import pygame

from nodes.node import Node
from settings import GRAPH_ICON_PATH


class GraphNode(Node):
    def __init__(self):
        super().__init__()
        self.max_points = 100
        self.values = []
        self.size = pygame.math.Vector2(100, 100)

        self.line_color = (255, 255, 255)
        self.ram_usage_kb = sys.getsizeof(self) / 1024
        self.icon = pygame.image.load(GRAPH_ICON_PATH)

    def add_value(self, value):
        self.values.append(value)

        if len(self.values) > self.max_points:
            self.values.pop(0)

    def render(self):
        super().render()
        graph_x = self.position.x
        graph_y = self.position.y
        graph_w = self.size.x
        graph_h = self.size.y

        pygame.draw.rect(self.window, (255, 255, 255), (self.position.x, self.position.y, graph_w, graph_h), 1)

        if len(self.values) < 2:
            return

        max_value = max(self.values)
        min_value = min(self.values)

        points = []

        for i, value in enumerate(self.values):
            x = graph_x + (i / (self.max_points - 1)) * graph_w

            normalized = ((value - min_value) / max(0.001, max_value - min_value))

            y = graph_y + graph_h - normalized * graph_h

            points.append((x, y))

        pygame.draw.lines(self.window, self.line_color, False, points, 2)