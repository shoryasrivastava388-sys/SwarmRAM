import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from swarm.config import DEFAULT_RPC_PORT
from swarm.worker import SwarmWorker

def main():
    parser = argparse.ArgumentParser(description="SwarmRAM Worker Node (Share your RAM with friends)")
    parser.add_argument("--coordinator", "-c", type=str, default=None, help="Coordinator address (e.g. 192.168.1.18:8080)")
    parser.add_argument("--port", "-p", type=int, default=DEFAULT_RPC_PORT, help=f"Port for RPC worker (default: {DEFAULT_RPC_PORT})")
    parser.add_argument("--ram", "-m", type=int, default=None, help="Specific amount of RAM to donate in Megabytes (skips menu)")
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Skip the RAM selection menu and automatically share the safe recommended amount"
    )
    args = parser.parse_args()

    worker = SwarmWorker(
        coordinator_addr=args.coordinator,
        rpc_port=args.port,
        ram_mb=args.ram,
        interactive=not args.no_interactive
    )
    worker.start()

if __name__ == "__main__":
    main()
