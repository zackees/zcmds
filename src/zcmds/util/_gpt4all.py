"""
Work in progress using the documentation at:
https://docs.gpt4all.io/gpt4all_python.html#quickstart
"""

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gpt4all import GPT4All


@dataclass
class Device:
    device_name: str
    index: int


def parse_devices(text: str) -> list[Device]:
    # Split the text into lines
    lines = text.split("\n")

    # Find the start of the device section
    start_index = lines.index("Devices:") + 2  # Skip '========' line

    # Extract device information
    devices: dict[str, Any] = {}
    current_device = None

    for i, line in enumerate(lines[start_index:]):
        if line.startswith("GPU"):
            current_device = line[:-1]  # Remove colon
            devices[current_device] = {}
            devices[current_device]["idx"] = i
        elif current_device and line.strip():
            key, value = line.strip().split("=", 1)
            devices[current_device][key.strip()] = value.strip()

    out: list[Device] = []
    # for device in devices:
    for key, device in devices.items():
        idx = int(device["idx"])
        device_name = device["deviceName"]
        d = Device(device_name=device_name, index=idx)
        out.append(d)
    return out


CACHE_DIR = Path.home() / ".cache" / "gpt4all"
MODEL_NAME = "orca-mini-3b-gguf2-q4_0.gguf"
# ggml-mpt-7b-chat.bin
# MODEL_NAME = "ggml-mpt-7b-chat.bin"


def get_device() -> str:
    # return "cpu"
    # return "gpu"
    # return "NVIDIA GeForce RTX 3060"

    cp = subprocess.run(
        "vulkaninfo --summary",
        shell=True,
        check=True,
        capture_output=True,
        universal_newlines=True,
        text=True,
        encoding="utf-8",
    )
    devices = parse_devices(cp.stdout)
    print(devices)
    return "cpu"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GPT4All")
    parser.add_argument("--clear", action="store_true", help="Clear the cache")
    return parser.parse_args()


def main() -> int:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    args = parse_args()
    if args.clear:
        for file in CACHE_DIR.glob("*"):
            os.remove(file)

    model = GPT4All(model_name=MODEL_NAME, model_path=CACHE_DIR, device=get_device())
    output = model.generate("The capital of France is ", max_tokens=3)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
