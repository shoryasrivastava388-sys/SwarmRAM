import os
import sys
import platform
import zipfile
import urllib.request
import shutil
from pathlib import Path
from swarm.config import BIN_DIR

LLAMA_CPP_RELEASES_API = "https://api.github.com/repos/ggerganov/llama.cpp/releases/latest"
# Direct stable release zip for Windows x64 AVX2
DEFAULT_WIN_RELEASE_ZIP = "https://github.com/ggerganov/llama.cpp/releases/download/b4400/llama-b4400-bin-win-avx2-x64.zip"

def get_binary_names():
    is_win = platform.system() == "Windows"
    ext = ".exe" if is_win else ""
    return {
        "rpc_server": f"rpc-server{ext}",
        "llama_server": f"llama-server{ext}",
        "llama_cli": f"llama-cli{ext}"
    }

def find_binary(binary_type: str) -> Path | None:
    """
    Checks BIN_DIR and system PATH for the required executable.
    binary_type: 'rpc_server' or 'llama_server'
    """
    names = get_binary_names()
    target_name = names.get(binary_type)
    if not target_name:
        return None

    # Check local project bin/
    local_path = BIN_DIR / target_name
    if local_path.is_file():
        return local_path

    # Check system PATH
    system_path = shutil.which(target_name)
    if system_path:
        return Path(system_path)

    return None

def download_and_extract_binaries(progress_callback=None) -> bool:
    """
    Downloads and extracts pre-compiled llama.cpp binaries into the bin/ folder.
    """
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    if platform.system() != "Windows":
        print("[!] Note: Automatic download is pre-configured for Windows x64.")
        print("[!] On Linux/macOS, install or build llama.cpp with: 'cmake -B build -DLLAMA_RPC=ON && cmake --build build'")
        return False

    zip_dest = BIN_DIR / "llama_binaries.zip"
    try:
        print(f"[*] Downloading llama.cpp binaries from:\n    {DEFAULT_WIN_RELEASE_ZIP}")
        
        def reporthook(block_num, block_size, total_size):
            if total_size > 0 and progress_callback:
                percent = min(100, int((block_num * block_size * 100) / total_size))
                progress_callback(percent)

        urllib.request.urlretrieve(DEFAULT_WIN_RELEASE_ZIP, zip_dest, reporthook=reporthook)
        print("\n[*] Download completed. Extracting...")

        with zipfile.ZipFile(zip_dest, 'r') as zip_ref:
            zip_ref.extractall(BIN_DIR)

        if zip_dest.exists():
            zip_dest.unlink()

        print(f"[+] Binaries ready in: {BIN_DIR}")
        return True
    except Exception as e:
        print(f"[-] Failed to download binaries automatically: {e}")
        if zip_dest.exists():
            zip_dest.unlink()
        return False
