import json
import os
import re
import subprocess
import psutil

import settings


def create_hardware_data_cache():
    file_path = "cache/hdc.json"
    folder_path = os.path.dirname(file_path)
    if folder_path:
        os.makedirs(folder_path, exist_ok=True)

    try:
        h_data = {}

        h_data["CacheVersion"] = settings.HDC_VERSION

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
            video_memory = re.search(r"Video memory:\s*([0-9]+(?:\s*[MGB][B]))", brute_data).group(1)
            h_data["GpuVideoMemory"] = video_memory

        memory_getter = psutil.virtual_memory()
        memory_total = memory_getter.total / 1024 / 1024 / 1024

        h_data["MemoryTotal"] = str(memory_total)

        with open("cache/hdcs.json", "w") as f:
            json.dump(h_data, f, indent=4)

    except Exception as _e:
        print(f"error {_e}")

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


if __name__ == "__main__":
    create_hardware_data_cache()