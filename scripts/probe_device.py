#!/usr/bin/env python3
"""
probe_device.py — Hardware and runtime probe for AgriSense Edge.

Prints CPU architecture, OS, Python version, available ONNX Runtime providers,
and whether the QNN execution provider loads successfully.
"""

import os
import platform
import struct
import sys


def probe_python():
    """Print Python environment details."""
    print("=" * 60)
    print("  AgriSense Edge — Device Probe")
    print("=" * 60)
    print()
    print("── Python ──")
    print(f"  Version:        {sys.version}")
    print(f"  Executable:     {sys.executable}")
    print(f"  Pointer size:   {struct.calcsize('P') * 8}-bit")
    print(f"  Platform tag:   {sys.platform}")
    print()


def probe_os():
    """Print OS details."""
    print("── Operating System ──")
    print(f"  System:         {platform.system()}")
    print(f"  Release:        {platform.release()}")
    print(f"  Version:        {platform.version()}")
    print(f"  Machine:        {platform.machine()}")
    print(f"  Processor:      {platform.processor() or 'unknown'}")
    print()


def probe_onnxruntime():
    """Check ONNX Runtime and available execution providers."""
    print("── ONNX Runtime ──")
    try:
        import onnxruntime as ort

        print(f"  Version:        {ort.__version__}")
        providers = ort.get_available_providers()
        print(f"  Providers:      {', '.join(providers)}")

        # Check for QNN specifically
        qnn_available = "QNNExecutionProvider" in providers
        print(f"  QNN EP:         {'✅ Available' if qnn_available else '❌ Not available'}")

        if not qnn_available:
            # Try loading onnxruntime-qnn plugin
            try:
                import onnxruntime_qnn as qnn_ep  # noqa: F401

                print(f"  QNN Plugin:     ✅ Installed (may need registration)")
            except ImportError:
                print(f"  QNN Plugin:     ❌ Not installed (pip install onnxruntime-qnn)")

        # Check for CUDA (useful for training)
        cuda_available = "CUDAExecutionProvider" in providers
        print(f"  CUDA EP:        {'✅ Available' if cuda_available else '❌ Not available'}")

    except ImportError:
        print("  ❌ onnxruntime not installed (pip install onnxruntime)")
    print()


def probe_torch():
    """Check PyTorch availability (needed for training/export)."""
    print("── PyTorch (for training/export) ──")
    try:
        import torch

        print(f"  Version:        {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA device:    {torch.cuda.get_device_name(0)}")
        # Check MPS (Apple Silicon)
        if hasattr(torch.backends, "mps"):
            print(f"  MPS available:  {torch.backends.mps.is_available()}")
    except ImportError:
        print("  ❌ Not installed (pip install torch — needed for training/export only)")
    print()


def probe_npm():
    """Check Node.js and npm for frontend."""
    print("── Node.js / npm (for frontend) ──")
    try:
        import subprocess

        result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print(f"  Node.js:        {result.stdout.strip()}")
        else:
            print("  Node.js:        ❌ Not found")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("  Node.js:        ❌ Not found")

    try:
        import subprocess

        result = subprocess.run(
            ["npm", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print(f"  npm:            {result.stdout.strip()}")
        else:
            print("  npm:            ❌ Not found")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("  npm:            ❌ Not found")
    print()


def probe_disk():
    """Check available disk space."""
    print("── Disk Space ──")
    try:
        usage = os.statvfs(".")
        free_gb = (usage.f_bavail * usage.f_frsize) / (1024**3)
        total_gb = (usage.f_blocks * usage.f_frsize) / (1024**3)
        print(f"  Free:           {free_gb:.1f} GB / {total_gb:.1f} GB")
        if free_gb < 10:
            print("  ⚠️  Less than 10 GB free — models may not fit!")
    except (AttributeError, OSError):
        # os.statvfs not available on Windows
        try:
            import shutil

            total, used, free = shutil.disk_usage(".")
            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            print(f"  Free:           {free_gb:.1f} GB / {total_gb:.1f} GB")
            if free_gb < 10:
                print("  ⚠️  Less than 10 GB free — models may not fit!")
        except Exception:
            print("  Could not determine disk space")
    print()


def probe_summary():
    """Print a summary of readiness."""
    print("── Summary ──")
    is_arm = platform.machine().lower() in ("aarch64", "arm64")
    is_windows = platform.system() == "Windows"

    if is_windows and is_arm:
        print("  🎯 Running on Windows ARM64 — target platform!")
        print("  → Use qnn_npu backend for inference")
    elif is_windows:
        print("  💻 Running on Windows x64 — use for export/compile via AI Hub")
        print("  → Use cpu backend for inference")
    else:
        print(f"  💻 Running on {platform.system()} {platform.machine()} — development machine")
        print("  → Use cpu backend for inference")
        print("  → Use AI Hub Workbench for NPU profiling on hosted devices")
    print()
    print("=" * 60)


def main():
    probe_python()
    probe_os()
    probe_onnxruntime()
    probe_torch()
    probe_npm()
    probe_disk()
    probe_summary()


if __name__ == "__main__":
    main()
