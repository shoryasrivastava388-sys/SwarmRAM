import time
import subprocess
import threading
import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

from swarm.config import (
    DEFAULT_COORDINATOR_PORT,
    MODELS_DIR,
    BIN_DIR,
    RECOMMENDED_MODELS
)
from swarm.system_info import get_full_node_specs, get_local_ip
from swarm.binaries import find_binary, download_and_extract_binaries
from swarm.discovery import DiscoveryBroadcaster

class WorkerNode:
    def __init__(self, node_id: str, hostname: str, worker_ip: str, rpc_port: int, allocated_ram_mb: int, total_ram_mb: int, is_simulation: bool = False):
        self.node_id = node_id
        self.hostname = hostname
        self.worker_ip = worker_ip
        self.rpc_port = rpc_port
        self.allocated_ram_mb = allocated_ram_mb
        self.total_ram_mb = total_ram_mb
        self.is_simulation = is_simulation
        self.last_heartbeat = time.time()

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "worker_ip": self.worker_ip,
            "rpc_port": self.rpc_port,
            "allocated_ram_mb": self.allocated_ram_mb,
            "total_ram_mb": self.total_ram_mb,
            "is_simulation": self.is_simulation,
            "online": (time.time() - self.last_heartbeat) < 15.0
        }

class SwarmCoordinator:
    def __init__(self, port: int = DEFAULT_COORDINATOR_PORT):
        self.port = port
        self.local_specs = get_full_node_specs()
        self.workers: Dict[str, WorkerNode] = {}
        self.broadcaster: Optional[DiscoveryBroadcaster] = None
        self.llama_process: Optional[subprocess.Popen] = None
        self.active_model_path: Optional[str] = None
        self.is_inferencing = False
        self._lock = threading.Lock()

    def start_discovery(self):
        local_ip = get_local_ip()
        self.broadcaster = DiscoveryBroadcaster(local_ip, self.port)
        self.broadcaster.start()
        print(f"[*] Discovery Broadcaster broadcasting on LAN from {local_ip}:{self.port}")

    def register_worker(self, data: dict) -> bool:
        with self._lock:
            key = f"{data['worker_ip']}:{data['rpc_port']}"
            node = WorkerNode(
                node_id=data.get("node_id", key),
                hostname=data.get("hostname", data["worker_ip"]),
                worker_ip=data["worker_ip"],
                rpc_port=data.get("rpc_port", 50052),
                allocated_ram_mb=data.get("allocated_ram_mb", 2048),
                total_ram_mb=data.get("total_ram_mb", 4096),
                is_simulation=data.get("is_simulation", False)
            )
            self.workers[key] = node
            print(f"[+] Worker joined cluster: {node.hostname} ({node.worker_ip}) contributing {node.allocated_ram_mb} MB RAM")
        return True

    def record_heartbeat(self, data: dict):
        key = f"{data['worker_ip']}:{data.get('rpc_port', 50052)}"
        with self._lock:
            if key in self.workers:
                self.workers[key].last_heartbeat = time.time()

    def get_cluster_stats(self) -> dict:
        with self._lock:
            active_workers = [w.to_dict() for w in self.workers.values() if w.to_dict()["online"]]
            workers_ram = sum(w["allocated_ram_mb"] for w in active_workers)
            coordinator_ram = self.local_specs["contributed_ram_mb"]
            total_pooled = coordinator_ram + workers_ram

            return {
                "coordinator": self.local_specs,
                "workers": active_workers,
                "total_nodes": len(active_workers) + 1,
                "coordinator_ram_mb": coordinator_ram,
                "workers_ram_mb": workers_ram,
                "total_pooled_ram_mb": total_pooled,
                "total_pooled_ram_gb": round(total_pooled / 1024.0, 2),
                "is_inferencing": self.is_inferencing,
                "active_model": self.active_model_path
            }

    def get_rpc_arg_string(self) -> str:
        """
        Builds the comma-separated --rpc argument list for llama.cpp:
        e.g. 192.168.1.12:50052,192.168.1.15:50052
        """
        with self._lock:
            active = [f"{w.worker_ip}:{w.rpc_port}" for w in self.workers.values() if w.to_dict()["online"]]
            return ",".join(active)

    def list_available_models(self) -> List[dict]:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        found = []
        for file in MODELS_DIR.glob("*.gguf"):
            size_mb = int(file.stat().st_size / (1024 * 1024))
            found.append({
                "filename": file.name,
                "path": str(file),
                "size_mb": size_mb,
                "size_gb": round(size_mb / 1024.0, 2)
            })
        return found

    def launch_llama_cluster(self, model_filename: str) -> bool:
        """
        Launches the master llama-server instance connected to all worker RPC nodes.
        """
        model_path = MODELS_DIR / model_filename
        if not model_path.is_file():
            print(f"[-] Model file not found: {model_path}")
            return False

        binary = find_binary("llama_server")
        if not binary:
            print("[!] llama-server binary not found. Please download binaries first.")
            return False

        rpc_targets = self.get_rpc_arg_string()
        cmd = [
            str(binary),
            "-m", str(model_path),
            "--host", "127.0.0.1",
            "--port", "8081",
            "-c", "2048",
        ]
        if rpc_targets:
            cmd.extend(["--rpc", rpc_targets])
            print(f"[*] Pooling RAM across RPC endpoints: {rpc_targets}")
        else:
            print("[*] No remote workers connected; running entirely on local RAM.")

        print(f"[*] Executing llama-server: {' '.join(cmd)}")
        try:
            self.llama_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            self.active_model_path = model_filename
            self.is_inferencing = True

            def log_llama():
                if self.llama_process and self.llama_process.stdout:
                    for line in iter(self.llama_process.stdout.readline, ''):
                        if line:
                            print(f"[llama-cluster] {line.strip()}")
            threading.Thread(target=log_llama, daemon=True).start()
            return True
        except Exception as e:
            print(f"[-] Failed to launch llama-server: {e}")
            return False

    def stop(self):
        if self.broadcaster:
            self.broadcaster.stop()
        if self.llama_process:
            try:
                self.llama_process.terminate()
            except Exception:
                pass
