import pygame

from nodes.node import Node
from settings import ROOT_ICON_PATH

class RootNode(Node):
    def __init__(self,):
        Node.__init__(self)
        self.icon = pygame.image.load(ROOT_ICON_PATH)
        self.children = []