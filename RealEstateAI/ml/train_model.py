from __future__ import annotations

from ml.model import PredictionEngine


def main() -> None:
    """Train the ML model and persist it to disk."""

    engine = PredictionEngine()
    mae = engine.train()
    print(f"Model trained. Validation MAE: {mae:.2f}")


if __name__ == "__main__":
    main()
