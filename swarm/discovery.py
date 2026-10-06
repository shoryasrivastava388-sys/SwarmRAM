import socket
import json
import threading
import time
from typing import Callable, Optional
from swarm.config import DEFAULT_DISCOVERY_PORT

MAGIC_HEADER = "SWARMRAM_DISCOVERY_V1"

class DiscoveryBroadcaster:
    """
    Runs in the background on the Coordinator.
    Broadcasts UDP announcements so Workers on the same Wi-Fi/LAN can find the master automatically.
    """
    def __init__(self, coordinator_ip: str, coordinator_port: int, interval: float = 2.0):
        self.coordinator_ip = coordinator_ip
        self.coordinator_port = coordinator_port
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _broadcast_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1.0)

        payload = {
            "magic": MAGIC_HEADER,
            "type": "COORDINATOR_BEACON",
            "coordinator_ip": self.coordinator_ip,
            "coordinator_port": self.coordinator_port,
            "timestamp": time.time()
        }
        message = json.dumps(payload).encode("utf-8")

        while self._running:
            try:
                sock.sendto(message, ("<broadcast>", DEFAULT_DISCOVERY_PORT))
            except Exception:
                # If <broadcast> fails on some interfaces, fallback to 255.255.255.255
                try:
                    sock.sendto(message, ("255.255.255.255", DEFAULT_DISCOVERY_PORT))
                except Exception:
                    pass
            time.sleep(self.interval)
        sock.close()


class DiscoveryListener:
    """
    Runs on Worker nodes to automatically locate the Coordinator on the local network.
    """
    def __init__(self, timeout: float = 6.0):
        self.timeout = timeout

    def scan_for_coordinator(self) -> Optional[dict]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(self.timeout)

        try:
            sock.bind(("", DEFAULT_DISCOVERY_PORT))
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    data, addr = sock.recvfrom(2048)
                    payload = json.loads(data.decode("utf-8"))
                    if payload.get("magic") == MAGIC_HEADER and payload.get("type") == "COORDINATOR_BEACON":
                        # If coordinator advertised 127.0.0.1 or 0.0.0.0, use sender's IP
                        reported_ip = payload.get("coordinator_ip")
                        if reported_ip in ("127.0.0.1", "0.0.0.0"):
                            payload["coordinator_ip"] = addr[0]
                        return payload
                except (socket.timeout, json.JSONDecodeError):
                    continue
        except Exception as e:
            # UDP bind might fail if port is occupied
            return None
        finally:
            sock.close()
        return None
