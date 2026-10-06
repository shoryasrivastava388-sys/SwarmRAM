# SwarmRAM

Pool the RAM from multiple computers on the same Wi-Fi and use them together to run AI models — including serious coding models like Qwen 2.5 Coder and DeepSeek.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![No pip required](https://img.shields.io/badge/dependencies-none%20required-brightgreen)](#)

---

## The Problem & The Idea

In my school and lab, almost every computer has only **4 GB of RAM**. If you try to run any good AI model on a 4GB computer, Windows either freezes or crashes with an Out-Of-Memory error.

Meanwhile, there are 20+ computers in the room doing nothing.

You cannot "merge raw RAM" like a giant USB stick because Wi-Fi latency is too slow for the operating system. But with **pipeline parallelism**, you can shard the AI model's layers across computers:

- Computer 1 (Your PC) runs Layers 1–8
- Computer 2 (Friend A) runs Layers 9–16
- Computer 3 (Friend B) runs Layers 17–24
- Computer 4 (Friend C) runs Layers 25–32

Each computer holds its slice of model weights in local RAM. When a prompt runs, only tiny activation tensors (~100 KB) are sent across the Wi-Fi.

**Result: 4 laptops with 4GB RAM become a 16GB AI supercomputer on school Wi-Fi.**

---

## 💻 Terminal CLI (Ollama-Style Commands)

You do **not** have to use a browser or website! SwarmRAM is designed to feel just like Ollama directly inside your terminal:

### 1. Check Connected Computers & Pooled RAM
```bash
swarm nodes
```
Prints a live terminal table showing every friend's PC, their IP, and total pooled memory.

### 2. See Available Models
```bash
swarm list
```
Instantly detects all models on your computer — including your local Ollama models (`deepseek-r1:8b`, `qwen2.5-coder:7b`, etc.) and any `.gguf` files.

### 3. Pull ANY Model (Zero Restrictions)
```bash
swarm pull hermes
# or
swarm pull qwen2.5-coder:14b
# or download direct HuggingFace GGUF links!
```

### 4. Run Interactive Chat in the Terminal
```bash
swarm run qwen2.5-coder:7b
# or
swarm run deepseek-r1:8b
# or
swarm run hermes
```
Drops you into an interactive terminal chat with live streaming:
```
==================================================================
  ⚡ SwarmRAM Terminal — qwen2.5-coder:7b (4.36 GB) ⚡
==================================================================
[*] Engine:   Shared RAM Cluster (7.2 GB Combined RAM)
[*] Sharding: Model weights partitioned across network peers
------------------------------------------------------------------
Type your message below. Type '/exit' or 'exit' to quit.
==================================================================

>>> Explain binary search in 1 sentence
Binary search is an efficient algorithm that finds a target in a sorted array by repeatedly dividing the search space in half.

>>> 
```

### 5. How Friends Join from Terminal
```bash
swarm join 192.168.1.18:8080
```
Pops up the interactive RAM chooser menu right in their shell!

---

## What Exact Steps Do Your Friends Take?

Friends don't need to know anything about coding. Here is their exact 30-second walkthrough:

1. **Connect to the same Wi-Fi** (or your phone's mobile hotspot).
2. **Copy the SwarmRAM folder** onto their laptop.
3. **Double-click `start_worker.bat`** (or run `python run_worker.py`).
4. **Choose how much RAM to share**:  
   A menu will pop up showing their actual free RAM:
   - `[1] Recommended`: Safely shares ~2 GB, keeping 1.2 GB+ free so Windows and Chrome stay 100% smooth.
   - `[2] Maximum`: Donates almost all free RAM for max cluster power.
   - `[3] Minimum`: Donates only 512 MB if they're actively gaming or doing homework.
   - `[4] Custom`: Type any amount in MB.
5. **Enter Coordinator IP**: If auto-discovery doesn't find your PC, they type your IP (shown on your screen).

That's it! They will see:
```
[+] Worker is ACTIVE and sharing 2.2 GB RAM with the cluster!
```

---

## How Does It Actually Use Their PC?

Your friends will probably ask: *"Is this going to slow down my laptop or mess up my files?"*

Here is exactly what happens on their machine:
- **No permanent files created**: The model weights exist in RAM only.
- **Safe RAM buffer**: It always reserves at least 1.2 GB of RAM exclusively for Windows, so their laptop doesn't freeze or lag.
- **CPU usage only during generation**: When nobody is chatting with the AI, CPU usage is **0%**. When you ask a question, their CPU computes matrix multiplications for a couple of seconds, then goes right back to idle.
- **Instant shutdown**: The moment they press `Ctrl + C` or close the command window, all RAM is instantly freed back to their computer.

---

## Cluster Modes: Single Output vs. Shared Mesh

You can choose how the cluster operates:

### 1. Focused Mode (`--mode focused` - Default)
All connected friends funnel their RAM to **your computer**. Only you see the output and control the prompts. Best when you need the full power of everyone's laptops to run a heavy task on your screen.

### 2. Mesh Mode (`--mode mesh`)
The model is sharded across everyone, and the web interface (`http://<your-ip>:8080`) is open to **everyone on the Wi-Fi**.
- Friend A can type a prompt from their browser.
- The model computes across Your PC + Friend A + Friend B.
- Friend A gets the answer on their screen.
- Everyone contributes RAM, and everyone gets to use the AI!

---

## Models You Can Run (From Small to Claude-Level Coders)

You don't have to limit yourself to small 3B models. With 3 to 6 friends pooled together, you can run state-of-the-art coding assistants:

| Model | Tag | File Size | Recommended Cluster RAM | What It Can Do |
|---|---|---|---|---|
| **Llama 3.2 1B** | General | 850 MB | 1.5 GB | Fast chat on 1 computer |
| **Llama 3.2 3B** | General | 2.0 GB | 3.5 GB | Good general assistant (2 PCs) |
| **Mistral 7B** | General | 4.3 GB | 6.5 GB | Great reasoning & writing (2–3 PCs) |
| **Qwen 2.5 Coder 14B** | **Coding** | 8.5 GB | 11.0 GB | **Serious coding assistant** (3–4 PCs) |
| **DeepSeek Coder V2 Lite 16B** | **Coding** | 10.0 GB | 12.0 GB | **Multi-file coding & reasoning** (3–4 PCs) |
| **Codestral 22B by Mistral** | **Coding** | 13.0 GB | 16.0 GB | **Fast 32k context coding model** (4–5 PCs) |
| **Qwen 2.5 Coder 32B** | **Coding** | 20.0 GB | 24.0 GB | **Claude 3.5 / GPT-4o level code generation** (6–8 PCs) |
| **Llama 3.1 70B** | General | 40.0 GB | 48.0 GB | **Enterprise mega-model** across a whole computer lab (12–16 PCs) |

To run any model, download its `.gguf` file from [HuggingFace](https://huggingface.co) and put it into the `models/` folder.

---

## Quickstart

### Master Computer (You)
Double-click `start_coordinator.bat` or run:
```bash
python run_coordinator.py --mode focused
```
Then open `http://localhost:8080` in your browser.

### Friend Computers (Workers)
Double-click `start_worker.bat` or run:
```bash
python run_worker.py --coordinator <MASTER_IP>:8080
```

---

## School Wi-Fi Troubleshooting

- **School Wi-Fi has AP isolation (laptops can't ping each other)**:  
  Turn on a **Mobile Hotspot** on your phone. Have everyone connect to it. Local inference uses **zero mobile data**!
- **Windows Firewall popup**:  
  Click "Allow access" for Python, or run in PowerShell (Admin):
  ```powershell
  New-NetFirewallRule -DisplayName "SwarmRAM" -Direction Inbound -LocalPort 8080,50052,53530 -Protocol TCP -Action Allow
  ```

---

## License
MIT — feel free to use, modify, and build on it with your friends!
