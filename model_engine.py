import os
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb
from heart_xgb_loader import load_heart_xgb
from diabetes_loader import load_diabetes
from stroke_loader import load_stroke

# Directory where pickle models reside
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

class ModelEngine:
    def __init__(self, model_dir=MODEL_DIR):
        self.model_dir = model_dir
        self.models = {}
        self.load_all_models()

    def _get_path(self, filename):
        return os.path.join(self.model_dir, filename)

    def load_all_models(self):
        print("[ModelEngine] Loading ML pickle models...")
        # 1. Heart Models
        self.models['heart_lgbm'] = joblib.load(self._get_path('heart_lgbm_model.pkl'))
        self.models['heart_logreg'] = joblib.load(self._get_path('heart_logreg_model.pkl'))
        self.models['heart_xgb'] = load_heart_xgb(self.model_dir)
        
        # 2. Diabetes
        self.models['diabetes'] = load_diabetes(self.model_dir)
        
        # 3. Stroke
        self.models['stroke'] = load_stroke(self.model_dir)
        
        # 4. Liver
        self.models['liver'] = joblib.load(self._get_path('liver_model.pkl'))
        
        # 5. Kidney
        self.models['kidney'] = joblib.load(self._get_path('kidney_model.pkl'))
        
        # 6. Breast Cancer
        self.models['breast_cancer'] = joblib.load(self._get_path('breast_cancer_model.pkl'))
        
        # 7. Obesity
        self.models['obesity'] = joblib.load(self._get_path('obesity_model.pkl'))
        
        print("[ModelEngine] All 9 models loaded successfully!")

    # -------------------------------------------------------------
    # 1. HEART DISEASE PREDICTION (3 Models)
    # -------------------------------------------------------------
    def predict_heart(self, data, model_name='lgbm'):
        """
        data dict features:
        BMI, Smoking, AlcoholDrinking, Stroke, PhysicalHealth, MentalHealth,
        DiffWalking, Sex, AgeCategory, Race, Diabetic, PhysicalActivity,
        GenHealth, SleepTime, Asthma, KidneyDisease, SkinCancer
        """
        # Calculate BMI if Height and Weight provided instead of direct BMI
        if 'Height' in data and 'Weight' in data and (float(data.get('Height', 0)) > 0):
            h_m = float(data['Height']) / 100.0 if float(data['Height']) > 3 else float(data['Height'])
            w_kg = float(data['Weight'])
            data['BMI'] = round(w_kg / (h_m * h_m), 1)

        key = f'heart_{model_name}' if not model_name.startswith('heart_') else model_name
        if key not in self.models:
            key = 'heart_lgbm'

        d = self.models[key]
        df = pd.DataFrame([data])
        pipe = d['pipeline']

        if 'xgb' in key:
            prep = pipe.named_steps['prep']
            model = pipe.named_steps['model']
            X_trans = prep.transform(df)
            try:
                prob = float(model.predict_proba(X_trans)[0][1])
            except Exception:
                b = model.get_booster()
                dmat = xgb.DMatrix(X_trans)
                prob = float(b.predict(dmat)[0])
        else:
            prob = float(pipe.predict_proba(df)[0][1])

        th = float(d.get('threshold', 0.5))
        is_positive = prob >= th

        # Severity range
        if prob < 0.35:
            severity = "Normal / Low Risk"
            badge_class = "success"
        elif prob < th:
            severity = "Moderate / Watch"
            badge_class = "warning"
        elif prob < 0.75:
            severity = "High Risk"
            badge_class = "danger"
        else:
            severity = "Critical Emergency Risk"
            badge_class = "critical"

        return {
            'model_used': model_name.upper(),
            'probability': round(prob, 4),
            'probability_pct': round(prob * 100, 1),
            'threshold': round(th, 4),
            'prediction': int(is_positive),
            'diagnosis': 'Heart Disease Risk Detected' if is_positive else 'No Heart Disease Risk Detected',
            'severity': severity,
            'badge_class': badge_class,
            'roc_auc': float(d.get('test_roc_auc', 0.836)),
            'calculated_bmi': data.get('BMI')
        }

    def predict_heart_all(self, data):
        """Run all 3 heart models for comparison"""
        lgbm_res = self.predict_heart(data, 'lgbm')
        logreg_res = self.predict_heart(data, 'logreg')
        xgb_res = self.predict_heart(data, 'xgb')
        
        avg_prob = (lgbm_res['probability'] + logreg_res['probability'] + xgb_res['probability']) / 3.0
        return {
            'consensus_prob_pct': round(avg_prob * 100, 1),
            'lgbm': lgbm_res,
            'logreg': logreg_res,
            'xgb': xgb_res
        }

    # -------------------------------------------------------------
    # 2. DIABETES PREDICTION
    # -------------------------------------------------------------
    def predict_diabetes(self, data):
        d = self.models['diabetes']
        features = d['features']
        
        # Fill missing with 0
        row = [float(data.get(f, 0)) for f in features]
        df = pd.DataFrame([row], columns=features)
        
        model = d['model']
        try:
            prob = float(model.predict_proba(df)[0][1])
        except Exception:
            b = model.get_booster()
            dmat = xgb.DMatrix(df)
            prob = float(b.predict(dmat)[0])

        th = float(d.get('threshold', 0.5))
        is_positive = prob >= th

        if prob < 0.30:
            severity = "Normal / Low Glycemic Risk"
            badge_class = "success"
        elif prob < th:
            severity = "Moderate / Pre-Diabetic Watch"
            badge_class = "warning"
        elif prob < 0.70:
            severity = "High Diabetic Risk"
            badge_class = "danger"
        else:
            severity = "Emergency High Diabetic Risk"
            badge_class = "critical"

        return {
            'probability': round(prob, 4),
            'probability_pct': round(prob * 100, 1),
            'threshold': th,
            'prediction': int(is_positive),
            'diagnosis': 'High Diabetes Risk Detected' if is_positive else 'Normal / Low Diabetes Risk',
            'severity': severity,
            'badge_class': badge_class,
            'accuracy': 70.8
        }

    # -------------------------------------------------------------
    # 3. STROKE PREDICTION
    # -------------------------------------------------------------
    def predict_stroke(self, data):
        d = self.models['stroke']
        features = d['features']
        row = {f: 0.0 for f in features}
        
        row['age'] = float(data.get('age', 50))
        row['hypertension'] = float(data.get('hypertension', 0))
        row['heart_disease'] = float(data.get('heart_disease', 0))
        row['avg_glucose_level'] = float(data.get('avg_glucose_level', 90))
        row['bmi'] = float(data.get('bmi', 25))

        gender = data.get('gender', 'Female')
        if gender == 'Male': row['gender_Male'] = 1.0
        elif gender == 'Other': row['gender_Other'] = 1.0

        if str(data.get('ever_married', '')).lower() in ['yes', '1', 'true']:
            row['ever_married_Yes'] = 1.0

        wt = data.get('work_type', 'Private')
        if f'work_type_{wt}' in row:
            row[f'work_type_{wt}'] = 1.0

        if data.get('Residence_type') == 'Urban':
            row['Residence_type_Urban'] = 1.0

        smk = data.get('smoking_status', 'never smoked')
        if f'smoking_status_{smk}' in row:
            row[f'smoking_status_{smk}'] = 1.0

        df = pd.DataFrame([row])
        model = d['model']
        try:
            prob = float(model.predict_proba(df)[0][1])
        except Exception:
            b = model.get_booster()
            dmat = xgb.DMatrix(df)
            prob = float(b.predict(dmat)[0])

        th = float(d.get('threshold', 0.5))
        is_positive = prob >= th

        if prob < 0.25:
            severity = "Normal Cerebrovascular Status"
            badge_class = "success"
        elif prob < th:
            severity = "Moderate Stroke Vulnerability"
            badge_class = "warning"
        elif prob < 0.70:
            severity = "High Stroke Risk"
            badge_class = "danger"
        else:
            severity = "Emergency Stroke Warning"
            badge_class = "critical"

        return {
            'probability': round(prob, 4),
            'probability_pct': round(prob * 100, 1),
            'threshold': th,
            'prediction': int(is_positive),
            'diagnosis': 'High Stroke Risk Detected' if is_positive else 'Normal / Low Stroke Risk',
            'severity': severity,
            'badge_class': badge_class,
            'accuracy': 82.29
        }

    # -------------------------------------------------------------
    # 4. LIVER DISEASE PREDICTION
    # -------------------------------------------------------------
    def predict_liver(self, data):
        d = self.models['liver']
        cols = d['columns']
        row = {c: 0.0 for c in cols}
        row['Unnamed: 0'] = 1.0
        row['Age'] = float(data.get('Age', 45))
        row['Sex'] = 1.0 if str(data.get('Sex')).lower() in ['male', 'm', '1'] else 0.0

        for k in ['ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT']:
            if k in data:
                row[k] = float(data[k])

        df = pd.DataFrame([row])
        model = d['model']
        pred_cls = int(model.predict(df)[0])
        target_str = d['target_map'].get(pred_cls, f'Class {pred_cls}')
        probs = [float(p) for p in model.predict_proba(df)[0]]

        if pred_cls == 0:
            severity = "Normal / Healthy Blood Donor"
            badge_class = "success"
        elif pred_cls == 1:
            severity = "Suspect Donor / Mild Anomaly"
            badge_class = "warning"
        elif pred_cls in [2, 3]:
            severity = "High Risk (Hepatitis / Fibrosis)"
            badge_class = "danger"
        else:
            severity = "Emergency Risk (Cirrhosis)"
            badge_class = "critical"

        return {
            'class_id': pred_cls,
            'diagnosis': target_str,
            'probabilities': [round(p, 4) for p in probs],
            'confidence_pct': round(max(probs) * 100, 1),
            'severity': severity,
            'badge_class': badge_class,
            'accuracy': 99.19
        }

    # -------------------------------------------------------------
    # 5. KIDNEY DISEASE PREDICTION
    # -------------------------------------------------------------
    def predict_kidney(self, data):
        model = self.models["kidney"]
        cols = list(model.feature_names_in_)

        binary_fields = {
            "rbc": {"normal": 0, "abnormal": 1},
            "pc": {"normal": 0, "abnormal": 1},
            "pcc": {"notpresent": 0, "not present": 0, "present": 1},
            "ba": {"notpresent": 0, "not present": 0, "present": 1},
            "htn": {"no": 0, "yes": 1},
            "dm": {"no": 0, "yes": 1},
            "cad": {"no": 0, "yes": 1},
            "appet": {"good": 0, "poor": 1},
            "pe": {"no": 0, "yes": 1},
            "ane": {"no": 0, "yes": 1},
        }

        row = {}

        for col in cols:
            raw = data.get(col)

            if raw is None or str(raw).strip() == "":
                raise ValueError(f"Missing kidney input: {col}")

            text = str(raw).strip().lower()

            if col in binary_fields and text in binary_fields[col]:
                value = float(binary_fields[col][text])
            else:
                try:
                    value = float(raw)
                except (TypeError, ValueError):
                    raise ValueError(f"Invalid kidney input: {col}")

            if not np.isfinite(value):
                raise ValueError(f"{col} must be a finite number.")

            if col in binary_fields and value not in (0, 1):
                raise ValueError(f"{col} must be 0 or 1.")

            row[col] = value

        # Convert your form's encoding to the existing model's encoding.
        row["rbc"] = 1.0 - row["rbc"]
        row["pc"] = 1.0 - row["pc"]
        row["dm"] = 4.0 if row["dm"] == 1 else 3.0
        row["cad"] = 2.0 if row["cad"] == 1 else 1.0

        df = pd.DataFrame([row], columns=cols)

        classes = [int(c) for c in model.classes_]

        if set(classes) != {0, 1, 2}:
            raise ValueError(
                "This function requires your original kidney model."
            )

        pred_cls = int(model.predict(df)[0])
        probs = [float(p) for p in model.predict_proba(df)[0]]
        prob_by_class = dict(zip(classes, probs))

        # Original model: 0 = CKD, 1 = CKD with trailing tab, 2 = No CKD.
        ckd_probability = prob_by_class[0] + prob_by_class[1]
        no_ckd_probability = prob_by_class[2]
        is_ckd = pred_cls in (0, 1)

        diagnosis = "CKD predicted" if is_ckd else "No CKD predicted"
        predicted_score = (
            ckd_probability if is_ckd else no_ckd_probability
        )

        return {
            "class_id": pred_cls,
            "prediction": int(is_ckd),
            "diagnosis": diagnosis,
            "probabilities": [round(p, 4) for p in probs],
            "probability_classes": classes,
            "ckd_probability": round(ckd_probability, 4),
            "no_ckd_probability": round(no_ckd_probability, 4),
            "confidence_pct": round(predicted_score * 100, 1),
            "severity": (
                "Severity not assessed" if is_ckd else "No CKD predicted"
            ),
            "badge_class": "warning" if is_ckd else "success",
        }
    # -------------------------------------------------------------
    # 6. BREAST CANCER PREDICTION
    # -------------------------------------------------------------
    def predict_breast_cancer(self, data):
        model = self.models['breast_cancer']
        cols = list(model.feature_names_in_)
        row = {}
        
        # Populate columns
        for c in cols:
            if c in data:
                row[c] = float(data[c])
            else:
                # Top 7 user mean fields mapping
                clean_col = c.replace('_mean', '').replace(' ', '').lower()
                matched = False
                for k, v in data.items():
                    clean_k = k.replace(' ', '').lower()
                    if clean_k == clean_col or clean_k in clean_col:
                        row[c] = float(v)
                        matched = True
                        break
                if not matched:
                    row[c] = 10.0 if 'mean' in c else 0.0

        df = pd.DataFrame([row])
        probs = model.predict_proba(df)[0]
        prob_malignant = float(probs[1]) if len(probs) > 1 else float(probs[0])
        pred = int(prob_malignant >= 0.5)

        if prob_malignant < 0.30:
            severity = "Normal / Benign Characteristics"
            badge_class = "success"
        elif prob_malignant < 0.50:
            severity = "Moderate / Borderline Watch"
            badge_class = "warning"
        elif prob_malignant < 0.80:
            severity = "High Malignancy Risk"
            badge_class = "danger"
        else:
            severity = "Emergency Malignant Tissue Warning"
            badge_class = "critical"

        return {
            'probability': round(prob_malignant, 4),
            'probability_pct': round(prob_malignant * 100, 1),
            'prediction': pred,
            'diagnosis': 'Malignant Tissue Risk Detected' if pred == 1 else 'Benign / Normal Tissue',
            'severity': severity,
            'badge_class': badge_class,
            'accuracy': 96.49
        }

    # -------------------------------------------------------------
    # 7. OBESITY LEVEL PREDICTION
    # -------------------------------------------------------------
    def predict_obesity(self, data):
        model = self.models['obesity']
        cols = list(model.feature_names_in_)
        row = {c: 0.0 for c in cols}
        
        age = float(data.get('Age', 25))
        height = float(data.get('Height', 1.70))
        weight = float(data.get('Weight', 70))
        
        if not np.isfinite([age, height, weight]).all() or height <= 0 or weight <= 0:
            raise ValueError('Height and weight must be positive finite numbers; height is in meters.')

        row['Age'] = age
        row['Height'] = height
        row['Weight'] = weight
        row['FCVC'] = float(data.get('FCVC', 2))
        row['NCP'] = float(data.get('NCP', 3))
        row['CH2O'] = float(data.get('CH2O', 2))
        row['FAF'] = float(data.get('FAF', 1))
        row['TUE'] = float(data.get('TUE', 1))

        if str(data.get('Gender')).lower() in ['male', 'm']:
            row['Gender_Male'] = 1.0
        if str(data.get('family_history_with_overweight')).lower() in ['yes', '1', 'true']:
            row['family_history_with_overweight_yes'] = 1.0
        if str(data.get('FAVC')).lower() in ['yes', '1', 'true']:
            row['FAVC_yes'] = 1.0

        caec = data.get('CAEC', 'Sometimes')
        if f'CAEC_{caec}' in row:
            row[f'CAEC_{caec}'] = 1.0

        if str(data.get('SMOKE')).lower() in ['yes', '1', 'true']:
            row['SMOKE_yes'] = 1.0
        if str(data.get('SCC')).lower() in ['yes', '1', 'true']:
            row['SCC_yes'] = 1.0

        calc = data.get('CALC', 'Sometimes')
        if f'CALC_{calc}' in row:
            row[f'CALC_{calc}'] = 1.0

        mtrans = data.get('MTRANS', 'Public_Transportation')
        if f'MTRANS_{mtrans}' in row:
            row[f'MTRANS_{mtrans}'] = 1.0

        # Match the exact training feature order and class-probability order.
        df = pd.DataFrame([row], columns=cols)
        pred_level = str(model.predict(df)[0])
        probabilities = model.predict_proba(df)[0]
        class_probabilities = {
            str(label): float(prob) for label, prob in zip(model.classes_, probabilities)
        }
        confidence = class_probabilities[pred_level]
        bmi = round(weight / (height * height), 1)
        level_clean = pred_level.replace('_', ' ')
        badges = {
            'Insufficient_Weight': 'warning', 'Normal_Weight': 'success',
            'Overweight_Level_I': 'warning', 'Overweight_Level_II': 'warning',
            'Obesity_Type_I': 'danger', 'Obesity_Type_II': 'danger',
            'Obesity_Type_III': 'danger'
        }
        return {
            'obesity_level': level_clean,
            'raw_class': pred_level,
            'calculated_bmi': bmi,
            'confidence_pct': round(confidence * 100, 2),
            'class_probabilities_pct': {
                label.replace('_', ' '): round(prob * 100, 2)
                for label, prob in class_probabilities.items()
            },
            'severity': level_clean,
            'badge_class': badges.get(pred_level, 'info'),
            'accuracy': 97.36
        }
