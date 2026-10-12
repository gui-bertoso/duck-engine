import json
import locale
import os
import platform
import re
import subprocess
import psutil

import settings


def to_snake_case(name):
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()

def create_hardware_data_cache():
    file_path = "cache/hdc.json"
    folder_path = os.path.dirname(file_path)
    if folder_path:
        os.makedirs(folder_path, exist_ok=True)

    try:
        h_data = {}

        h_data["CacheVersion"] = settings.HDC_VERSION

        system_name = platform.system()
        h_data["OperationalSystem"] = system_name
        system_version = platform.release()
        h_data["OperationalSystemVersion"] = system_version
        system_platform = platform.platform()
        h_data["OperatingSystemPlatform"] = system_platform


        language, codification = locale.getdefaultlocale()
        h_data["Language"] = language
        h_data["LanguageCodification"] = codification

        lscpu_getter = subprocess.run(
            ["lscpu", "--json"],
            capture_output=True,
            check=True,
            text=True,
            timeout=10,
            env={**__import__("os").environ, "LC_ALL": "C"}
        )

        if lscpu_getter.returncode == 0:
            datas = json.loads(lscpu_getter.stdout)["lscpu"]
            for data in datas:
                h_data[data['field']] = data['data']

        glxinfo_getter = subprocess.run(
            "glxinfo",
            capture_output=True,
            check=True,
            text=True,
            timeout=10,
            env={**__import__("os").environ, "LC_ALL": "C"}
        )

        if glxinfo_getter.returncode == 0:
            brute_data = glxinfo_getter.stdout
            vendor = re.search(r"Vendor:\s*(.+?)(?:\s*\(|$)", brute_data).group(1)
            h_data["GpuVendor"] = vendor
            device = re.search(r"Device:\s*(.+?)(?:\s*\(|$)", brute_data).group(1)
            h_data["GpuName"] = device
            video_memory = re.search(r"Video memory:\s*([0-9]+)\s*[MGB]B", brute_data).group(1)
            h_data["GpuVideoMemory"] = str(round((int(video_memory)  / 1024), 1)) + "GB"

        memory_getter = psutil.virtual_memory()
        memory_total = memory_getter.total / 1024 / 1024 / 1024

        h_data["MemoryTotal"] = str(round(memory_total, 1)) + "GB"

        h_data = {
            to_snake_case(key): value
            for key, value in h_data.items()
        }

        with open(file_path, "w") as f:
            json.dump(h_data, f, indent=4)

    except Exception as _e:
        print(f"error {_e}")


def read_hardware_data_cache():
    file_path = "cache/hdc.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    print(read_hardware_data_cache())