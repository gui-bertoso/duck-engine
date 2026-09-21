from enums import LogType


def print_log(message, type, indent=0):
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