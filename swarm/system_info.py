import socket
import sys
import os
import platform
import ctypes
from typing import Tuple, Dict

def get_system_ram_mb() -> Tuple[int, int]:
    """
    Returns (total_ram_mb, available_ram_mb).
    Works reliably on Windows, Linux, and macOS without requiring external packages.
    Falls back gracefully if psutil is not installed.
    """
    try:
        import psutil
        vm = psutil.virtual_memory()
        return int(vm.total / (1024 * 1024)), int(vm.available / (1024 * 1024))
    except ImportError:
        pass

    # Windows Native fallback via ctypes
    if platform.system() == "Windows":
        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                total = int(stat.ullTotalPhys / (1024 * 1024))
                avail = int(stat.ullAvailPhys / (1024 * 1024))
                return total, avail
        except Exception:
            pass

    # Linux native fallback
    if platform.system() == "Linux" and os.path.exists("/proc/meminfo"):
        try:
            mem_info = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].split()[0].strip()
                        mem_info[key] = int(val)
            total = int(mem_info.get("MemTotal", 4000000) / 1024)
            avail = int(mem_info.get("MemAvailable", mem_info.get("MemFree", 2000000)) / 1024)
            return total, avail
        except Exception:
            pass

    # Default fallback assumption (4GB total, 2GB available)
    return 4096, 2048

def get_local_ip() -> str:
    """
    Finds the primary local LAN IP address of this machine.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def get_node_id() -> str:
    """Returns a friendly identifier for this machine."""
    hostname = socket.gethostname()
    system = platform.system()
    return f"{hostname} ({system})"

def calculate_safe_ram_contribution(reserve_mb: int = 1200) -> int:
    """
    Calculates how much RAM can be donated to the cluster while keeping
    the host system responsive.
    """
    total_mb, avail_mb = get_system_ram_mb()
    safe_max = max(512, total_mb - reserve_mb)
    safe_budget = min(safe_max, int(avail_mb * 0.85))
    return max(512, safe_budget)

def get_full_node_specs(reserve_mb: int = 1200) -> Dict:
    total_mb, avail_mb = get_system_ram_mb()
    contribution_mb = calculate_safe_ram_contribution(reserve_mb)
    return {
        "node_id": get_node_id(),
        "hostname": socket.gethostname(),
        "ip": get_local_ip(),
        "platform": platform.platform(),
        "total_ram_mb": total_mb,
        "available_ram_mb": avail_mb,
        "contributed_ram_mb": contribution_mb
    }

def interactive_ram_chooser(reserve_mb: int = 1200) -> int:
    """
    Shows the user their PC RAM stats and lets them choose how much to share.
    Returns the chosen amount in Megabytes.
    """
    total_mb, avail_mb = get_system_ram_mb()
    safe_default = calculate_safe_ram_contribution(reserve_mb)
    max_share = max(512, avail_mb - 600)
    
    print("\n---------------------------------------------------------")
    print("           📊 Your PC Memory Contribution Options        ")
    print("---------------------------------------------------------")
    print(f"[*] Total Installed RAM:  {round(total_mb / 1024, 1)} GB ({total_mb} MB)")
    print(f"[*] Currently Free:       {round(avail_mb / 1024, 1)} GB ({avail_mb} MB)")
    print(f"[*] Reserved for Windows: ~{round(reserve_mb / 1024, 1)} GB (keeps your computer smooth)")
    print("---------------------------------------------------------")
    print(f"  [1] Recommended: {round(safe_default / 1024, 1)} GB ({safe_default} MB)  <-- Best balance")
    print(f"  [2] Maximum:     {round(max_share / 1024, 1)} GB ({max_share} MB)  <-- Maximum power for cluster")
    print(f"  [3] Minimum:     0.5 GB (512 MB)        <-- Lightest background impact")
    print(f"  [4] Custom:      Type your own amount in MB")
    print("---------------------------------------------------------")
    
    try:
        choice = input("[?] Choose [1/2/3/4] (press Enter for Recommended): ").strip()
    except EOFError:
        choice = "1"

    if choice == "2":
        chosen = max_share
        print(f"[+] Selected Maximum: {round(chosen / 1024, 1)} GB ({chosen} MB)")
    elif choice == "3":
        chosen = 512
        print(f"[+] Selected Minimum: 0.5 GB (512 MB)")
    elif choice == "4":
        try:
            custom_input = input("[?] Enter RAM to donate in MB (e.g. 2000): ").strip()
            custom_val = int(custom_input)
            chosen = max(256, min(custom_val, avail_mb - 300))
            print(f"[+] Selected Custom: {round(chosen / 1024, 1)} GB ({chosen} MB)")
        except Exception:
            chosen = safe_default
            print(f"[!] Invalid input. Using Recommended: {round(chosen / 1024, 1)} GB ({chosen} MB)")
    else:
        chosen = safe_default
        print(f"[+] Selected Recommended: {round(chosen / 1024, 1)} GB ({chosen} MB)")

    return chosen
