from logger import *
import subprocess
import os
import re


def hardware_getter():
    print_log("locating hardware data cache", LogType.Detail, 2)
    local_app_data = os.environ["LOCALAPPDATA"]
    engine_cache = os.path.join(local_app_data, "duck_engine")

    if not os.path.isdir(engine_cache):
        print_log("cache folder not found, creating", LogType.Detail, 3)
        os.mkdir(engine_cache)

    if not os.path.exists(engine_cache + "/hardware_data_cache.json"):
        print_log("cache file not found, creating", LogType.Detail, 3)
        os.open(engine_cache + "/hardware_data_cache.json", os.O_CREAT)
        create_hardware_data_cache(engine_cache)

    print_log("all right to ready cache", LogType.Detail, 3)
    read_hardware_data_cache(engine_cache)


def read_hardware_data_cache(engine_cache):
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

    print_log("verifying memory value", LogType.Detail, 2)
    if much_video_memory > 0:
        print(much_video_memory)

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


hardware_getter()