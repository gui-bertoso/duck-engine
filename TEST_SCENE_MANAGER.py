

import random

import pygame
from settings import ENGINE_VERSION, SCENE_EXTENSION, SCENES_FOLDER_PATH, EMPTY_NODE_ICON_PATH, NODE_ICON_PATH, \
    ROOT_ICON_PATH


class EmptyNode:
    def __init__(self):
        self.id = random.randint(0, 99999999999999)
        self.name = ""
        self.icon = pygame.image.load(EMPTY_NODE_ICON_PATH)


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



class RootNode(Node):
    def __init__(self,):
        Node.__init__(self)
        self.icon = pygame.image.load(ROOT_ICON_PATH)
        self.children = []

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


def save_scene(scene_path):
    pass


def create_scene(scene: Scene):
    scene_name = scene.scene_name
    scene_version = scene.scene_version
    scene_id = scene.scene_id

    file_template = f"FILETYPE SCENE\n\nscene_name -> {scene_name}\nscene_version -> {scene_version}\nscene_id -> {scene_id}"
    file_template += "\n\nchilds -> {\n"
    for child in scene.nodes:
        file_template += child.serialize_node(1)

    file_template += "}"

    t_file = open(SCENES_FOLDER_PATH+scene_name+SCENE_EXTENSION, "w+")
    t_file.write(file_template)
    t_file.close()


def quicksave_scene():
    pass



if __name__ == "__main__":
    my_scene = Scene()
    my_scene.scene_name = "my_scene_name"
    my_scene.scene_version = "my_scene_version"
    my_scene.scene_id = "my_scene_id"

    create_scene(my_scene)