# ⚡ SwarmRAM

> **Pool multiple low-spec computers (4GB RAM) over LAN/Wi-Fi to run large AI models together.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![llama.cpp: RPC](https://img.shields.io/badge/backend-llama.cpp%20RPC-orange.svg)](https://github.com/ggerganov/llama.cpp)
[![Zero Dependency](https://img.shields.io/badge/dependencies-Zero%20Mandatory%20Pip-green.svg)](#requirements)

---

## 📌 The Problem
Most school and university lab computers have only **4 GB of RAM**. 

Running a modern 7B or 8B parameter Large Language Model (LLM) requires **4.5 GB to 8 GB of memory**. When you try to run it on a single 4GB computer, the OS freezes or crashes with an Out-Of-Memory (OOM) error.

However:
- 1 Computer = 4 GB *(Cannot run 7B model)*
- **3 Friends combined = 12 GB RAM** *(Easily runs Llama-3, Mistral-7B, or Qwen-2.5!)*

**SwarmRAM** makes pooling your computers as simple as double-clicking a script on each friend's laptop.

---

## 🔬 How It Works: The Science

### Why you cannot "merge physical RAM directly"
Motherboard RAM transfers data at **30,000 to 60,000 MB/s** with **50 nanoseconds** latency. Local Wi-Fi runs at **10 to 50 MB/s** with **5 milliseconds** latency. 

If Windows tries to treat another computer's RAM as raw virtual memory over Wi-Fi, it runs **100,000× too slow** and locks up.

### How SwarmRAM Solves This: Neural Layer Sharding
Instead of transferring raw memory bytes, SwarmRAM partitions the **neural network layers** across computers using `llama.cpp` RPC:

```
[User Prompt]
      │
      ▼
┌──────────────┐   Activation Tensor (~100 KB)   ┌──────────────┐
│  Master PC   │ ──────────────────────────────► │  Friend 1 PC │
│ Layers 1 - 8 │                                 │ Layers 9-16  │
└──────────────┘                                 └──────────────┘
                                                        │
                                           Activation   │
                                           Tensor (~100 KB)
                                                        ▼
┌──────────────┐   Activation Tensor (~100 KB)   ┌──────────────┐
│  Final Token │ ◄────────────────────────────── │  Friend 2 PC │
│  Generation  │                                 │ Layers 17-24 │
└──────────────┘                                 └──────────────┘
```

1. Each computer loads only its slice of model weights (e.g. 1.2 GB) into RAM **once**.
2. During chat generation, only tiny **activation vectors (a few kilobytes)** are sent across the Wi-Fi.
3. This completely bypasses the network bandwidth bottleneck and runs smoothly on school Wi-Fi!

---

## 🚀 Quickstart Guide

### 1. Setup Coordinator (Your Computer)
Clone the repository:
```bash
git clone https://github.com/your-username/SwarmRAM.git
cd SwarmRAM
```

Start the coordinator:
```bash
# Windows (Double-click or run):
start_coordinator.bat

# Or via Python CLI:
python run_coordinator.py
```
The terminal will display your **Local LAN IP** (e.g., `192.168.1.18:8080`).

---

### 2. Connect Workers (Your Friends' Computers)
Send this folder to your friends on the same Wi-Fi. On their computers:
```bash
# Windows (Double-click):
start_worker.bat

# Or via Python CLI:
python run_worker.py --coordinator 192.168.1.18:8080
```
- The worker automatically detects total system RAM and calculates a safe contribution (leaving at least 1.2 GB for Windows so their laptop never lags).
- As each friend joins, the master terminal and web dashboard will notify:
  ```
  [+] Worker joined cluster: Aryan-Laptop (192.168.1.25) contributing 2.4 GB RAM
  [*] Total Pooled Cluster Memory: 8.8 GB
  ```

---

### 3. Open the Web Dashboard
On the Master computer, open your browser:
```
http://localhost:8080
```
- View all connected friend nodes in real time.
- See total pooled cluster memory.
- Chat with the distributed model and watch tokens stream live!

---

## 🏫 School Wi-Fi & Firewall Troubleshooting

School networks often have security policies that restrict device communication. Here is how to bypass common restrictions:

| Situation | Solution |
| :--- | :--- |
| **School Wi-Fi has Client Isolation (devices can't see each other)** | Turn on a **Mobile Hotspot** on your phone or laptop. Have friends connect to your hotspot. No internet is needed for local inference! |
| **Windows Firewall blocks incoming ports** | When prompted, click **Allow Access** for Python, or run in PowerShell (Admin): `New-NetFirewallRule -DisplayName "SwarmRAM" -Direction Inbound -LocalPort 8080,50052,53530 -Protocol TCP -Action Allow` |
| **Auto-discovery UDP beacon blocked** | Have friends enter the coordinator IP manually when prompted by `run_worker.py`. |

---

## 📦 Recommended Models for 4GB Clusters

Place `.gguf` quantized models inside the `models/` folder:

| Model | Quantization | Size | Min. Total Cluster RAM | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **Llama 3.2 1B** | Q4_K_M | 850 MB | 1.5 GB | Single 4GB PC or 2 peers |
| **Llama 3.2 3B** | Q4_K_M | 2.0 GB | 3.5 GB | 2 friends pooled |
| **Qwen 2.5 3B** | Q4_K_M | 2.1 GB | 3.8 GB | 2 friends pooled |
| **Mistral 7B** | Q4_K_M | 4.3 GB | 6.5 GB | 3–4 friends pooled |

---

## 🛠️ Architecture Overview

- **`swarm/discovery.py`**: UDP broadcast beacon on port `53530` for zero-configuration LAN discovery.
- **`swarm/system_info.py`**: Safe memory budget calculation (works with zero pip dependencies on Windows, Linux, and macOS).
- **`swarm/binaries.py`**: Auto-detects and caches `rpc-server` and `llama-server` binaries.
- **`swarm/coordinator.py`**: Aggregates node specifications, generates `--rpc` command flags, and manages cluster state.
- **`swarm/worker.py`**: Runs `rpc-server`, handles heartbeats, and provides graceful cleanup on shutdown.
- **`swarm/web/`**: Built-in HTTP dashboard and chat interface.

---

## 📜 License
Distributed under the [MIT License](LICENSE).
