#!/usr/bin/env python3
"""
accuracy_eval.py — Vision model accuracy evaluation for AgriSense Edge.

Reports held-out accuracy, confusion matrix, and per-class metrics
for both FP32 and quantised models on:
1. PlantVillage (clean baseline test set)
2. PlantDoc (field-style test set with clutter, lighting, and noise)
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image

from app.backend.engines.vision import VisionEngine


def evaluate_dataset(
    engine: VisionEngine,
    dataset_dir: Path,
    labels: list[str],
) -> dict:
    """Evaluate vision engine on a dataset folder structured as dataset_dir/<class_name>/<images>."""
    label_to_idx = {name: i for i, name in enumerate(labels)}
    num_classes = len(labels)

    confusion_mat = np.zeros((num_classes, num_classes), dtype=int)
    total_samples = 0
    top1_correct = 0
    top3_correct = 0
    low_confidence_count = 0
    latencies = []

    for class_name in labels:
        class_folder = dataset_dir / class_name
        if not class_folder.exists() or not class_folder.is_dir():
            continue

        true_idx = label_to_idx[class_name]
        image_files = list(class_folder.glob("*.jpg")) + list(class_folder.glob("*.png"))

        for img_path in image_files:
            try:
                img = Image.open(img_path).convert("RGB")
                res = engine.classify(img)
                latencies.append(res.latency_ms)

                pred_label = res.top_3[0][0]
                pred_idx = label_to_idx.get(pred_label, num_classes - 1)
                confusion_mat[true_idx, pred_idx] += 1

                total_samples += 1

                if res.is_low_confidence:
                    low_confidence_count += 1

                if pred_label == class_name:
                    top1_correct += 1

                top_3_labels = [lbl for lbl, _ in res.top_3]
                if class_name in top_3_labels:
                    top3_correct += 1

            except Exception as e:
                print(f"Error processing {img_path}: {e}")

    if total_samples == 0:
        return {
            "total_samples": 0,
            "top1_accuracy": 0.0,
            "top3_accuracy": 0.0,
            "low_confidence_rate": 0.0,
            "avg_latency_ms": 0.0,
        }

    top1_acc = float(top1_correct / total_samples)
    top3_acc = float(top3_correct / total_samples)
    low_conf_rate = float(low_confidence_count / total_samples)
    avg_latency = float(np.mean(latencies)) if latencies else 0.0

    # Per-class metrics
    per_class = {}
    for i, name in enumerate(labels):
        tp = confusion_mat[i, i]
        fp = np.sum(confusion_mat[:, i]) - tp
        fn = np.sum(confusion_mat[i, :]) - tp
        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        per_class[name] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": int(np.sum(confusion_mat[i, :])),
        }

    return {
        "total_samples": total_samples,
        "top1_accuracy": round(top1_acc, 4),
        "top3_accuracy": round(top3_acc, 4),
        "low_confidence_rate": round(low_conf_rate, 4),
        "avg_latency_ms": round(avg_latency, 2),
        "per_class": per_class,
        "confusion_matrix": confusion_mat.tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description="Vision Model Accuracy Evaluation")
    parser.add_argument("--fp32-model", default="models/vision/model.onnx", help="Path to FP32 ONNX model")
    parser.add_argument("--int8-model", default="models/vision/model_quantized.onnx", help="Path to INT8 ONNX model")
    parser.add_argument("--data-dir", default="benchmarks/data", help="Path to test datasets folder")
    parser.add_argument("--output-dir", default="benchmarks/results")
    parser.add_argument("--backend", default="cpu", choices=["cpu", "qnn_npu"])
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_dir = Path(args.data_dir)

    pv_dir = data_dir / "plantvillage_test"
    pd_dir = data_dir / "plantdoc_test"

    print("=" * 65)
    print("  AgriSense Edge — Vision Accuracy & Generalisation Evaluation")
    print(f"  Backend: {args.backend}")
    print("=" * 65)

    # 1. Evaluate FP32 Model
    print(f"\n[1/2] Evaluating FP32 Model: {args.fp32_model}")
    engine_fp32 = VisionEngine(model_path=args.fp32_model)
    engine_fp32.load(backend=args.backend)

    pv_fp32 = evaluate_dataset(engine_fp32, pv_dir, engine_fp32.labels)
    pd_fp32 = evaluate_dataset(engine_fp32, pd_dir, engine_fp32.labels)
    engine_fp32.unload()

    # 2. Evaluate INT8 Quantized Model
    print(f"\n[2/2] Evaluating INT8 Quantized Model: {args.int8_model}")
    engine_int8 = VisionEngine(model_path=args.int8_model)
    engine_int8.load(backend=args.backend)

    pv_int8 = evaluate_dataset(engine_int8, pv_dir, engine_int8.labels)
    pd_int8 = evaluate_dataset(engine_int8, pd_dir, engine_int8.labels)
    engine_int8.unload()

    # Summary table
    print("\n" + "=" * 65)
    print(f"{'Metric':<32} | {'FP32 Model':<14} | {'INT8 Quantized':<14}")
    print("-" * 65)
    print(f"{'PlantVillage Top-1 Acc (Lab)':<32} | {pv_fp32['top1_accuracy']:>13.1%} | {pv_int8['top1_accuracy']:>13.1%}")
    print(f"{'PlantVillage Top-3 Acc':<32} | {pv_fp32['top3_accuracy']:>13.1%} | {pv_int8['top3_accuracy']:>13.1%}")
    print(f"{'PlantDoc Top-1 Acc (Field)':<32} | {pd_fp32['top1_accuracy']:>13.1%} | {pd_int8['top1_accuracy']:>13.1%}")
    print(f"{'PlantDoc Top-3 Acc':<32} | {pd_fp32['top3_accuracy']:>13.1%} | {pd_int8['top3_accuracy']:>13.1%}")
    print(f"{'Avg Latency (ms)':<32} | {pv_fp32['avg_latency_ms']:>11.2f} ms | {pv_int8['avg_latency_ms']:>11.2f} ms")
    print(f"{'Field Rejection Rate (<40%)':<32} | {pd_fp32['low_confidence_rate']:>13.1%} | {pd_int8['low_confidence_rate']:>13.1%}")
    print("=" * 65)

    # Save results JSON
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "backend": args.backend,
        "classes": engine_fp32.labels,
        "fp32": {
            "model_path": str(args.fp32_model),
            "plantvillage": pv_fp32,
            "plantdoc": pd_fp32,
        },
        "int8": {
            "model_path": str(args.int8_model),
            "plantvillage": pv_int8,
            "plantdoc": pd_int8,
        },
    }

    json_path = out_dir / "vision_accuracy.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Saved evaluation metrics to {json_path}")

    # Save confusion matrix CSV (for FP32 PlantDoc)
    cm_path = out_dir / "confusion_matrix.csv"
    with open(cm_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["True\\Pred"] + engine_fp32.labels)
        for i, row in enumerate(pd_fp32["confusion_matrix"]):
            writer.writerow([engine_fp32.labels[i]] + row)
    print(f"✓ Saved confusion matrix to {cm_path}")


if __name__ == "__main__":
    main()
