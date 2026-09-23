import platform
import socket


def get_system_info():
    system_info = {
        "computer_name": socket.gethostname(),
        "operating_system": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor()
    }

    return system_info

