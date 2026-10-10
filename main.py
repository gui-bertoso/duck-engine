import os

from enums import *

import logging

logging.basicConfig(level=logging.FATAL)

from nodes import *
from settings import *
from scene import *

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import threading
import platform
import time
import psutil
import wmi
import subprocess
import re
import asyncio

DELTA_TIME = 0.0
RUNTIME_PROCESS_TIME = 0.0
RENDER_TIME = 0.0
RUNTIME_RENDER_TIME = 0.0

RUNTIME_EVENT_PROCESS_TIME = 0.0
RUNTIME_NODES_UPDATE_TIME = 0.0
RUNTIME_NODE_ICONS_DRAW_TIME = 0.0
RUNTIME_INSPECTOR_TIME = 0.0

TICK_RATE_COUNT = 0
RENDER_RATE_COUNT = 0

INSPECTOR_LEFT_PANEL_WIDTH = 400

CURRENT_LOADING_TEXT = ""


def print_log(message, type, indent=0):
    global CURRENT_LOADING_TEXT
    prefix = ""
    if type == LogType.Info:
        prefix = "[INFO]"
    elif type == LogType.Warning:
        prefix = "[WARNING]"
    elif type == LogType.Error:
        prefix = "[ERROR]"
    elif type == LogType.Debug:
        prefix = "[DEBUG]"
    elif type == LogType.Detail:
        prefix = "[+]"
    elif type == LogType.Core:
        prefix = "[CORE]"
    else:
        prefix = ""

    indentation = "      " * indent
    print(f"{indentation}{prefix} {message}")
    CURRENT_LOADING_TEXT = message


