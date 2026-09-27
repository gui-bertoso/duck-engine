import pygame

from .button import Button
from .nodes_pack import NodePack
from .node import Node


class TabsPanel(Node):
    def __init__(self):
        super().__init__()

        self.window = None

        self.tabs = []

        self.tabs_count = 1

        self.tab_height = 32

        self.tab_size = pygame.math.Vector2(32, self.tab_height)

        self.size = pygame.math.Vector2(320, 320)

        self.background_color = pygame.Color(75, 75, 75)

        self.tab_button_base_color = pygame.Color(100, 100, 100)
        self.tab_button_hover_color = pygame.Color(150, 150, 150)
        self.tab_button_selected_color = pygame.Color(30, 30, 30)

        self.tab_button_font_size = 12

        self.current_tab = None

        self.click_event = None



    def add_tab(self, tab: NodePack):
        if len(self.tabs) + 1 < 2:
            self.tabs_count = 1
        else:
            self.tabs_count = len(self.tabs) + 1

        self.tab_size = pygame.math.Vector2(self.size.x/self.tabs_count, self.tab_height)

        new_tab_button = Button()
        new_tab_button.text = tab.name
        new_tab_button.window = self.window
        new_tab_button.action_parameter = new_tab_button
        new_tab_button.action = self.tab_selected
        new_tab_button.click_event = self.click_event
        new_tab_button.base_color = self.tab_button_base_color
        new_tab_button.hover_color = self.tab_button_hover_color
        new_tab_button.pressed_color = self.tab_button_selected_color
        new_tab_button.font_size = self.tab_button_font_size

        tab_data = {
            "node_pack": tab,
            "button": new_tab_button
        }

        self.tabs.append(tab_data)

        for i in range(len(self.tabs)):
            tab = self.tabs[i]
            tab_button = tab["button"]

            tab_button.size = self.tab_size
            tab_button.position = pygame.math.Vector2(self.position.x+i*self.tab_size.x, self.position.y)

    def tab_selected(self, tab: Button):
        if self.current_tab is not None:
            self.current_tab["button"].locked = False

        tab.locked = True

        for tab_data in self.tabs:
            if tab_data["button"] == tab:
                self.current_tab = tab_data


    def render(self):
        pygame.draw.rect(self.window, self.background_color, (self.position.x, self.position.y, self.size.x, self.size.y))

        super().render()

        for tab in self.tabs:
            tab["button"].render()

        if self.current_tab is not None:
            self.current_tab["node_pack"].render()

    def update(self):
        super().update()

        for tab in self.tabs:
            tab["button"].update()

        if self.current_tab is not None:
            self.current_tab["node_pack"].render()