import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = PROJECT_ROOT / "bin"
MODELS_DIR = PROJECT_ROOT / "models"
WEB_DIR = PROJECT_ROOT / "swarm" / "web"

# Networking & Ports
DEFAULT_DISCOVERY_PORT = 53530  # UDP broadcast port for LAN discovery
DEFAULT_COORDINATOR_PORT = 8080  # HTTP UI & API port
DEFAULT_RPC_PORT = 50052        # Default llama.cpp RPC server port

# Memory Defaults (in Megabytes)
# Always reserve at least 1200 MB so the host OS / school browser does not freeze
DEFAULT_OS_RESERVE_MB = 1200
DEFAULT_MIN_CONTRIBUTION_MB = 512

# Popular lightweight models suited for distributed 4GB clusters
RECOMMENDED_MODELS = {
    "llama-3.2-1b": {
        "name": "Llama 3.2 (1B Instruct, Q4_K_M)",
        "size_mb": 850,
        "recommended_cluster_ram_mb": 1500,
        "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    },
    "llama-3.2-3b": {
        "name": "Llama 3.2 (3B Instruct, Q4_K_M)",
        "size_mb": 2020,
        "recommended_cluster_ram_mb": 3500,
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    },
    "qwen2.5-3b": {
        "name": "Qwen 2.5 (3B Instruct, Q4_K_M)",
        "size_mb": 2150,
        "recommended_cluster_ram_mb": 3800,
        "url": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
    },
    "mistral-7b": {
        "name": "Mistral 7B (v0.3 Instruct, Q4_K_M)",
        "size_mb": 4370,
        "recommended_cluster_ram_mb": 6500,
        "url": "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
    }
}
