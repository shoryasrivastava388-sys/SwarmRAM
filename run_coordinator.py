import argparse
import sys
import threading
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from swarm.config import DEFAULT_COORDINATOR_PORT
from swarm.system_info import get_local_ip, get_full_node_specs
from swarm.coordinator import SwarmCoordinator
from swarm.web.server import run_web_server

def main():
    parser = argparse.ArgumentParser(description="SwarmRAM Cluster Coordinator (Master Node)")
    parser.add_argument("--port", type=int, default=DEFAULT_COORDINATOR_PORT, help="Port for the Web UI & API (default: 8080)")
    parser.add_argument("--model", type=str, default=None, help="Optional GGUF model filename in models/ folder to load")
    args = parser.parse_args()

    local_ip = get_local_ip()
    specs = get_full_node_specs()

    print("==================================================================")
    print("       ⚡ SwarmRAM — Neural Memory Cluster Coordinator ⚡         ")
    print("==================================================================")
    print(f"[*] Hostname:         {specs['hostname']}")
    print(f"[*] Local LAN IP:     {local_ip}")
    print(f"[*] Local System RAM: {round(specs['total_ram_mb'] / 1024, 1)} GB (Donating {round(specs['contributed_ram_mb'] / 1024, 1)} GB)")
    print(f"[*] Web Dashboard:    http://localhost:{args.port}  or  http://{local_ip}:{args.port}")
    print("------------------------------------------------------------------")
    print("[*] Tell your friends on the same Wi-Fi / LAN to run:")
    print(f"    python run_worker.py --coordinator {local_ip}:{args.port}")
    print("    (or they can just double-click 'start_worker.bat'!)")
    print("==================================================================\n")

    coordinator = SwarmCoordinator(port=args.port)
    coordinator.start_discovery()

    if args.model:
        print(f"[*] Auto-launching cluster with model: {args.model}")
        coordinator.launch_llama_cluster(args.model)

    try:
        run_web_server(coordinator, host="0.0.0.0", port=args.port)
    except KeyboardInterrupt:
        print("\n[*] Shutting down Coordinator...")
        coordinator.stop()
        print("[+] Cluster stopped.")

if __name__ == "__main__":
    main()
