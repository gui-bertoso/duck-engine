import enum


class Window(enum.Enum):
    Loading = 0
    Main = 1


class LogType(enum.Enum):
    Info = 0
    Warning = 1
    Error = 2
    Debug = 3
    Detail = 4
    Core = 5


class SceneLoadState(enum.Enum):
    PathIsNotScene = 1
    PathIsNotFound = 2
    SuccessfulLoaded = 3
    UnknownError = 4
    PathIsNone = 5


class ButtonState(enum.Enum):
    Clicked = 2
    Hovered = 1
    Standard = 0
    Disabled = 3

class HardwareCacheType(enum.Enum):
    GpuVideoMemory = 0
    GpuName = 1
    GpuChipType = 2
    RamTotalMemory = 3
    PageFileMemory = 4
    OperatingSystem = 5
    SystemManufacturer = 6
    SystemModel = 7
    SystemType = 8
    Language = 9
    Processor = 10
    ProcessorCores = 11
    ProcessorThreads = 12
    ProcessorClockSpeed = 13
    Manufacturer = 14
    DxVersion = 15