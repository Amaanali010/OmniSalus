"""Load the recovered heart model without XGBoost pickle snapshots."""
from pathlib import Path
import joblib
from xgboost import XGBClassifier


def load_heart_xgb(model_dir):
    root = Path(model_dir)
    bundle = joblib.load(root / 'heart_xgb_preprocessing.pkl')
    model = XGBClassifier()
    model.load_model(root / 'heart_xgb_portable.json')
    pipe = bundle['pipeline']
    pipe.steps = [(name, model if name == 'model' else step)
                  for name, step in pipe.steps]
    return bundle
