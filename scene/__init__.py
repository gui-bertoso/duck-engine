import random

from nodes import RootNode
from settings import ENGINE_VERSION


class Scene:
    def __init__(self):
        self.window = None
        self.nodes = []
        self.root_node = RootNode()
        self.nodes.append(self.root_node)

        self.scene_name = "Scene"
        self.scene_path = "scenes/"
        self.scene_id = random.randint(1, 999999999)
        self.scene_version = ENGINE_VERSION

    def add_node(self, node):
        self.root_node.children.append(node)
