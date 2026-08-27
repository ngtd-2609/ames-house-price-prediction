"""Backend service layer for deployment."""

from .service import load_assets, predict_batch, predict_one

__all__ = ["load_assets", "predict_batch", "predict_one"]
