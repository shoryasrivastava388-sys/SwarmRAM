import os
import sys
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional

from swarm.config import MODELS_DIR

def get_ollama_models() -> List[Dict]:
    """
    Discovers all models pulled via Ollama and extracts their GGUF blob paths.
    """
    manifest_base = Path(os.path.expanduser("~/.ollama/models/manifests/registry.ollama.ai/library"))
    if not manifest_base.exists():
        return []

    models = []
    try:
        for model_dir in manifest_base.iterdir():
            if model_dir.is_dir():
                for tag_file in model_dir.iterdir():
                    if tag_file.is_file():
                        tag = tag_file.name
                        model_name = f"{model_dir.name}:{tag}"
                        try:
                            with open(tag_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            for l in data.get("layers", []):
                                if "model" in l.get("mediaType", ""):
                                    digest = l["digest"].replace("sha256:", "sha256-")
                                    blob_path = Path(os.path.expanduser(f"~/.ollama/models/blobs/{digest}"))
                                    if blob_path.exists():
                                        size_bytes = blob_path.stat().st_size
                                        models.append({
                                            "name": model_name,
                                            "short_name": model_dir.name if tag == "latest" else model_name,
                                            "path": str(blob_path),
                                            "size_bytes": size_bytes,
                                            "size_gb": round(size_bytes / (1024**3), 2),
                                            "source": "ollama"
                                        })
                        except Exception:
                            pass
    except Exception:
        pass
    return models

def get_local_gguf_models() -> List[Dict]:
    """
    Finds .gguf models stored in the local models/ directory.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    models = []
    for f in MODELS_DIR.glob("*.gguf"):
        size_bytes = f.stat().st_size
        models.append({
            "name": f.name,
            "short_name": f.stem,
            "path": str(f.resolve()),
            "size_bytes": size_bytes,
            "size_gb": round(size_bytes / (1024**3), 2),
            "source": "local"
        })
    return models

def list_all_available_models() -> List[Dict]:
    """
    Returns a unified list of all models found locally and via Ollama.
    """
    all_models = get_local_gguf_models() + get_ollama_models()
    return all_models

def resolve_model(name: str) -> Optional[Dict]:
    """
    Finds a model by exact name, short name, or partial match.
    """
    all_models = list_all_available_models()
    # 1. Exact match
    for m in all_models:
        if m["name"].lower() == name.lower() or m.get("short_name", "").lower() == name.lower():
            return m

    # 2. Match without tag (e.g. 'qwen2.5-coder' matches 'qwen2.5-coder:7b')
    for m in all_models:
        base_name = m["name"].split(":")[0].lower()
        if base_name == name.lower():
            return m

    # 3. Substring match
    for m in all_models:
        if name.lower() in m["name"].lower():
            return m

    return None

def pull_model_cli(model_name: str) -> bool:
    """
    Pulls ANY model. If Ollama is installed, uses 'ollama pull <name>'.
    Otherwise, if it's a HuggingFace URL, downloads it directly.
    """
    print(f"[*] Requesting model: {model_name}")

    # Check if URL
    if model_name.startswith("http://") or model_name.startswith("https://"):
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        filename = model_name.split("/")[-1].split("?")[0]
        if not filename.endswith(".gguf"):
            filename += ".gguf"
        dest = MODELS_DIR / filename
        print(f"[*] Downloading GGUF from URL to: {dest}")
        try:
            urllib.request.urlretrieve(model_name, dest)
            print(f"[+] Download complete: {filename}")
            return True
        except Exception as e:
            print(f"[-] Download failed: {e}")
            return False

    # Check if Ollama CLI is available
    ollama_path = shutil.which("ollama")
    if ollama_path:
        print(f"[*] Using Ollama backend to pull '{model_name}'...")
        print("[*] Streaming download progress from Ollama registry:\n")
        try:
            proc = subprocess.run(["ollama", "pull", model_name])
            if proc.returncode == 0:
                print(f"\n[+] Successfully pulled '{model_name}' into your local registry!")
                return True
            else:
                print(f"\n[-] Ollama pull exited with code {proc.returncode}")
                return False
        except Exception as e:
            print(f"[-] Error invoking Ollama: {e}")
            return False
    else:
        print("[-] Ollama CLI was not found on your system PATH.")
        print("[*] Install Ollama from https://ollama.com or provide a direct HuggingFace GGUF URL.")
        return False
