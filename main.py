import os
from unittest import case

from enums import LogType, HardwareCacheType

from logger import print_log
import logging

from scene import Scene

logging.basicConfig(level=logging.FATAL)

from nodes import *

from settings import *

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import multiprocessing
import pygame
import threading
import platform
import time
import psutil
import wmi
import subprocess
import re
import pympler.asizeof
import asyncio

DELTA_TIME = 0.0
RUNTIME_PROCESS_TIME = 0.0
RENDER_TIME = 0.0
RUNTIME_RENDER_TIME = 0.0

RUNTIME_EVENT_PROCESS_TIME = 0.0
RUNTIME_NODES_UPDATE_TIME = 0.0
RUNTIME_NODE_ICONS_DRAW_TIME = 0.0
RUNTIME_INSPECTOR_TIME = 0.0

INSPECTOR_LEFT_PANEL_WIDTH = 400

class NodesDisplay:
    def __init__(self, rect):
        global INSPECTOR_LEFT_PANEL_WIDTH

        self.nodes = []
        self.scroll_y = 0
        self.window = None
        self.rect = rect
        self.click_event = None

        self.color = (30, 30, 30)

        self.position = pygame.math.Vector2(0, 0)
        self.size = pygame.math.Vector2(INSPECTOR_LEFT_PANEL_WIDTH-20, INSPECTOR_LEFT_PANEL_WIDTH-20)
        self.node_size = pygame.math.Vector2((self.size.x/3)-10, (self.size.y/3)-10)

    def render(self):
        self.click_event.clear()
        for ev in pygame.event.get():
            if ev.type == pygame.MOUSEBUTTONDOWN:
                self.click_event.set()
        pygame.draw.rect(self.window, self.color, self.rect)
        for i in self.nodes:
            i.click_event = self.click_event
            i.render()

            
    def add_node(self, _node:NodesDisplayNode):
        i = len(self.nodes)
        column = i % 3
        row = i // 3

        x = self.rect.left + (column * self.node_size.x) + 2.5
        y = self.rect.top + (row * self.node_size.y) + 2.5

        _node.position.x = x
        _node.position.y = y

        _node.window = self.window

        self.nodes.append(_node)

        print_log("new node added to nodes display", LogType.Info, 1)
        print_log(f"nodes list : {self.nodes}", LogType.Detail, 2)

class NodesDisplayNode:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.icon = None
        self.node = None
        self.click_event = None
        self.position = pygame.math.Vector2(0, 0)
        self.size = pygame.math.Vector2(((INSPECTOR_LEFT_PANEL_WIDTH-20)/3)-10, ((INSPECTOR_LEFT_PANEL_WIDTH-20)/3)-10)
        self.base_color = (90, 90, 0)
        self.hover_color = (120, 120, 0)
        self.click_color = (60, 60, 250)
        self.rect = None
        self.parent = None
        self.font = pygame.font.SysFont(DEFAULT_FONT, DEFAULT_MAIN_FONT_SIZE)
        self.window = None
        self.is_preview_only = False

    def render(self):
        if self.is_preview_only:
            self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
            pygame.draw.rect(self.window, self.base_color, self.rect)

            text = self.font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            self.window.blit(text, text_rect)
        else:

            self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
            
            color = self.base_color

            if self.rect.collidepoint(pygame.mouse.get_pos()):
                if self.click_event.is_set():
                    color = self.click_color

                    t_node = self.get_copy()
                    t_node.is_preview_only = True
                    self.parent.inspector_selected_node = t_node

                    print_log("node clicked", LogType.Detail, 3)
                else:
                    color = self.hover_color

            pygame.draw.rect(self.window, color, self.rect)

            text = self.font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            self.window.blit(text, text_rect)

    def get_copy(self):
        copy = NodesDisplayNode()
        copy.name = self.name
        copy.icon = self.icon
        copy.description = self.description
        copy.node = self.node
        copy.rect = self.rect
        copy.position = self.position
        copy.window = self.window
        copy.parent = self.parent
        return copy





