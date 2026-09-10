"""
NexChain Local LLM Connector & Standalone GGUF Engine
Supports:
1. Direct GGUF Model Execution via llama-cpp-python or llama-cli (Works on Android Termux & PC without Ollama)
2. Local Ollama HTTP API (if running on desktop/laptop)
3. Zero-dependency fast rule-based fallback if no model is loaded.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import httpx

# HuggingFace Direct GGUF Download URL (Qwen2.5-0.5B-Instruct-Q4_K_M, ~468MB)
GGUF_MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"
GGUF_MODEL_FILENAME = "qwen2.5-0.5b.gguf"

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:0.5b"

_llama_model_instance = None


def get_local_gguf_path() -> Optional[Path]:
    """Finds downloaded GGUF model file across standard locations."""
    # 1. Project root models/
    project_root = Path(__file__).resolve().parent.parent.parent
    local_path = project_root / "models" / GGUF_MODEL_FILENAME
    if local_path.is_file() and local_path.stat().st_size > 50_000_000:
        return local_path

    # 2. User home ~/.nexchain/models/
    home_path = Path.home() / ".nexchain" / "models" / GGUF_MODEL_FILENAME
    if home_path.is_file() and home_path.stat().st_size > 50_000_000:
        return home_path

    return None


def is_gguf_model_present() -> bool:
    return get_local_gguf_path() is not None


def is_ollama_running() -> bool:
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=1.2)
        return r.status_code == 200
    except Exception:
        return False


def get_available_model() -> Optional[str]:
    """Returns active model identifier (GGUF or Ollama)."""
    gguf = get_local_gguf_path()
    if gguf:
        return f"Qwen2.5-0.5B (Direct GGUF: {gguf.name})"

    if is_ollama_running():
        try:
            r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=1.2)
            if r.status_code == 200:
                names = [m["name"] for m in r.json().get("models", [])]
                for pref in [DEFAULT_MODEL, "qwen2.5:0.5b", "qwen2.5:latest"]:
                    for name in names:
                        if pref in name:
                            return f"Ollama: {name}"
                if names:
                    return f"Ollama: {names[0]}"
        except Exception:
            pass

    return None


def query_gguf_direct(prompt: str, system_prompt: str = "") -> Optional[str]:
    """Runs inference directly using GGUF file via llama-cpp-python or llama-cli."""
    global _llama_model_instance
    model_path = get_local_gguf_path()
    if not model_path:
        return None

    full_prompt = f"<|im_start|>system\n{system_prompt or 'You are NexChain AI, an offline crypto crime forensics assistant.'}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

    # Strategy 1: llama_cpp Python package
    try:
        from llama_cpp import Llama
        if _llama_model_instance is None:
            _llama_model_instance = Llama(
                model_path=str(model_path),
                n_ctx=2048,
                n_threads=os.cpu_count() or 4,
                verbose=False
            )
        output = _llama_model_instance(
            full_prompt,
            max_tokens=256,
            temperature=0.2,
            stop=["<|im_end|>"]
        )
        return output["choices"][0]["text"].strip()
    except ImportError:
        pass
    except Exception:
        pass

    # Strategy 2: llama-cli / llama.cpp binary (commonly installed in Termux / Linux)
    cli_bin = shutil.which("llama-cli") or shutil.which("llama-completion") or shutil.which("llama")
    if cli_bin:
        try:
            cmd = [
                cli_bin,
                "-m", str(model_path),
                "-p", full_prompt,
                "-n", "256",
                "--temp", "0.2",
                "--silent-prompt"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            if res.returncode == 0 and res.stdout.strip():
                # Clean prompt echo if any
                out = res.stdout.strip()
                if "<|im_start|>assistant" in out:
                    out = out.split("<|im_start|>assistant")[-1]
                return out.replace("<|im_end|>", "").strip()
        except Exception:
            pass

    return None


def query_local_llm(prompt: str, system_prompt: str = "", temperature: float = 0.2) -> Optional[str]:
    """Queries either direct GGUF engine or local Ollama instance."""
    # 1. First try Direct GGUF (Works on Termux & Laptop without Ollama)
    direct_res = query_gguf_direct(prompt, system_prompt)
    if direct_res:
        return direct_res

    # 2. Try Ollama if running
    if is_ollama_running():
        try:
            payload = {
                "model": DEFAULT_MODEL,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 256
                }
            }
            r = httpx.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=6.0)
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except Exception:
            pass

    return None


def download_gguf_model(target_dir: Optional[Path] = None) -> bool:
    """Streams and downloads Qwen2.5-0.5B GGUF with real-time progress bar."""
    import urllib.request
    from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

    dest_dir = target_dir or (Path.home() / ".nexchain" / "models")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / GGUF_MODEL_FILENAME

    if dest_file.is_file() and dest_file.stat().st_size > 100_000_000:
        return True

    print(f"\n[*] Downloading {GGUF_MODEL_FILENAME} directly from HuggingFace...")
    print(f"[*] Target location: {dest_file}\n")

    try:
        with httpx.stream("GET", GGUF_MODEL_URL, follow_redirects=True, timeout=30.0) as response:
            if response.status_code != 200:
                print(f"[!] HTTP Error: {response.status_code}")
                return False
            
            total = int(response.headers.get("content-length", 491400032))
            
            from rich.progress import Progress
            with Progress() as progress:
                task = progress.add_task("[cyan]Downloading AI Brain Model...", total=total)
                with open(dest_file, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=65536):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
        
        print("\n[✓] Download complete!")
        return True
    except Exception as e:
        print(f"[!] Direct download error: {e}")
        # Fallback to standard curl
        try:
            subprocess.run(["curl", "-L", "--progress-bar", GGUF_MODEL_URL, "-o", str(dest_file)], check=True)
            return True
        except Exception:
            return False
