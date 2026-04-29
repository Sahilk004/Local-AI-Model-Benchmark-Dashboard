import psutil
import os

def get_system_metrics():
    """Returns current RAM and CPU usage."""
    ram = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=None) # Don't block
    return {
        "ram_used_gb": ram.used / (1024**3),
        "ram_total_gb": ram.total / (1024**3),
        "ram_percent": ram.percent,
        "cpu_percent": cpu
    }

def get_process_ram_mb():
    """Returns memory usage of current process in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)
