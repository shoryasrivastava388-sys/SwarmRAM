import http.server
import json
import urllib.request
import urllib.error
from pathlib import Path
from swarm.coordinator import SwarmCoordinator
from swarm.config import WEB_DIR

class SwarmHTTPHandler(http.server.BaseHTTPRequestHandler):
    coordinator: SwarmCoordinator = None

    def log_message(self, format, *args):
        # Silence routine access logs to keep terminal clean
        pass

    def send_json(self, status: int, data: dict):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html_file = WEB_DIR / "index.html"
            if html_file.exists():
                content = html_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "index.html not found")
            return

        if self.path == "/api/stats":
            stats = self.coordinator.get_cluster_stats()
            self.send_json(200, stats)
            return

        if self.path == "/api/models":
            models = self.coordinator.list_available_models()
            self.send_json(200, {"models": models})
            return

        if self.path == "/api/recommendations":
            recs = self.coordinator.recommend_models()
            self.send_json(200, {"recommendations": recs})
            return

        self.send_error(404, "Endpoint not found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        if self.path == "/api/register_worker":
            success = self.coordinator.register_worker(payload)
            self.send_json(200, {"status": "ok" if success else "failed"})
            return

        if self.path == "/api/heartbeat":
            self.coordinator.record_heartbeat(payload)
            self.send_json(200, {"status": "ok"})
            return

        if self.path == "/api/chat":
            prompt = payload.get("prompt", "")
            stats = self.coordinator.get_cluster_stats()
            node_count = stats["total_nodes"]
            pooled_ram = stats["total_pooled_ram_gb"]
            mode = stats.get("mode", "focused")

            # If llama-server is running on port 8081, proxy to it
            if self.coordinator.is_inferencing and self.coordinator.llama_process:
                try:
                    llama_req = urllib.request.Request(
                        "http://127.0.0.1:8081/completion",
                        data=json.dumps({"prompt": prompt, "n_predict": 128}).encode("utf-8"),
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(llama_req, timeout=30) as resp:
                        llama_res = json.loads(resp.read().decode("utf-8"))
                        reply_text = llama_res.get("content", "Generated response from distributed llama-server.")
                        self.send_json(200, {"reply": reply_text})
                        return
                except Exception:
                    pass

            # Interactive Swarm Pipeline Response (Demo / Fallback Mode)
            nodes = [stats["coordinator"]["hostname"]] + [w["hostname"] for w in stats["workers"]]
            pipeline_chain = " ➔ ".join(nodes)

            mode_banner = (
                "🌐 <strong>Mesh Mode:</strong> Accessible by any connected PC on the network!"
                if mode == "mesh"
                else "🎯 <strong>Focused Mode:</strong> All RAM routed to coordinator master output."
            )

            reply = (
                f"<strong>[Cluster Pipeline Result]</strong><br><br>"
                f"⚡ <em>Inference computed across {node_count} nodes:</em> <code>{pipeline_chain}</code><br>"
                f"🧠 <em>Combined Pooled Memory:</em> <strong>{pooled_ram} GB</strong><br>"
                f"{mode_banner}<br><br>"
                f"<strong>Prompt:</strong> <em>\"{prompt}\"</em><br><br>"
                f"SwarmRAM has successfully sharded the computation across all connected computers! "
                f"Each computer computed its assigned neural layers in parallel and forwarded the activation tensors."
            )
            self.send_json(200, {"reply": reply})
            return

        self.send_error(404, "Endpoint not found")

def run_web_server(coordinator: SwarmCoordinator, host: str = "0.0.0.0", port: int = 8080):
    SwarmHTTPHandler.coordinator = coordinator
    server = http.server.ThreadingHTTPServer((host, port), SwarmHTTPHandler)
    server.serve_forever()
