# SwarmRAM

Pool the RAM from multiple computers on the same Wi-Fi and use them together to run large AI models — without buying new hardware.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![No pip required](https://img.shields.io/badge/dependencies-none%20required-brightgreen)](#)

---

## Why I built this

I'm in school and all the computers here have 4GB of RAM. Running even a small AI model on 4GB freezes the whole machine. But there are like 20+ computers in every lab sitting there doing nothing.

So I thought — what if I could combine the RAM from all of them?

Turns out you can't just merge RAM over Wi-Fi directly (the OS would lock up trying to page memory at Wi-Fi speeds). But you *can* split the AI model's layers across machines, so each computer only holds a chunk of the model. Small activation tensors (~100KB) pass between them, not gigabytes of raw memory. This is called pipeline parallelism and it's what this project does.

**3 friends × 4GB each = 12GB cluster. Enough to run Mistral 7B or Llama 3.**

---

## How it works

Each computer loads a slice of the model's neural network layers into its own local RAM once. When you type a prompt, it flows through the chain:

```
Your PC          Friend 1 PC       Friend 2 PC
[Layers 1-8] --> [Layers 9-16] --> [Layers 17-24] --> output
     ^                ^                  ^
  ~1.2 GB RAM      ~1.2 GB RAM       ~1.2 GB RAM
```

Only tiny activation tensors (~100KB) travel across the network between steps. The heavy model weights stay local on each machine and never move. This is why it works fine on regular school Wi-Fi.

---

## Getting started

### You (the coordinator / master node)

1. Clone the repo:
   ```bash
   git clone https://github.com/shoryasrivastava388-sys/SwarmRAM.git
   cd SwarmRAM
   ```

2. Double-click `start_coordinator.bat`, or run:
   ```bash
   python run_coordinator.py
   ```

3. Your terminal will show your local IP like `192.168.1.18`. Share that with your friends.

4. Open `http://localhost:8080` in a browser — that's your live cluster dashboard.

### Your friends (worker nodes)

They just need to clone the repo and double-click `start_worker.bat`. It will ask for your IP and connect automatically. Or they can run:

```bash
python run_worker.py --coordinator 192.168.1.18:8080
```

The worker figures out how much RAM is safe to share (it always keeps at least 1.2GB free so their laptop doesn't lag) and joins the cluster. Your dashboard will update in real time.

### Running a model

Put any `.gguf` model file in the `models/` folder, then pass it on startup:

```bash
python run_coordinator.py --model mistral-7b-instruct-q4_k_m.gguf
```

The system will automatically spread the model layers across all connected nodes using the [llama.cpp RPC backend](https://github.com/ggerganov/llama.cpp).

---

## Models that work well on 4GB clusters

| Model | File size | Min total cluster RAM | Notes |
|---|---|---|---|
| Llama 3.2 1B Q4_K_M | 850 MB | 1.5 GB | Works solo on a single 4GB PC |
| Llama 3.2 3B Q4_K_M | 2.0 GB | 3.5 GB | 2 people |
| Qwen 2.5 3B Q4_K_M | 2.1 GB | 3.8 GB | 2 people |
| Mistral 7B Q4_K_M | 4.3 GB | 6.5 GB | 3-4 people |

Download `.gguf` files from [HuggingFace](https://huggingface.co) and drop them in `models/`.

---

## It's not working — common fixes

**"My friends can't connect"**  
School Wi-Fi often has AP isolation which blocks devices from talking to each other. Fix: turn on a mobile hotspot on your phone, have everyone connect to that instead. No internet required for local inference.

**Windows Firewall prompt**  
When you run the coordinator for the first time, Windows Firewall will ask you to allow Python. Click "Allow access". If you missed it, run this in PowerShell as admin:
```powershell
New-NetFirewallRule -DisplayName "SwarmRAM" -Direction Inbound -LocalPort 8080,50052,53530 -Protocol TCP -Action Allow
```

**Auto-discovery isn't finding the coordinator**  
UDP broadcast is sometimes blocked. That's fine — when the worker starts, just type the coordinator IP manually when it asks.

**Python not found**  
Download Python from [python.org](https://python.org). Make sure to check "Add Python to PATH" during install.

---

## File structure

```
SwarmRAM/
├── run_coordinator.py      # start this on YOUR computer
├── run_worker.py           # friends run this
├── start_coordinator.bat   # Windows double-click shortcut
├── start_worker.bat        # Windows double-click shortcut for friends
├── models/                 # drop .gguf model files here
├── swarm/
│   ├── coordinator.py      # tracks nodes, RAM pool, cluster state
│   ├── worker.py           # runs rpc-server, sends heartbeats
│   ├── discovery.py        # LAN auto-discovery via UDP broadcast
│   ├── system_info.py      # reads system RAM, calculates safe budget
│   ├── binaries.py         # finds or downloads llama.cpp binaries
│   ├── config.py           # ports, model list, defaults
│   └── web/
│       ├── index.html      # dashboard UI
│       └── server.py       # lightweight HTTP server (no Flask needed)
```

---

## Requirements

- Python 3.10 or newer (no mandatory pip packages)
- All computers on the same Wi-Fi or LAN (or same mobile hotspot)
- `psutil` is optional but makes RAM readings slightly more accurate

---

## License

MIT — use it however you want.