class Engine:
    def __init__(self):

        self.inspector_profiler_dynamic_label = None
        self.render_thread = None
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

        self.inspector_node_pack = None

        self.nodes = [
            Controller,
            EmptyNode,
            Entity,
            GraphNode,
            LoadingBar,
            Node,
            Rect,
            RootNode,
            SimulatedEntity,
            Sprite,
            Target,
            TargetController,
        ]

        self.nodes_display = None

        self.sub_runtime_0_thread = None

        self.inspector_max_right_width = INSPECTOR_LEFT_PANEL_WIDTH * 2


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


        self.current_scene = None


        print_log(f"creating default fonts", LogType.Detail, 1)
        self.default_main_font = pygame.font.SysFont(DEFAULT_FONT, DEFAULT_MAIN_FONT_SIZE)
        self.default_title_font = pygame.font.SysFont(DEFAULT_FONT, DEFAULT_TITLE_FONT_SIZE)


        print_log(f"starting hardware getter thread", LogType.Detail, 1)
        self.hardware_data_getter_thread.start()


        print_log(f"starting loading screen", LogType.Detail, 1)
        self.loading_screen()





    def create_scene_packs(self):
        print_log(f"creating nodes and node packs", LogType.Detail, 1)
        self.inspector_node_pack = NodePack()

        tp = TabsPanel()
        tp.window = self.window
        tp.size.y = WINDOW_BASE_HEIGHT
        tp.size.x = INSPECTOR_LEFT_PANEL_WIDTH
        tp.position = pygame.math.Vector2(0, 0)
        tp.click_event = self.click_event

        tp.add_tab(self.create_tab_0_node_pack())
        tp.add_tab(self.create_tab_1_node_pack())
        tp.add_tab(self.create_tab_2_node_pack())
        tp.add_tab(self.create_tab_3_node_pack())

        self.inspector_node_pack.add_node(tp)



    def create_tab_0_node_pack(self):
        n = NodePack()
        n.name = f"Node"
        a = list(vars(Button()).keys())
        b = list(vars(Button()).values())

        t_text = ""
        for i2 in a:
            t_text += str(i2) + "\n"

        bt_text = ""
        for bi2 in b:
            bt_text += self.parse_property_value(bi2) + "\n"


        l = Label()
        l.window = self.window
        l.position = pygame.math.Vector2(160, 40)
        l.text = "Properties"
        l.update_render_data()

        sl = ScrollableLabel()
        sl.window = self.window
        sl.position = pygame.math.Vector2(20, 70)
        sl.text = t_text
        sl.font_size = 16
        sl.update_render_data()

        sl2 = ScrollableLabel()
        sl2.window = self.window
        sl2.position = pygame.math.Vector2(220, 70)
        sl2.text = bt_text
        sl2.font_size = 16
        sl2.update_render_data()

        n.add_node(l)
        n.add_node(sl)
        n.add_node(sl2)

        return n

    def create_tab_1_node_pack(self):
        n = NodePack()
        n.name = f"Hardware"
        a = [
            "CPU Name",
            "CPU Cores",
            "CPU Threads",
            "",
            "GPU Name",
            "GPU Total VRAM",
            "GPU Used VRAM",
            "",
            "Total Memory",
            "used Memory",
        ]
        b = [
            f"{self.cpu_name}",
            f"{self.cpu_cores}",
            f"{self.cpu_threads}",
            "",
            f"{self.gpu_name}",
            f"{self.gpu_total_video_memory}",
            f"{self.gpu_used_video_memory}",
            "",
            f"{self.total_memory_amount}",
            f"{self.used_memory_amount}",
        ]

        t_text = ""
        for i2 in a:
            t_text += str(i2) + "\n"

        bt_text = ""
        for bi2 in b:
            bt_text += self.parse_property_value(bi2) + "\n"


        l = Label()
        l.window = self.window
        l.position = pygame.math.Vector2(160, 40)
        l.text = "Hardware"
        l.update_render_data()

        sl = ScrollableLabel()
        sl.window = self.window
        sl.position = pygame.math.Vector2(20, 70)
        sl.text = t_text
        sl.font_size = 16
        sl.update_render_data()

        sl2 = ScrollableLabel()
        sl2.window = self.window
        sl2.position = pygame.math.Vector2(220, 70)
        sl2.text = bt_text
        sl2.font_size = 16
        sl2.update_render_data()

        n.add_node(l)
        n.add_node(sl)
        n.add_node(sl2)

        return n

    def create_tab_2_node_pack(self):
        n = NodePack()
        n.name = f"Nodes"
        a = list(vars(Button()).keys())
        b = list(vars(Button()).values())

        t_text = ""
        for i2 in a:
            t_text += str(i2) + "\n"

        bt_text = ""
        for bi2 in b:
            bt_text += self.parse_property_value(bi2) + "\n"


        l = Label()
        l.window = self.window
        l.position = pygame.math.Vector2(160, 40)
        l.text = "Nodes picker"
        l.update_render_data()


        nd = NodesDisplay()
        nd.window = self.window
        nd.click_event = self.click_event
        nd.position = pygame.math.Vector2(20, 70)
        nd.update_rect_data()

        for node in self.nodes:
            na = NodesDisplayNode()
            na.name = node.__name__
            na.node = node
            nd.add_node(na)


        n.add_node(l)
        n.add_node(nd)

        return n

    def create_tab_3_node_pack(self):

        n = NodePack()
        n.name = f"Profiler"
        a = [
            "TickRate",
            "FrameRate",
            "",
            "TickTime",
            "FrameTime",
        ]
        b = [
            f"{TICK_RATE_COUNT}",
            f"{RENDER_RATE_COUNT}",
            "",
            f"{RUNTIME_PROCESS_TIME}",
            f"{RUNTIME_RENDER_TIME}",
        ]

        bt_text = ""
        for bi2 in b:
            bt_text += self.parse_property_value(bi2) + "\n"


        t_text = ""
        for i2 in a:
            t_text += str(i2) + "\n"


        l = Label()
        l.window = self.window
        l.position = pygame.math.Vector2(160, 40)
        l.text = "Profiler"
        l.update_render_data()

        sl = ScrollableLabel()
        sl.window = self.window
        sl.position = pygame.math.Vector2(20, 70)
        sl.text = t_text
        sl.font_size = 16
        sl.update_render_data()

        sl2 = ScrollableLabel()
        sl2.window = self.window
        sl2.position = pygame.math.Vector2(220, 70)
        sl2.text = bt_text
        sl2.font_size = 16
        sl2.update_render_data()

        self.inspector_profiler_dynamic_label = sl2

        n.add_node(l)
        n.add_node(sl)
        n.add_node(sl2)

        return n

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

            text = self.default_main_font.render(CURRENT_LOADING_TEXT, True, DEFAULT_FONT_COLOR)
            self.window.blit(text, (WINDOW_LOADING_WIDTH - text.get_size()[0] / 2, WINDOW_LOADING_HEIGHT + DEFAULT_MAIN_FONT_SIZE))

            pygame.display.flip()

            if self.ready:
                break

        print_log("starting engine runtime", LogType.Detail, 1)
        self.start()


    def start(self):
        print_log(f"creating main window", LogType.Detail, 1)
        self.window = pygame.display.set_mode((WINDOW_BASE_WIDTH, WINDOW_BASE_HEIGHT), vsync=VSYNC_ENABLED, display=DEFAULT_DISPLAY)

        print_log(f"creating inspector node packs", LogType.Detail, 1)
        self.create_scene_packs()

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
        if self.render_thread.is_alive():
            self.render_thread.join()

    def sub_runtime_0(self):
        try:
            while not self.close_event.is_set():
                self.update_dynamic_tab_1_data()
        except Exception as _e:
            print_log(f"error initiating sub runtime 0 {_e}", LogType.Error, 1)

    def runtime_renderer(self):
        global RUNTIME_RENDER_TIME
        global RENDER_RATE_COUNT

        while not self.close_event.is_set():

            all_start_time = time.perf_counter()

            self.render_clock.tick(FRAME_RATE)

            for _ev in pygame.event.get():
                if _ev.type == pygame.QUIT:
                    self.close_event.set()

            self.window.fill(BACKGROUND_COLOR)

            if self.current_scene is not None:
                self.current_scene.root_node.icon_draw()
                self.current_scene.root_node.render()

                text = self.default_main_font.render("SCENE NOT LOADED", True, DEFAULT_FONT_COLOR)
                self.window.blit(text, (WINDOW_BASE_WIDTH-INSPECTOR_LEFT_PANEL_WIDTH, WINDOW_BASE_HEIGHT))

            self.inspector_node_pack.render()
            pygame.display.flip()

            RENDER_RATE_COUNT = self.render_clock.get_fps()
            RUNTIME_RENDER_TIME = time.perf_counter() - all_start_time

    def runtime_processer(self):
        global RUNTIME_PROCESS_TIME
        global RUNTIME_NODES_UPDATE_TIME
        global RUNTIME_NODE_ICONS_DRAW_TIME
        global RUNTIME_INSPECTOR_TIME
        global RUNTIME_EVENT_PROCESS_TIME
        global TICK_RATE_COUNT

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
                    elif self.inspector_right_width is not None and event.pos is not None and event.pos[0] is not None and self.inspector_max_right_width is not None and event.type == pygame.MOUSEMOTION and self.resizing_right_inspector_left_panel:

                        self.inspector_right_width = max(self.inspector_min_right_width, min(event.pos[0], self.inspector_max_right_width))

                        INSPECTOR_LEFT_PANEL_WIDTH = self.inspector_right_width

                        self.tab_size = INSPECTOR_LEFT_PANEL_WIDTH / 3

                    elif self.inspector_right_width is not None and event.pos is not None and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.resizing_right_inspector_left_panel = False

            RUNTIME_EVENT_PROCESS_TIME = time.perf_counter() - start_time

            self.update_inspector_dynamic_texts()

            if self.current_scene is not None:
                start_time = time.perf_counter()
                self.current_scene.root_node.update()
                RUNTIME_NODES_UPDATE_TIME = time.perf_counter() - start_time

                RUNTIME_NODES_UPDATE_TIME = "SceneNotLoaded"
                RUNTIME_NODE_ICONS_DRAW_TIME = "SceneNotLoaded"

            self.inspector_node_pack.update()

            TICK_RATE_COUNT = self.process_clock.get_fps()
            RUNTIME_PROCESS_TIME = time.perf_counter() - all_start_time

    def update_inspector_dynamic_texts(self):
        self.update_inspector_profiler_dynamic_texts()

    def update_inspector_profiler_dynamic_texts(self):
        b = [
            f"{TICK_RATE_COUNT}",
            f"{RENDER_RATE_COUNT}",
            "",
            f"{RUNTIME_PROCESS_TIME}",
            f"{RUNTIME_RENDER_TIME}",
        ]

        bt_text = ""
        for bi2 in b:
            bt_text += self.parse_property_value(bi2) + "\n"

        self.inspector_profiler_dynamic_label.text = bt_text
        self.inspector_profiler_dynamic_label.update_render_data()

    def runtime(self):

        print_log(f"starting main loop", LogType.Detail, 1)

        self.render_thread = threading.Thread(target=self.runtime_renderer)
        self.render_thread.start()

        self.runtime_processer()


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
        return None

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

    @staticmethod
    def parse_property_value(value):
        if isinstance(value, pygame.Color):
            return f"({value.r}, {value.g}, {value.b})"
        if isinstance(value, pygame.Surface):
            return f"{value.get_width()}x{value.get_height()}"
        if isinstance(value, pygame.Rect):
            return f"RectObj"
        if isinstance(value, list):
            return f"ListObj ({len(value)} items)"
        if isinstance(value, pygame.font.Font):
            return f"FontObj"
        if value is None:
            return f"None"
        return str(value)

    @staticmethod
    def create_scene(_scene: Scene):
        scene_name = _scene.scene_name
        scene_version = _scene.scene_version
        scene_id = _scene.scene_id

        file_template = f"FILETYPE SCENE\n\nscene_name -> {scene_name}\nscene_version -> {scene_version}\nscene_id -> {scene_id}"
        file_template += "\n\nchildren -> {\n"
        for child in _scene.nodes:
            file_template += child.serialize_node(1)

        file_template += "}"

        t_file = open(SCENES_FOLDER_PATH + scene_name + SCENE_EXTENSION, "w+")
        t_file.write(file_template)
        t_file.close()

    @staticmethod
    def load_scene(scene_path):
        if not scene_path:
            return [SceneLoadState.PathIsNone, None]
        if not scene_path.endswith(SCENE_EXTENSION):
            return [SceneLoadState.PathIsNotScene, None]
        if not os.path.exists(scene_path):
            return [SceneLoadState.PathIsNotFound, None]

        file = open(scene_path, "r")
        brute_data = file.read()
        print(brute_data)

        extracted_datas = {}

        for line in brute_data.split("\n"):
            match = re.match(SCENE_DATA_GETTER_REGEX, line)
            if match:
                extracted_datas[match.group(1)] = match.group(2)

        print(extracted_datas)

        loaded_scene = Scene()
        try:
            loaded_scene.scene_name = extracted_datas["scene_name"]
        except KeyError:
            loaded_scene.scene_name = "NotFound"
        try:
            loaded_scene.scene_version = extracted_datas["scene_version"]
        except KeyError:
            loaded_scene.scene_version = "NotFound"
        try:
            loaded_scene.scene_id = extracted_datas["scene_id"]
        except KeyError:
            loaded_scene.scene_id = "NotFound"

        print(loaded_scene)
        return [SceneLoadState.SuccessfulLoaded, loaded_scene]



if __name__ == "__main__":
    engine = Engine()
