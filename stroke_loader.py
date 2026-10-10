"""Load the recovered stroke classifier without XGBoost pickle snapshots."""
import json
from pathlib import Path
from xgboost import XGBClassifier


def load_stroke(model_dir):
    root = Path(model_dir)
    with (root / 'stroke_metadata.json').open(encoding='utf-8') as f:
        bundle = json.load(f)
    model = XGBClassifier()
    model.load_model(root / 'stroke_portable.json')
    bundle['model'] = model
    return bundle
