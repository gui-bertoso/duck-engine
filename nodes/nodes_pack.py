from enums import LogType


class NodePack:
    def __init__(self):
        self.nodes = []

        self.name = "NodePack"

    def render(self):
        for i in self.nodes:
            i.render()

    def update(self):
        for i in self.nodes:
            i.update()

    def add_node(self, node):
        self.nodes.append(node)