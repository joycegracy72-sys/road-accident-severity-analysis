"""Evaluation, visualization, confusion matrix plotting, and metrics extraction."""

from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from src.utils import (
    REPORTS_DIR,
    FIGURES_DIR,
    setup_logger,
)

logger = setup_logger("evaluate_model")


def plot_confusion_matrices() -> None:
    """Generates and saves visual confusion matrix comparison across candidate models."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = REPORTS_DIR / "evaluation_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Evaluation summary not found: {summary_path}")
        
    with open(summary_path, "r", encoding="utf-8") as f:
        results = json.load(f)
        
    class_labels = ["Fatal (1)", "Serious (2)", "Slight (3)"]
    num_models = len(results)
    
    fig, axes = plt.subplots(1, num_models, figsize=(5 * num_models, 4.5))
    if num_models == 1:
        axes = [axes]
        
    for ax, (name, metrics) in zip(axes, results.items()):
        cm = np.array(metrics["confusion_matrix"])
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            xticklabels=class_labels,
            yticklabels=class_labels,
            ax=ax,
        )
        macro_f1 = metrics["macro_f1"]
        acc = metrics["accuracy"]
        ax.set_title(f"{name}\nMacro-F1: {macro_f1:.4f} | Acc: {acc:.4f}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Predicted Severity")
        ax.set_ylabel("True Severity")
        
    plt.tight_layout()
    out_path = FIGURES_DIR / "confusion_matrices.png"
    fig.savefig(out_path, dpi=300)
    plt.close()
    logger.info(f"Saved confusion matrices figure to {out_path}")


if __name__ == "__main__":
    plot_confusion_matrices()
