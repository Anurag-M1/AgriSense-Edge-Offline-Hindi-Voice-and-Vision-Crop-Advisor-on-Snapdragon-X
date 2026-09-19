#!/usr/bin/env python3
"""
run_bench.py — Benchmark runner for AgriSense Edge.

Runs N warm iterations per pipeline stage and end-to-end,
on each backend, and writes CSV + chart.
"""

import argparse
import csv
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

import numpy as np


def get_device_label() -> str:
    """Generate a device label for benchmark results."""
    machine = platform.machine()
    system = platform.system()
    if system == "Windows" and machine in ("ARM64", "aarch64"):
        return "Snapdragon X (local)"
    return f"{system} {machine} (dev machine)"


def run_stage_benchmark(stage_fn, name: str, iterations: int = 30) -> dict:
    """Run a benchmark for a single stage.

    Args:
        stage_fn: Callable that runs the stage once. Returns latency in ms.
        name: Stage name.
        iterations: Number of warm iterations.

    Returns:
        Dict with benchmark results.
    """
    # Warmup
    for _ in range(min(3, iterations)):
        stage_fn()

    # Measure
    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        stage_fn()
        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)

    return {
        "stage": name,
        "iterations": iterations,
        "median_ms": round(statistics.median(latencies), 2),
        "p95_ms": round(sorted(latencies)[int(len(latencies) * 0.95)], 2),
        "mean_ms": round(statistics.mean(latencies), 2),
        "min_ms": round(min(latencies), 2),
        "max_ms": round(max(latencies), 2),
        "stdev_ms": round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0,
        "device": get_device_label(),
    }


def main():
    parser = argparse.ArgumentParser(description="AgriSense Edge Benchmark Runner")
    parser.add_argument("--iterations", type=int, default=30, help="Iterations per stage")
    parser.add_argument("--backend", default="cpu", choices=["cpu", "qnn_npu"])
    parser.add_argument("--output-dir", default="benchmarks/results")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"  AgriSense Edge Benchmark — {args.backend}")
    print(f"  Device: {get_device_label()}")
    print(f"  Iterations: {args.iterations}")
    print("=" * 60)

    # TODO: Import and load engines, then benchmark each stage
    # For now, print placeholder
    print("\n⚠️  Models not yet loaded. Benchmark will run after Phase 1-5 are complete.")
    print("Run this script after implementing the engine backends.\n")

    # Create empty results CSV
    csv_path = output_dir / f"latency_{args.backend}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "stage", "iterations", "median_ms", "p95_ms",
                "mean_ms", "min_ms", "max_ms", "stdev_ms", "device",
            ],
        )
        writer.writeheader()

    print(f"Results will be written to: {csv_path}")


if __name__ == "__main__":
    main()
