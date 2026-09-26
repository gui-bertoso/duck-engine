import random
import pygame
from node.serializer import serialize_node

from settings import EMPTY_NODE_ICON_PATH


class EmptyNode:
    def __init__(self):
        self.id = random.randint(0, 99999999999999)
        self.name = ""
        self.icon = pygame.image.load(EMPTY_NODE_ICON_PATH)


