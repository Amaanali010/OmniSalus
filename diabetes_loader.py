"""Load the original diabetes model from portable JSON files."""
import json
from pathlib import Path
from xgboost import XGBClassifier


def load_diabetes(model_dir):
    root = Path(model_dir)
    with (root / 'diabetes_metadata.json').open(encoding='utf-8') as f:
        bundle = json.load(f)
    model = XGBClassifier()
    model.load_model(root / 'diabetes_portable.json')
    bundle['model'] = model
    return bundle
