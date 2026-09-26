from nodes.empty_node import EmptyNode
import pygame

from settings import NODE_ICON_PATH

class Node(EmptyNode):
    def __init__(self):
        super().__init__()
        self.window = None
        self.children = []
        self.position = pygame.math.Vector2(0, 0)
        self.icon = pygame.image.load(NODE_ICON_PATH)

    def render(self):
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

    def serialize_node(self, depth=0)->str:
        indent = "    " * depth

        result = (
            f"{indent}node -> " + "{\n"
            f"{indent}    name -> {self.name}\n"
            f"{indent}    id -> {self.id}\n"
            f"{indent}    node -> {self.__class__.__name__}\n"
        )

        for child in self.children:
            result += child.serialize_node(depth + 1)

        result += f"{indent}}}\n"
        return result