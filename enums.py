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