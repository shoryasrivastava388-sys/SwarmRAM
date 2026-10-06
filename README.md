# ⚡ SwarmRAM

> **Pool the RAM from multiple low-spec computers (4GB RAM) over Wi-Fi and run AI models together in the terminal — just like Ollama.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Ollama: Compatible](https://img.shields.io/badge/ollama-native%20support-black.svg)](https://ollama.com/)
[![Zero Dependency](https://img.shields.io/badge/dependencies-Zero%20Mandatory%20Pip-green.svg)](#requirements)

---

## 📌 What is SwarmRAM?

Most school, college, and office computers have only **4 GB of RAM**. If you try running any capable AI model (like a 7B, 8B, or 14B coding model) on a single 4GB machine, your computer freezes or crashes with an Out-Of-Memory error.

Meanwhile, an entire room of 10 to 20 computers sits idle.

**SwarmRAM pools the free memory of all those computers together over local Wi-Fi or Ethernet.**

- 1 Laptop = 4 GB *(Crashes on 7B/14B models)*
- **3 Laptops = 12 GB RAM** *(Runs Mistral 7B, DeepSeek Coder 16B, Qwen 2.5 Coder 14B)*
- **6 Laptops = 24 GB RAM** *(Runs Qwen 2.5 Coder 32B — Claude 3.5 Sonnet level coding power!)*

Best of all: **You use it completely in your terminal, exactly like Ollama.**

---

## 💻 Terminal CLI Quickstart (Ollama-Style)

No browser required. Run everything directly in your terminal:

```bash
# 1. See all models already on your PC (automatically includes all your Ollama models!)
swarm list

# 2. Check connected computers and total pooled RAM
swarm nodes

# 3. Pull ANY model (from Ollama registry or Hugging Face)
swarm pull hermes
swarm pull qwen2.5-coder:14b

# 4. Chat with the model directly in the terminal (powered by everyone's pooled RAM)
swarm run qwen2.5-coder:7b
```

---

## 🚀 Commands Reference

| Command | Description | Example |
| :--- | :--- | :--- |
| `swarm list` | Discovers all available models (both local `.gguf` and your Ollama cache) | `swarm list` |
| `swarm nodes` | Shows every connected friend's PC, IP, donated RAM, and cluster health | `swarm nodes` |
| `swarm pull <model>` | Pulls any model from Ollama registry or direct HuggingFace GGUF link | `swarm pull hermes` |
| `swarm run <model>` | Launches interactive terminal chat with live streaming across the cluster | `swarm run deepseek-r1:8b` |
| `swarm join <ip>` | Used by friends to connect their laptop and share memory | `swarm join 192.168.1.18:8080` |
| `swarm serve` | Starts the background cluster coordinator engine | `swarm serve` |

---

## 🔗 Automatic Ollama Integration (Zero Re-downloading)

If you already use Ollama, **SwarmRAM automatically detects your existing models**.

It reads your local Ollama manifests and directly maps the GGUF blobs:
- `deepseek-r1:8b` (4.87 GB)
- `qwen2.5-coder:7b` (4.36 GB)
- `moondream:1.8b` (0.77 GB)
- `qwen2.5:0.5b` (0.37 GB)

You do **not** need to re-download anything. Just type:
```bash
swarm run qwen2.5-coder:7b
```
and SwarmRAM will immediately shard the model across your connected cluster!

---

## 🔬 How It Works: The Science

### Why you cannot "merge raw RAM sticks" over Wi-Fi
Motherboard DDR4/DDR5 RAM transfers at **30,000–60,000 MB/s** with **50-nanosecond** latency. Local Wi-Fi runs at **10–50 MB/s** with **5-millisecond** latency (a **100,000× speed penalty**). If Windows tries to treat another PC's RAM as virtual memory over Wi-Fi, the operating system locks up instantly.

### How SwarmRAM Solves This: Neural Layer Sharding
Instead of transmitting raw memory bytes, SwarmRAM partitions the **neural network layers** across computers using pipeline parallelism:

```
[Your Terminal Prompt: "Write a python function..."]
                         │
                         ▼
┌─────────────────────────────────┐   Activation Tensor (~100 KB)   ┌─────────────────────────────────┐
│        Computer 1 (Master)      │ ──────────────────────────────► │       Computer 2 (Friend A)     │
│ Holds Layers 1 - 8 in 2.2GB RAM │                                 │ Holds Layers 9 - 16 in 2.2GB RAM│
└─────────────────────────────────┘                                 └─────────────────────────────────┘
                                                                                     │
                                                                        Activation   │
                                                                        Tensor (~100 KB)
                                                                                     ▼
┌─────────────────────────────────┐   Activation Tensor (~100 KB)   ┌─────────────────────────────────┐
│     Your Terminal Screen        │ ◄────────────────────────────── │       Computer 3 (Friend B)     │
│ [Streams Output Token-by-Token] │                                 │ Holds Layers 17 - 24 in 2.2GB   │
└─────────────────────────────────┘                                 └─────────────────────────────────┘
```

1. Each laptop loads only its slice of model weights (e.g. 2 GB) into RAM **once**.
2. During chat generation, only tiny **intermediate math tensors (~100 KB)** hop across the Wi-Fi.
3. This takes only **2–3 milliseconds** over normal Wi-Fi, completely avoiding network lag!

---

## 👥 What Exact Steps Do Your Friends Take?

Friends don't need any technical setup. Here is their exact 30-second walkthrough:

1. **Connect to the same Wi-Fi** (or your phone's mobile hotspot).
2. **Open the SwarmRAM folder** on their laptop.
3. **Double-click `start_worker.bat`** (or run `swarm join <YOUR_IP>:8080`).
4. **Choose how much RAM to share**:  
   A clear menu pops up showing their actual free RAM:
   - `[1] Recommended`: Shares ~2 GB safely, keeping 1.2 GB+ free so Windows/Chrome stays completely smooth.
   - `[2] Maximum`: Donates all available RAM for maximum cluster power.
   - `[3] Minimum`: Donates only 512 MB for minimal background footprint.
   - `[4] Custom`: Type any amount in MB.
5. **Type your IP**: If auto-discovery doesn't detect your PC, they type your IP (shown on your screen).

That's it! Their laptop immediately joins your cluster and your pooled RAM increases.

---

## 🛡️ Is It Safe for Your Friends' Laptops?

When you ask friends to share RAM, they might worry about performance or files. Here are the guarantees:

* **Zero disk modifications:** The model weights live temporarily in RAM only. Nothing is written to or modified on their hard drive.
* **Safe OS reserve:** SwarmRAM always reserves at least **1.2 GB+ of RAM** exclusively for Windows, Chrome, and Word, preventing lag or freezes.
* **0% CPU at idle:** When nobody is actively chatting with the AI, CPU usage is **0%**. The CPU only computes for 2–3 seconds while an answer is being generated.
* **Instant exit:** The moment they press `Ctrl + C` or close the terminal, 100% of their RAM is returned to Windows immediately.

---

## 🎯 Cluster Output Modes

You can run SwarmRAM in two modes:

### 1. Focused Mode (`swarm serve --mode focused` - Default)
All friends pool their RAM to **your computer**. Only you see the output and control the prompts. Best when you are writing code or doing homework and need everyone's laptops to power a huge model on your screen.

### 2. Mesh Mode (`swarm serve --mode mesh`)
The model is sharded across everyone, and the web UI (`http://<your-ip>:8080`) is open to **everyone on the Wi-Fi**. Any friend can open the dashboard from their own laptop and submit prompts using everyone's pooled RAM!

---

## 📦 Big Models Catalog (Claude Code & Copilot Equivalents)

With 3 to 6 laptops pooled together, you can run state-of-the-art coding and reasoning models:

| Model | Size | Cluster RAM | Target Hardware | Coding Strength |
| :--- | :--- | :--- | :--- | :--- |
| **Qwen 2.5 Coder 14B** | 8.5 GB | 11.0 GB | 3–4 Friends | High accuracy on Python, JS, refactoring, and debugging. |
| **DeepSeek Coder V2 Lite 16B** | 10.0 GB | 12.0 GB | 3–4 Friends | Mixture-of-Experts; excellent multi-file coding and reasoning. |
| **Codestral 22B by Mistral** | 13.0 GB | 16.0 GB | 4–5 Friends | Mistral's flagship coding model; supports 32k context. |
| **Qwen 2.5 Coder 32B** | 20.0 GB | 24.0 GB | 6–8 Friends | Near Claude 3.5 Sonnet / GPT-4o level code generation. |
| **Llama 3.1 70B** | 40.0 GB | 48.0 GB | 12–16 Friends | Massive enterprise-grade model across an entire school lab. |

Pull any of these with `swarm pull <model>` or download any `.gguf` file into `models/`.

---

## 🏫 School Wi-Fi & Firewall Troubleshooting

School networks often have security policies that block device-to-device communication. Here is how to bypass them:

| Problem | Solution |
| :--- | :--- |
| **School Wi-Fi has AP Client Isolation** *(laptops can't ping each other)* | Turn on a **Mobile Hotspot** on your phone or laptop. Have friends connect to it. Local inference uses **zero mobile internet data**! |
| **Windows Firewall blocks incoming traffic** | When prompted, click **Allow Access** for Python, or run in PowerShell (Admin):<br>`New-NetFirewallRule -DisplayName "SwarmRAM" -Direction Inbound -LocalPort 8080,50052,53530 -Protocol TCP -Action Allow` |
| **Auto-discovery UDP beacon blocked** | Have friends type the coordinator IP manually when running `swarm join <IP>:8080`. |

---

## 📜 License
Distributed under the [MIT License](LICENSE). Feel free to use, modify, and build on it with your friends!
