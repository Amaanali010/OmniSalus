"""Run beside model_engine.py; check all nine loaders, even after failures."""
from pathlib import Path
import importlib
import sys

ROOT = Path(__file__).resolve().parent
CHECKS = [
    ('heart_lgbm', 'heart_lgbm_model.pkl', None, None),
    ('heart_logreg', 'heart_logreg_model.pkl', None, None),
    ('heart_xgb', None, 'heart_xgb_loader', 'load_heart_xgb'),
    ('diabetes', None, 'diabetes_loader', 'load_diabetes'),
    ('stroke', None, 'stroke_loader', 'load_stroke'),
    ('liver', 'liver_model.pkl', None, None),
    ('kidney', 'kidney_model.pkl', None, None),
    ('breast_cancer', 'breast_cancer_model.pkl', None, None),
    ('obesity', 'obesity_model.pkl', None, None),
]


def main():
    failures = []
    for name, filename, module, function in CHECKS:
        try:
            if module:
                getattr(importlib.import_module(module), function)(ROOT)
            else:
                importlib.import_module('joblib').load(ROOT / filename)
            print(f'PASS: {name}', flush=True)
        except Exception as exc:
            failures.append(name)
            print(f'FAIL: {name}: {type(exc).__name__}: {exc}', flush=True)
    print(f'\nLoaded {len(CHECKS) - len(failures)}/{len(CHECKS)} models.')
    if failures:
        print('Send the complete output above so all failures can be handled together.')
    else:
        print('All loaders passed. Start app.py using this same Python environment.')
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
