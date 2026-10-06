import os
import sys
import argparse
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Ensure UTF-8 / safe output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from swarm.config import DEFAULT_COORDINATOR_PORT
from swarm.model_resolver import list_all_available_models, resolve_model, pull_model_cli
from swarm.system_info import get_local_ip

COORDINATOR_URL = f"http://127.0.0.1:{DEFAULT_COORDINATOR_PORT}"

def get_cluster_stats():
    try:
        req = urllib.request.urlopen(f"{COORDINATOR_URL}/api/stats", timeout=2)
        return json.loads(req.read().decode("utf-8"))
    except Exception:
        return None

def cmd_list(args):
    models = list_all_available_models()
    if not models:
        print("[*] No models found yet.")
        print("[*] Pull any model with: swarm pull <model-name>")
        print("    Example: swarm pull hermes  or  swarm pull qwen2.5-coder:7b")
        return

    print(f"\nAvailable Models for SwarmRAM ({len(models)} found):")
    print(f"{'NAME':<28} {'SOURCE':<10} {'SIZE':<10} {'PATH'}")
    print("-" * 80)
    for m in models:
        print(f"{m['name']:<28} {m['source']:<10} {str(m['size_gb']) + ' GB':<10} {m['path']}")
    print("-" * 80)
    print("Run any model across your pooled RAM with: swarm run <name>\n")

def cmd_nodes(args):
    stats = get_cluster_stats()
    if not stats:
        print(f"[!] Coordinator not detected on {COORDINATOR_URL}.")
        print("[*] Start the cluster with: swarm serve  (or start_coordinator.bat)")
        return

    coord = stats["coordinator"]
    workers = stats["workers"]
    total_ram = stats["total_pooled_ram_gb"]

    print("\n==================================================================")
    print(f"       ⚡ SwarmRAM Cluster Nodes — Total Pooled RAM: {total_ram} GB ⚡      ")
    print("==================================================================")
    print(f"{'NODE':<26} {'ROLE':<10} {'IP:PORT':<20} {'DONATED RAM':<12} {'STATUS'}")
    print("-" * 78)
    print(f"{coord['hostname']:<26} {'Master':<10} {coord['ip'] + ':8080':<20} {str(round(coord['contributed_ram_mb']/1024, 1)) + ' GB':<12} ONLINE")
    for w in workers:
        addr = f"{w['worker_ip']}:{w['rpc_port']}"
        status = "ONLINE" if w["online"] else "OFFLINE"
        print(f"{w['hostname']:<26} {'Worker':<10} {addr:<20} {str(round(w['allocated_ram_mb']/1024, 1)) + ' GB':<12} {status}")
    print("-" * 78)
    print(f"Active Nodes: {stats['total_nodes']} | Mode: {stats.get('mode', 'focused').upper()}\n")

def cmd_pull(args):
    if not args.model:
        print("[!] Please specify a model to pull. Example: swarm pull hermes")
        return
    pull_model_cli(args.model)

def cmd_join(args):
    from swarm.worker import SwarmWorker
    from swarm.config import DEFAULT_RPC_PORT
    worker = SwarmWorker(
        coordinator_addr=args.coordinator,
        rpc_port=args.port or DEFAULT_RPC_PORT,
        ram_mb=args.ram,
        interactive=True
    )
    worker.start()

def cmd_serve(args):
    from run_coordinator import main as coord_main
    coord_main()

def cmd_run(args):
    if not args.model:
        print("[!] Please specify a model to run. Example: swarm run qwen2.5-coder:7b")
        return

    model_info = resolve_model(args.model)
    if not model_info:
        print(f"[!] Model '{args.model}' not found on this computer.")
        print(f"[*] You can pull it automatically with:")
        print(f"    swarm pull {args.model}")
        return

    stats = get_cluster_stats()
    node_str = f"{stats['total_nodes']} Nodes Online ({stats['total_pooled_ram_gb']} GB Pooled RAM)" if stats else "Single Node (Coordinator offline)"

    print("\n==================================================================")
    print(f"  ⚡ SwarmRAM Terminal — {model_info['name']} ({model_info['size_gb']} GB) ⚡")
    print("==================================================================")
    print(f"[*] Engine:      Shared RAM Cluster")
    print(f"[*] Cluster:     {node_str}")
    print(f"[*] Weights:     {model_info['path']}")
    print("------------------------------------------------------------------")
    print("Type your message below. Type '/exit' or 'exit' to quit.")
    print("==================================================================\n")

    while True:
        try:
            prompt = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting SwarmRAM...")
            break

        if not prompt:
            continue
        if prompt.lower() in ("/exit", "exit", "/bye", "quit"):
            print("Bye!")
            break

        # Submit to cluster API
        print()
        sys.stdout.write("AI: ")
        sys.stdout.flush()

        try:
            payload = json.dumps({"prompt": prompt}).encode("utf-8")
            req = urllib.request.Request(
                f"{COORDINATOR_URL}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data.get("reply", "")
                
                # Strip HTML tags if any returned from web server
                import re
                clean_text = re.sub("<[^<]+?>", "", reply)
                # Stream out clean text
                for char in clean_text:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(0.003)
                print("\n")
        except Exception as e:
            print(f"\n[!] Cluster response error: {e}\n")

def main():
    parser = argparse.ArgumentParser(
        prog="swarm",
        description="SwarmRAM — Ollama-style Terminal CLI for Distributed Memory AI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # swarm list
    subparsers.add_parser("list", help="List all available models (local + Ollama)")

    # swarm nodes / status
    subparsers.add_parser("nodes", help="List connected computers and pooled RAM")
    subparsers.add_parser("status", help="Show cluster status")

    # swarm pull <model>
    pull_p = subparsers.add_parser("pull", help="Pull any model (via Ollama or HuggingFace URL)")
    pull_p.add_argument("model", type=str, help="Model name (e.g. hermes, llama3, qwen2.5-coder:14b)")

    # swarm run <model>
    run_p = subparsers.add_parser("run", help="Run interactive terminal chat with shared RAM")
    run_p.add_argument("model", type=str, help="Model name to run")

    # swarm join <coordinator>
    join_p = subparsers.add_parser("join", help="Join a cluster as a worker from terminal")
    join_p.add_argument("coordinator", type=str, nargs="?", default=None, help="Coordinator IP:PORT")
    join_p.add_argument("--port", "-p", type=int, default=None, help="RPC port")
    join_p.add_argument("--ram", "-m", type=int, default=None, help="RAM in MB to donate")

    # swarm serve
    subparsers.add_parser("serve", help="Start the cluster coordinator daemon")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command in ("nodes", "status"):
        cmd_nodes(args)
    elif args.command == "pull":
        cmd_pull(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "join":
        cmd_join(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
