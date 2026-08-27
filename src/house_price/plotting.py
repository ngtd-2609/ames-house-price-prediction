"""Plotting utilities shared by training diagnostics modules."""
from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt


def save_figure(figures_dir: Path, name: str) -> Path:
    """Save current matplotlib figure with consistent layout and close it."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    path = figures_dir / name
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path
