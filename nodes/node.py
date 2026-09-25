from nodes.empty_node import EmptyNode
import pygame

from settings import NODE_ICON_PATH


class Node(EmptyNode):
    def __init__(self):
        EmptyNode.__init__(self)
        self.window = None
        self.children = []
        self.position = pygame.math.Vector2(0, 0)
        self.icon = pygame.image.load(NODE_ICON_PATH)
    def draw(self):
        for child in self.children:
            child.draw()
    def update(self):
        for child in self.children:
            child.update()
    def icon_draw(self):
        for child in self.children:
            child.icon_draw()
        if self.window is not None:
            self.window.blit(self.icon, self.position)