class Engine:
    def __init__(self):

        self.cpu_cores = None
        print_log(f"initializing pygame", LogType.Detail, 1)
        pygame.init()
        pygame.font.init()


        print_log(f"creating pygame window", LogType.Detail, 1)
        self.window = None
        pygame.display.set_caption("Duck Engine")
        

        print_log(f"creating clocks", LogType.Detail, 1)
        self.process_clock = pygame.time.Clock()
        self.render_clock = pygame.time.Clock()
        

        print_log(f"creating events", LogType.Detail, 1)
        self.close_event = threading.Event()
        self.click_event = threading.Event()


        print_log(f"creating main scene", LogType.Detail, 1)
        self.scene = Scene()


        print_log(f"creating inspector variables", LogType.Detail, 1)
        self.current_inspector_tab = 1

        self.tab_0 = None
        self.tab_1 = None
        self.tab_2 = None

        self.tab_0_state = 0
        self.tab_1_state = 0
        self.tab_2_state = 0

        self.tab_size = INSPECTOR_LEFT_PANEL_WIDTH / 3

        self.left_panel_divisor = None
        self.inspector_max_right_width = None

        self.inspector_right_width = INSPECTOR_LEFT_PANEL_WIDTH
        self.resizing_left_inspector_left_panel = False
        self.resizing_right_inspector_left_panel = False
        self.inspector_min_right_width = INSPECTOR_LEFT_PANEL_WIDTH

        self.inspector_nodes_display_size = INSPECTOR_LEFT_PANEL_WIDTH-20
        self.inspector_nodes_node_size = self.inspector_nodes_display_size/3

        self.inspector_selected_node = None

        self.resizing_inspector_left_panel = False
        self.can_resize_inspector_left_panel = False

        self.nodes = [
            Node,
            Target,
            Entity,
            Sprite,
            LoadingBar,
            GraphNode,
        ]

        self.nodes_display = None

        self.sub_runtime_0_thread = None


        print_log(f"creating hardware variables", LogType.Detail, 1)
        self.cpu_count = 0
        self.cpu_threads = 0
        self.cpu_name = ""

        self.gpu_count = 0
        self.gpu_name = ""
        self.gpu_total_video_memory = 0
        self.gpu_used_video_memory = 0

        self.os_arch = ""
        self.os_name = ""
        self.os_version = ""

        self.total_memory_amount = 0
        self.used_memory_amount = 0
        
        self.hardware_data_getter_thread = threading.Thread(target=self.get_hardware_data, daemon=True)
        

        print_log(f"creating loading screen variables", LogType.Detail, 1)
        self.ready = False
        self.ready_percentage = 0


        print_log(f"creating default fonts", LogType.Detail, 1)
        self.default_main_font = pygame.font.SysFont(DEFAULT_FONT, DEFAULT_MAIN_FONT_SIZE)
        self.default_title_font = pygame.font.SysFont(DEFAULT_FONT, DEFAULT_TITLE_FONT_SIZE)


        print_log(f"starting hardware getter thread", LogType.Detail, 1)
        self.hardware_data_getter_thread.start()


        print_log(f"starting loading screen", LogType.Detail, 1)
        self.loading_screen()


    def loading_screen(self):
        self.window = pygame.display.set_mode((WINDOW_LOADING_WIDTH, WINDOW_LOADING_HEIGHT), vsync=VSYNC_ENABLED, display=DEFAULT_DISPLAY)

        while not self.close_event.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_event.set()

            self.window.fill(BACKGROUND_COLOR)

            text = self.default_title_font.render("Loading", True, DEFAULT_FONT_COLOR)
            self.window.blit(text, (WINDOW_LOADING_WIDTH/2-text.get_size()[0]/2, WINDOW_LOADING_HEIGHT/2-text.get_size()[1]/2))

            percent = min(self.ready_percentage, 100) / 100.0
            pygame.draw.rect(self.window, (0, 255, 0), (0, WINDOW_LOADING_HEIGHT-20, WINDOW_LOADING_WIDTH * percent, 20))

            if self.ready_percentage > 80:
                text = self.default_main_font.render("Getting ready, wait", True, DEFAULT_FONT_COLOR)
                self.window.blit(text, (WINDOW_LOADING_WIDTH-text.get_size()[0]/2, WINDOW_LOADING_HEIGHT+DEFAULT_MAIN_FONT_SIZE))

            pygame.display.flip()

            if self.ready:
                break

        print_log("starting engine runtime", LogType.Detail, 1)
        self.start()


    def start(self):
        self.window = pygame.display.set_mode((WINDOW_BASE_WIDTH, WINDOW_BASE_HEIGHT), vsync=VSYNC_ENABLED, display=DEFAULT_DISPLAY)

        print_log(f"starting sub runtime 0", LogType.Detail, 1)
        self.sub_runtime_0_thread = threading.Thread(target=self.sub_runtime_0)
        self.sub_runtime_0_thread.start()

        print_log("initializing main runtime", LogType.Detail, 1)
        self.runtime()

        print_log("quitting modules", LogType.Detail, 1)
        pygame.quit()

        print_log(f"joining alive threads", LogType.Detail, 1)
        if self.sub_runtime_0_thread.is_alive():
            self.sub_runtime_0_thread.join()
        if self.hardware_data_getter_thread.is_alive():
            self.hardware_data_getter_thread.join()

    def sub_runtime_0(self):
        try:
            while not self.close_event.is_set():
                self.update_dynamic_tab_1_data()
        except Exception as _e:
            print_log(f"error initiating sub runtime 0 {_e}", LogType.Error, 1)

    def runtime(self):
        print_log(f"populating nodes display", LogType.Detail, 1)
        self.populate_nodes_in_display()

        print_log(f"starting main loop", LogType.Detail, 1)

        global RUNTIME_PROCESS_TIME
        global RUNTIME_NODES_UPDATE_TIME
        global RUNTIME_NODE_ICONS_DRAW_TIME
        global RUNTIME_INSPECTOR_TIME
        global RUNTIME_EVENT_PROCESS_TIME

        global INSPECTOR_LEFT_PANEL_WIDTH

        while not self.close_event.is_set():

            all_start_time = time.perf_counter()

            self.process_clock.tick(UPDATE_RATE)

            start_time = time.perf_counter()
            self.click_event.clear()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_event.set()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click_event.set()
                        print("click")
                if self.can_resize_inspector_left_panel:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.inspector_right_width is not None and event.pos is not None and abs(event.pos[0] - self.inspector_right_width) <= 5:
                            self.resizing_right_inspector_left_panel = True
                    elif self.inspector_right_width is not None and event.pos is not None and event.type == pygame.MOUSEMOTION and self.resizing_right_inspector_left_panel:
                        self.inspector_right_width = max(self.inspector_min_right_width, min(event.pos[0], self.inspector_max_right_width))

                        INSPECTOR_LEFT_PANEL_WIDTH = self.inspector_right_width

                        self.tab_size = INSPECTOR_LEFT_PANEL_WIDTH / 3

                    elif self.inspector_right_width is not None and event.pos is not None and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.resizing_right_inspector_left_panel = False

            RUNTIME_EVENT_PROCESS_TIME = time.perf_counter() - start_time
            self.window.fill(BACKGROUND_COLOR)

            start_time = time.perf_counter()
            self.scene.root_node.update()
            RUNTIME_NODES_UPDATE_TIME = time.perf_counter() - start_time

            start_time = time.perf_counter()
            self.scene.root_node.icon_draw()
            RUNTIME_NODE_ICONS_DRAW_TIME = time.perf_counter() - start_time

            start_time = time.perf_counter()
            self.inspector()
            RUNTIME_INSPECTOR_TIME = time.perf_counter() - start_time

            pygame.display.flip()
            RUNTIME_PROCESS_TIME = time.perf_counter() - all_start_time


    def populate_nodes_in_display(self):
        _nd_rect = pygame.Rect(10, INSPECTOR_TAB_HEIGHT+45, self.inspector_nodes_display_size, self.inspector_nodes_display_size)
        self.nodes_display = NodesDisplay(_nd_rect)
        self.nodes_display.click_event = self.click_event
        self.nodes_display.window = self.window

        for _node in self.nodes:
            new_node = NodesDisplayNode()

            t_node = _node()

            new_node.parent = self

            new_node.name = t_node.__class__.__name__
            new_node.node = _node
            new_node.icon = t_node.icon

            self.nodes_display.add_node(new_node)


    def inspector(self):
        pygame.draw.rect(self.window, (50, 50, 50), (0, 0, INSPECTOR_LEFT_PANEL_WIDTH, WINDOW_BASE_HEIGHT))
        self.left_panel_divisor = pygame.draw.rect(self.window, (255, 20, 20), (INSPECTOR_LEFT_PANEL_WIDTH, 0, 4, WINDOW_BASE_HEIGHT))

        if self.left_panel_divisor.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            self.can_resize_inspector_left_panel = True
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.can_resize_inspector_left_panel = False
            if self.resizing_right_inspector_left_panel:
                self.resizing_right_inspector_left_panel = False

        if self.current_inspector_tab == 0:
            self.draw_inspector_tab_0(2)
        else:
            self.draw_inspector_tab_0(0)

        if self.current_inspector_tab == 1:
            self.draw_inspector_tab_1(2)
        else:
            self.draw_inspector_tab_1(0)

        if self.current_inspector_tab == 2:
            self.draw_inspector_tab_2(2)
        else:
            self.draw_inspector_tab_2(0)

        if self.tab_0.collidepoint(pygame.mouse.get_pos()):
            if self.click_event.is_set():
                self.current_inspector_tab = 0
                self.inspector_selected_node = None
                self.draw_inspector_tab_0(2)
                print_log("inspector tab 0 selected", LogType.Detail, 1)
            else:
                if self.current_inspector_tab == 0:
                    self.draw_inspector_tab_0(3)
                else:
                    self.draw_inspector_tab_0(1)

        if self.tab_1.collidepoint(pygame.mouse.get_pos()):
            if self.click_event.is_set():
                self.current_inspector_tab = 1
                self.inspector_selected_node = None
                self.draw_inspector_tab_1(2)
                print_log("inspector tab 1 selected", LogType.Detail, 1)
            else:
                if self.current_inspector_tab == 1:
                    self.draw_inspector_tab_1(3)
                else:
                    self.draw_inspector_tab_1(1)

        if self.tab_2.collidepoint(pygame.mouse.get_pos()):
            if self.click_event.is_set():
                self.current_inspector_tab = 2
                self.inspector_selected_node = None
                self.draw_inspector_tab_2(2)
                print_log("inspector tab 2 selected", LogType.Detail, 1)
            else:
                if self.current_inspector_tab == 2:
                    self.draw_inspector_tab_2(3)
                else:
                    self.draw_inspector_tab_2(1)

        match self.current_inspector_tab:
            case 0:
                self.inspector_tab_0()
            case 1:
                self.inspector_tab_1()
            case 2:
                self.inspector_tab_2()

        if self.inspector_selected_node is not None:
            self.inspector_selected_node.position = pygame.math.Vector2(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])
            self.inspector_selected_node.render()

            if self.click_event.is_set():
                n_node = self.inspector_selected_node.get_copy().node()
                n_node.window = self.window
                n_node.position = pygame.mouse.get_pos()
                self.scene.add_node(n_node)

    def inspector_tab_0(self):
        text = self.default_title_font.render("Controls", True, DEFAULT_FONT_COLOR)
        self.window.blit(text, (INSPECTOR_LEFT_PANEL_WIDTH / 2 - text.get_width() / 2, INSPECTOR_TAB_HEIGHT + 10))

        self.nodes_display.render()

        text = self.default_main_font.render(f"Current Scene: {self.scene}", True, DEFAULT_FONT_COLOR)
        self.window.blit(text, (10, WINDOW_BASE_HEIGHT / 2 + 0 * (INSPECTOR_SUBTEXT_SIZE + 5)))
        text = self.default_main_font.render(f"Selected Node: {self.inspector_selected_node}", True, DEFAULT_FONT_COLOR)
        self.window.blit(text, (10, WINDOW_BASE_HEIGHT / 2 + 1 * (INSPECTOR_SUBTEXT_SIZE + 5)))
        text = self.default_main_font.render(f"NODES IN SCENE: {len(self.scene.root_node.children)}", True, DEFAULT_FONT_COLOR)
        self.window.blit(text, (10, WINDOW_BASE_HEIGHT / 2 + 2 * (INSPECTOR_SUBTEXT_SIZE + 5)))
        text_str = self.inspector_selected_node
        if self.inspector_selected_node is not None:
            text_str = float(pympler.asizeof.asizesof(self.inspector_selected_node.node())[0]) / 1024**2
        text = self.default_main_font.render(f"Selected Node Memory Usage: {text_str}MB", True, DEFAULT_FONT_COLOR)
        self.window.blit(text, (10, WINDOW_BASE_HEIGHT / 2 + 3 * (INSPECTOR_SUBTEXT_SIZE + 5)))

    def inspector_tab_1(self):
        text = self.default_title_font.render("Analysis", True, DEFAULT_FONT_COLOR)
        self.window.blit(text, (INSPECTOR_LEFT_PANEL_WIDTH / 2 - text.get_width() / 2, INSPECTOR_TAB_HEIGHT + 10))

        analysis_helper = [
            f"CPU name: {self.cpu_name}",
            f"GPU name: {self.gpu_name}",
            "",
            f"OS name: {self.os_name}",
            f"OS arch: {self.os_arch}",
            f"OS version: {self.os_version}",
            "",
            f"CPU cores: {self.cpu_count}",
            f"CPU threads: {self.cpu_threads}",
            "",
            f"GPU count: {self.gpu_count}",
            f"GPU total VRAM: {self.gpu_total_video_memory}GB",
            f"GPU used VRAM: {self.gpu_used_video_memory}GB",
            "",
            f"Total RAM: {self.total_memory_amount}GB",
            f"Used RAM: {self.used_memory_amount}GB",
            "",
            f"FPS: {self.render_clock.get_fps()}",
            f"Frame Time: {self.render_clock.get_time()}ms",
            f"Delta Time: {DELTA_TIME}ms",
            f"Tick Rate: {self.process_clock.get_fps()}",
            f"Tick Time: {self.process_clock.get_time()}ms",
            "",
            f"Runtime process time: {RUNTIME_PROCESS_TIME}",
            f"Runtime event process time: {RUNTIME_EVENT_PROCESS_TIME}",
            f"Runtime inspector time: {RUNTIME_INSPECTOR_TIME}",
            f"Runtime node icons draw time: {RUNTIME_NODE_ICONS_DRAW_TIME}",
            f"Runtime nodes update time: {RUNTIME_NODES_UPDATE_TIME}",
        ]

        for index, text in enumerate(analysis_helper):
            setting_text = self.default_main_font.render(text, True, DEFAULT_FONT_COLOR)
            self.window.blit(setting_text, (10, WINDOW_BASE_HEIGHT / 10 + index * (INSPECTOR_SUBTEXT_SIZE + 5)))


    def inspector_tab_2(self):
        text = self.default_title_font.render("Settings", True, DEFAULT_FONT_COLOR)
        self.window.blit(text, (INSPECTOR_LEFT_PANEL_WIDTH / 2 - text.get_width() / 2, INSPECTOR_TAB_HEIGHT + 10))

        settings_helper = [
            f"Empty Node Icon Path: {EMPTY_NODE_ICON_PATH}",
            f"Node Icon Path: {NODE_ICON_PATH}",
            f"Root Icon Path: {ROOT_ICON_PATH}",
            f"Default Font: {DEFAULT_FONT}",
            f"Inspector Tab Font Size: {INSPECTOR_TAB_FONT_SIZE}",
            f"Background Color: {BACKGROUND_COLOR}",
            f"Inspector Tab Base Color: {INSPECTOR_TAB_BASE_COLOR}",
            f"Inspector Tab Hover Color: {INSPECTOR_TAB_HOVER_COLOR}",
            f"Inspector Tab Selected Color: {INSPECTOR_TAB_SELECTED_COLOR}",
            f"Inspector Tab Selected Hover Color: {INSPECTOR_TAB_SELECTED_HOVER_COLOR}",
            f"Inspector Tab Base Text Color: {INSPECTOR_TAB_BASE_TEXT_COLOR}",
            f"Inspector Tab Hover Text Color: {INSPECTOR_TAB_HOVER_TEXT_COLOR}",
            f"Inspector Tab Selected Text Color: {INSPECTOR_TAB_SELECTED_TEXT_COLOR}",
            f"Inspector Tab Selected Hover Text Color: {INSPECTOR_TAB_SELECTED_HOVER_TEXT_COLOR}",
            f"Default Font Color: {DEFAULT_FONT_COLOR}",
            f"Inspector Subtext Size: {INSPECTOR_SUBTEXT_SIZE}",
            f"Window Width: {WINDOW_BASE_WIDTH}",
            f"Window Height: {WINDOW_BASE_HEIGHT}",
            f"Frame Rate: {FRAME_RATE}",
            f"Update Rate: {UPDATE_RATE}",
            f"Vsync Enabled: {VSYNC_ENABLED}",
            f"Default Display: {DEFAULT_DISPLAY}",
        ]

        for index, text in enumerate(settings_helper):
            setting_text = self.default_main_font.render(text, True, DEFAULT_FONT_COLOR)
            self.window.blit(setting_text, (10, WINDOW_BASE_HEIGHT / 10 + index * (INSPECTOR_SUBTEXT_SIZE + 5)))

    def draw_inspector_tab_0(self, state=0):
        font_color = INSPECTOR_TAB_BASE_TEXT_COLOR
        tab_color = INSPECTOR_TAB_BASE_COLOR

        match state:
            case 0:
                font_color = INSPECTOR_TAB_BASE_TEXT_COLOR
                tab_color = INSPECTOR_TAB_BASE_COLOR
            case 1:
                font_color = INSPECTOR_TAB_HOVER_TEXT_COLOR
                tab_color = INSPECTOR_TAB_HOVER_COLOR
            case 2:
                font_color = INSPECTOR_TAB_SELECTED_TEXT_COLOR
                tab_color = INSPECTOR_TAB_SELECTED_COLOR
            case 3:
                font_color = INSPECTOR_TAB_SELECTED_HOVER_TEXT_COLOR
                tab_color = INSPECTOR_TAB_SELECTED_HOVER_COLOR

        self.tab_0 = pygame.draw.rect(self.window, tab_color, (0, 0, self.tab_size, INSPECTOR_TAB_HEIGHT))
        tab_0_text = self.default_main_font.render("Tab 0", True, font_color)
        text_rect = tab_0_text.get_rect(center=self.tab_0.center)
        self.window.blit(tab_0_text, text_rect)

    def draw_inspector_tab_1(self, state=0):
        font_color = INSPECTOR_TAB_BASE_TEXT_COLOR
        tab_color = INSPECTOR_TAB_BASE_COLOR

        match state:
            case 0:
                font_color = INSPECTOR_TAB_BASE_TEXT_COLOR
                tab_color = INSPECTOR_TAB_BASE_COLOR
            case 1:
                font_color = INSPECTOR_TAB_HOVER_TEXT_COLOR
                tab_color = INSPECTOR_TAB_HOVER_COLOR
            case 2:
                font_color = INSPECTOR_TAB_SELECTED_TEXT_COLOR
                tab_color = INSPECTOR_TAB_SELECTED_COLOR
            case 3:
                font_color = INSPECTOR_TAB_SELECTED_HOVER_TEXT_COLOR
                tab_color = INSPECTOR_TAB_SELECTED_HOVER_COLOR

        self.tab_1 = pygame.draw.rect(self.window, tab_color, (self.tab_size, 0, self.tab_size, INSPECTOR_TAB_HEIGHT))
        tab_1_text = self.default_main_font.render("Tab 1", True, font_color)
        text_rect = tab_1_text.get_rect(center=self.tab_1.center)
        self.window.blit(tab_1_text, text_rect)

    def draw_inspector_tab_2(self, state=0):
        font_color = INSPECTOR_TAB_BASE_TEXT_COLOR
        tab_color = INSPECTOR_TAB_BASE_COLOR

        match state:
            case 0:
                font_color = INSPECTOR_TAB_BASE_TEXT_COLOR
                tab_color = INSPECTOR_TAB_BASE_COLOR
            case 1:
                font_color = INSPECTOR_TAB_HOVER_TEXT_COLOR
                tab_color = INSPECTOR_TAB_HOVER_COLOR
            case 2:
                font_color = INSPECTOR_TAB_SELECTED_TEXT_COLOR
                tab_color = INSPECTOR_TAB_SELECTED_COLOR
            case 3:
                font_color = INSPECTOR_TAB_SELECTED_HOVER_TEXT_COLOR
                tab_color = INSPECTOR_TAB_SELECTED_HOVER_COLOR

        self.tab_2 = pygame.draw.rect(self.window, tab_color, (self.tab_size*2, 0, self.tab_size, INSPECTOR_TAB_HEIGHT))
        tab_2_text = self.default_main_font.render("Tab 2", True, font_color)
        text_rect = tab_2_text.get_rect(center=self.tab_2.center)
        self.window.blit(tab_2_text, text_rect)


    def get_hardware_data(self):
        asyncio.run(self.get_hardware_data_async())

    def update_dynamic_tab_1_data(self):
        self.update_used_video_memory()

    def update_used_video_memory(self):
        used_video_memory = subprocess.check_output(["powershell", "-Command", "(Get-Counter '\\GPU Adapter Memory(*)\\Dedicated Usage').CounterSamples.CookedValue"], text=True)[0]
        video_memory = float(used_video_memory) / (1024 ** 3)
        self.gpu_used_video_memory = round(video_memory, 2)

    def update_used_memory(self):
        self.used_memory_amount = round(psutil.virtual_memory().used / (1024 ** 3), 2)

    async def get_hardware_data_async(self):
        print_log("getting hardware data", LogType.Detail, 1)

        print_log("getting cpu data", LogType.Detail, 2)
        self.ready_percentage += 7.7
        self.cpu_cores = await self.hardware_getter(HardwareCacheType.ProcessorCores)
        self.ready_percentage += 7.7
        self.cpu_threads = await self.hardware_getter(HardwareCacheType.ProcessorThreads)
        self.ready_percentage += 7.7
        self.cpu_name = await self.hardware_getter(HardwareCacheType.Processor)
        self.ready_percentage += 7.7

        print_log("getting system data", LogType.Detail, 2)
        self.os_name = await self.hardware_getter(HardwareCacheType.OperatingSystem)
        self.ready_percentage += 7.7
        self.os_arch = await self.hardware_getter(HardwareCacheType.SystemType)
        self.ready_percentage += 7.7
        self.os_version = platform.version()
        self.ready_percentage += 7.7

        print_log("getting memory data", LogType.Detail, 2)
        self.total_memory_amount = round(psutil.virtual_memory().total / (1024 ** 3))
        self.ready_percentage += 7.7
        self.update_used_memory()
        self.ready_percentage += 7.7

        print_log("preparing to get gpus data", LogType.Detail, 2)
        
        print_log("creating wmi computer", LogType.Detail, 3)
        computer = wmi.WMI()

        print_log("getting gpus", LogType.Detail, 3)
        gpus = computer.Win32_VideoController()
        self.gpu_count = len(gpus)
        self.ready_percentage += 7.7

        print_log("getting main gpu data", LogType.Detail, 3)
        self.gpu_name = await self.hardware_getter(HardwareCacheType.GpuName)
        self.ready_percentage += 7.7

        self.gpu_total_video_memory = await self.hardware_getter(HardwareCacheType.GpuVideoMemory)
        self.ready_percentage += 7.7

        self.update_used_video_memory()
        self.ready_percentage += 7.7

        print_log("hardware data got", LogType.Detail, 1)
        self.ready = True

    async def hardware_getter(self, data_type:HardwareCacheType):
        print_log("locating hardware data cache", LogType.Detail, 2)
        local_app_data = os.environ["LOCALAPPDATA"]
        engine_cache = os.path.join(local_app_data, "duck_engine")

        if not os.path.isdir(engine_cache):
            print_log("cache folder not found, creating", LogType.Detail, 3)
            os.mkdir(engine_cache)

        if not os.path.exists(engine_cache + "/hardware_data_cache.json"):
            print_log("cache file not found, creating", LogType.Detail, 3)
            os.open(engine_cache + "/hardware_data_cache.json", os.O_CREAT)
            self.create_hardware_data_cache(engine_cache)

        print_log("all right to ready cache", LogType.Detail, 3)

        content = self.read_hardware_data_cache(engine_cache)
        match data_type:
            case HardwareCacheType.GpuVideoMemory:
                return content["gpu_video_memory"]
            case HardwareCacheType.GpuName:
                return content["gpu_name"]
            case HardwareCacheType.GpuChipType:
                return content["gpu_chip_type"]
            case HardwareCacheType.RamTotalMemory:
                return content["ram_total_memory"]
            case HardwareCacheType.PageFileMemory:
                return content["page_file_memory"]
            case HardwareCacheType.OperatingSystem:
                return content["operating_system"]
            case HardwareCacheType.Language:
                return content["language"]
            case HardwareCacheType.Manufacturer:
                return content["manufacturer"]
            case HardwareCacheType.Processor:
                    return content["processor_name"]
            case HardwareCacheType.ProcessorClockSpeed:
                return content["processor_clock_speed"]
            case HardwareCacheType.ProcessorCores:
                return content["processor_cores"]
            case HardwareCacheType.DxVersion:
                return content["dx_version"]
            case HardwareCacheType.SystemManufacturer:
                return content["system_manufacturer"]
            case HardwareCacheType.SystemModel:
                return content["system_model"]
            case HardwareCacheType.SystemType:
                return content["system_type"]


    @staticmethod
    def read_hardware_data_cache(engine_cache):
        all_data = {}

        file = open(engine_cache + "/hardware_data_cache.json", "r")
        content = file.read()
        file.close()

        print_log("reading all data", LogType.Detail, 3)
        memory_mb = re.findall(r"<DedicatedMemory>(.*?)</DedicatedMemory>", content)

        print_log("finding correct memory value", LogType.Detail, 2)
        much_video_memory = 0

        print(memory_mb)
        for mem_text in memory_mb:
            numbers = "".join(filter(str.isdigit, mem_text))
            if numbers:
                video_memory = round(int(numbers) / 1024)
                if video_memory > much_video_memory:
                    much_video_memory = video_memory

        all_data["gpu_video_memory"] = 0

        print_log("verifying memory value", LogType.Detail, 2)
        if much_video_memory > 0:
            all_data["gpu_video_memory"] = much_video_memory

        all_data["gpu_name"] = re.findall(r"<CardName>(.*?)</CardName>", content)[0]
        all_data["gpu_chip_type"] = re.findall(r"<ChipType>(.*?)</ChipType>", content)[0]
        all_data["ram_total_memory"] = re.findall(r"<Memory>(.*?)</Memory>", content)[0]
        all_data["page_file_memory"] = re.findall(r"<PageFile>(.*?)</PageFile>", content)[0]
        all_data["operating_system"] = re.findall(r"<OperatingSystem>(.*?)</OperatingSystem>", content)[0]
        all_data["system_manufacturer"] = re.findall(r"<SystemManufacturer>(.*?)</SystemManufacturer>", content)[0]
        all_data["system_model"] = re.findall(r"<SystemModel>(.*?)</SystemModel>", content)[0]

        is_64b = re.findall(r"<DxDiag64Bit>(.*?)</DxDiag64Bit>", content)[0]
        if is_64b == "1":
            all_data["system_type"] = "x64"
        else:
            all_data["system_type"] = "x32"

        all_data["language"] = re.findall(r"<Language>(.*?)</Language>", content)[0]
        all_data["dx_version"] = re.findall(r"<DirectXVersion>(.*?)</DirectXVersion>", content)[0]

        processor = re.findall(r"<Processor>(.*?)</Processor>", content)[0]
        cpus = re.findall(r"\((\d+) CPUs\)", processor)[0]
        all_data["processor_name"] = re.findall(r"<Processor>(.*?) \(\d+ CPUs\)", content)[0]
        all_data["processor_cores"] = cpus
        all_data["processor_clock_speed"] = re.findall(r"~([\d.]+)GHz", content)[0]
        all_data["manufacturer"] = re.findall(r"<Manufacturer>(.*?)</Manufacturer>", content)[0]

        return all_data

    @staticmethod
    def create_hardware_data_cache(engine_cache):
        file = open(engine_cache + "/hardware_data_cache.json", "w+")
        try:
            print_log("creating temp file", LogType.Detail, 4)
            temp_file = os.path.join(os.environ["TEMP"], "dx_vram_report.xml")

            print_log("creating subprocess", LogType.Detail, 4)
            subprocess.run(["dxdiag", "/x", temp_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           check=True)

            print_log("verifying temp files as generated", LogType.Detail, 4)
            if os.path.exists(temp_file):
                print_log("trying to open temp file", LogType.Detail, 4)
                with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                print_log("deleting temp file", LogType.Detail, 4)
                os.remove(temp_file)

                print_log("writing hardware cache", LogType.Detail, 4)
                file.write(content)
                file.close()
        except Exception as _e:
            print_log("error creating hardware cache", LogType.Error, 3)




if __name__ == "__main__":
    print_log("starting engine", LogType.Core, 0)
    try:
        engine = Engine()
        print_log("quitting engine", LogType.Core, 0)
    except Exception as e:
        print_log("error starting engine", LogType.Core, 0)
        print_log(f"{e}", LogType.Error, 1)