from nodes.root import RootNode


class Scene:
    def __init__(self):
        self.window = None
        self.nodes = []
        self.root_node = RootNode()
        self.nodes.append(self.root_node)
    def add_node(self, node):
        self.root_node.children.append(node)
