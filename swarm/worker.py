import sys
import time
import json
import urllib.request
import urllib.error
import subprocess
import threading
import signal
from pathlib import Path
from typing import Optional

from swarm.config import DEFAULT_RPC_PORT, DEFAULT_COORDINATOR_PORT
from swarm.system_info import get_full_node_specs, calculate_safe_ram_contribution, get_local_ip
from swarm.discovery import DiscoveryListener
from swarm.binaries import find_binary, download_and_extract_binaries

class SwarmWorker:
    def __init__(self, coordinator_addr: Optional[str] = None, rpc_port: int = DEFAULT_RPC_PORT, ram_mb: Optional[int] = None):
        self.coordinator_addr = coordinator_addr
        self.rpc_port = rpc_port
        self.specs = get_full_node_specs()
        self.allocated_ram_mb = ram_mb if ram_mb else self.specs["contributed_ram_mb"]
        self.rpc_process: Optional[subprocess.Popen] = None
        self._running = False
        self._heartbeat_thread: Optional[threading.Thread] = None

    def discover_or_ask_coordinator(self):
        if self.coordinator_addr:
            return

        print("\n[*] Scanning local network for SwarmRAM Coordinator beacon...")
        listener = DiscoveryListener(timeout=4.0)
        found = listener.scan_for_coordinator()

        if found:
            ip = found.get("coordinator_ip")
            port = found.get("coordinator_port", DEFAULT_COORDINATOR_PORT)
            self.coordinator_addr = f"{ip}:{port}"
            print(f"[+] Auto-discovered Coordinator at {self.coordinator_addr}!")
        else:
            print("[!] Auto-discovery timed out (school Wi-Fi might block UDP broadcasts).")
            entered = input(f"[?] Enter Coordinator IP address: ").strip()
            if not entered:
                entered = f"127.0.0.1:{DEFAULT_COORDINATOR_PORT}"
            elif ":" not in entered:
                entered = f"{entered}:{DEFAULT_COORDINATOR_PORT}"
            self.coordinator_addr = entered

    def ensure_rpc_binary(self) -> Optional[Path]:
        binary = find_binary("rpc_server")
        if binary:
            return binary

        print("\n[!] 'rpc-server' binary not found locally.")
        choice = input("[?] Download pre-built llama.cpp binaries for Windows now? (Y/n): ").strip().lower()
        if choice in ("", "y", "yes"):
            success = download_and_extract_binaries()
            if success:
                return find_binary("rpc_server")
        return None

    def start_rpc_server(self, binary_path: Optional[Path]):
        if not binary_path:
            print("[*] Running in Mock/Simulated Worker mode (no native rpc-server binary).")
            return

        # llama.cpp rpc-server command syntax:
        # rpc-server -H 0.0.0.0 -p <port> -m <mem_mb>
        cmd = [
            str(binary_path),
            "-H", "0.0.0.0",
            "-p", str(self.rpc_port),
            "-m", str(self.allocated_ram_mb)
        ]
        print(f"[*] Launching RPC engine: {' '.join(cmd)}")
        try:
            self.rpc_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            # Background thread to log output
            def stream_logs():
                if self.rpc_process and self.rpc_process.stdout:
                    for line in iter(self.rpc_process.stdout.readline, ''):
                        if line:
                            print(f"[RPC-Worker] {line.strip()}")
            threading.Thread(target=stream_logs, daemon=True).start()
        except Exception as e:
            print(f"[-] Could not start rpc-server process: {e}")

    def register_with_coordinator(self) -> bool:
        url = f"http://{self.coordinator_addr}/api/register_worker"
        payload = {
            "node_id": self.specs["node_id"],
            "hostname": self.specs["hostname"],
            "worker_ip": get_local_ip(),
            "rpc_port": self.rpc_port,
            "allocated_ram_mb": self.allocated_ram_mb,
            "total_ram_mb": self.specs["total_ram_mb"],
            "available_ram_mb": self.specs["available_ram_mb"],
            "is_simulation": self.rpc_process is None
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode("utf-8"))
                if res.get("status") == "ok":
                    print(f"[+] Successfully joined SwarmRAM cluster at {self.coordinator_addr}!")
                    return True
        except Exception as e:
            print(f"[-] Failed to register with coordinator ({url}): {e}")
            return False
        return False

    def _heartbeat_loop(self):
        url = f"http://{self.coordinator_addr}/api/heartbeat"
        while self._running:
            time.sleep(3.0)
            try:
                payload = {
                    "node_id": self.specs["node_id"],
                    "worker_ip": get_local_ip(),
                    "rpc_port": self.rpc_port
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    pass
            except Exception:
                pass

    def start(self):
        self._running = True
        print("==================================================")
        print("         SwarmRAM - Worker Node Daemon            ")
        print("==================================================")
        print(f"[*] Node Name:      {self.specs['node_id']}")
        print(f"[*] System Total:   {self.specs['total_ram_mb']} MB RAM")
        print(f"[*] Donating RAM:   {self.allocated_ram_mb} MB to Cluster")
        print(f"[*] RPC Port:       {self.rpc_port}")

        self.discover_or_ask_coordinator()
        binary = self.ensure_rpc_binary()
        self.start_rpc_server(binary)

        if not self.register_with_coordinator():
            print("[!] Could not connect to coordinator. Retrying every 5s in background...")

        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

        print("\n[+] Worker is ACTIVE and sharing RAM with the cluster!")
        print("[*] Press Ctrl+C at any time to disconnect cleanly.\n")

        try:
            while self._running:
                time.sleep(1.0)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("\n[*] Stopping SwarmRAM worker...")
        self._running = False
        if self.rpc_process:
            try:
                self.rpc_process.terminate()
                self.rpc_process.wait(timeout=3)
            except Exception:
                self.rpc_process.kill()
        print("[+] Disconnected cleanly. Thank you for sharing your RAM!")
