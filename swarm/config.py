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

# Cluster Operational Modes
CLUSTER_MODES = {
    "focused": {
        "name": "Focused Mode",
        "description": "All worker RAM is funneled to the coordinator. The coordinator PC controls the model and displays output. Ideal when one person needs maximum computing power."
    },
    "mesh": {
        "name": "Mesh / Shared Mode",
        "description": "The AI model is sharded across all connected nodes, and ANY connected computer can open the web UI and run prompts. Everyone pools their RAM and everyone gets to use the AI."
    }
}

# Catalog of Models (from lightweight 1B up to serious coding assistants like Claude Code)
RECOMMENDED_MODELS = {
    # Small / Fast Models (1-2 PCs)
    "llama-3.2-1b": {
        "name": "Llama 3.2 (1B Instruct, Q4_K_M)",
        "size_mb": 850,
        "recommended_cluster_ram_mb": 1500,
        "tag": "general",
        "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    },
    "llama-3.2-3b": {
        "name": "Llama 3.2 (3B Instruct, Q4_K_M)",
        "size_mb": 2020,
        "recommended_cluster_ram_mb": 3500,
        "tag": "general",
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    },
    "qwen2.5-3b": {
        "name": "Qwen 2.5 (3B Instruct, Q4_K_M)",
        "size_mb": 2150,
        "recommended_cluster_ram_mb": 3800,
        "tag": "general",
        "url": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
    },
    "mistral-7b": {
        "name": "Mistral 7B (v0.3 Instruct, Q4_K_M)",
        "size_mb": 4370,
        "recommended_cluster_ram_mb": 6500,
        "tag": "general",
        "url": "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
    },
    "mistral-nemo-12b": {
        "name": "Mistral Nemo (12B Instruct, Q4_K_M)",
        "size_mb": 7500,
        "recommended_cluster_ram_mb": 10000,
        "tag": "general",
        "url": "https://huggingface.co/bartowski/Mistral-Nemo-Instruct-2407-GGUF/resolve/main/Mistral-Nemo-Instruct-2407-Q4_K_M.gguf"
    },

    # Serious Coding Models (Claude Code / Copilot equivalents)
    "qwen2.5-coder-14b": {
        "name": "Qwen 2.5 Coder (14B Instruct, Q4_K_M)",
        "size_mb": 8500,
        "recommended_cluster_ram_mb": 11000,
        "tag": "coding",
        "url": "https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF/resolve/main/qwen2.5-coder-14b-instruct-q4_k_m.gguf"
    },
    "deepseek-coder-v2-lite-16b": {
        "name": "DeepSeek Coder V2 Lite (16B MoE, Q4_K_M)",
        "size_mb": 10000,
        "recommended_cluster_ram_mb": 12000,
        "tag": "coding",
        "url": "https://huggingface.co/bartowski/DeepSeek-Coder-V2-Lite-Instruct-GGUF/resolve/main/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf"
    },
    "codestral-22b": {
        "name": "Codestral (22B by Mistral, Q4_K_M)",
        "size_mb": 13000,
        "recommended_cluster_ram_mb": 16000,
        "tag": "coding",
        "url": "https://huggingface.co/bartowski/Codestral-22B-v0.1-GGUF/resolve/main/Codestral-22B-v0.1-Q4_K_M.gguf"
    },
    "qwen2.5-coder-32b": {
        "name": "Qwen 2.5 Coder (32B Instruct, Q4_K_M)",
        "size_mb": 20000,
        "recommended_cluster_ram_mb": 24000,
        "tag": "coding",
        "url": "https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct-GGUF/resolve/main/qwen2.5-coder-32b-instruct-q4_k_m.gguf"
    },

    # Full Lab Mega-Model (Entire Classroom: 12-16 PCs)
    "llama-3.1-70b": {
        "name": "Llama 3.1 (70B Instruct, Q4_K_M)",
        "size_mb": 40000,
        "recommended_cluster_ram_mb": 48000,
        "tag": "general",
        "url": "https://huggingface.co/bartowski/Meta-Llama-3.1-70B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf"
    }
}
