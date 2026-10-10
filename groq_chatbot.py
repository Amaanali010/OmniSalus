import os
import json
from groq import Groq

PAGE_CONTEXTS = {
    'heart': {
        'title': 'Heart Disease Risk Diagnostics',
        'models': ['Logistic Regression (ROC-AUC: 83.23%)', 'LightGBM (ROC-AUC: 83.66%)', 'XGBoost (ROC-AUC: 83.64%)'],
        'fields': [
            'Sex', 'Age Category', 'Race/Ethnicity', 'Height', 'Weight', 'BMI',
            'Average Sleep per night', 'General Health', 'Days of Poor Physical Health (last 30d)',
            'Days of Poor Mental Health (last 30d)', 'Diabetic status', 'Difficulty Walking',
            'Kidney Disease', 'Ever Had Stroke', 'Asthma', 'Skin Cancer', 'Smoked 100+ cigarettes',
            'Heavy Alcohol Drinking', 'Physical Activity (last 30d)'
        ],
        'keywords': ['heart', 'cardiac', 'lgbm', 'lightgbm', 'logreg', 'logistic', 'xgboost', 'bmi', 'sleep', 'physicalhealth', 'mentalhealth', 'chest', 'pulse', 'bp', 'blood pressure', 'cholesterol', 'smoking', 'alcohol', 'walking', 'race', 'sex', 'age', 'genhealth', 'diabetic', 'asthma', 'skin cancer', 'stroke', 'roc-auc', 'threshold', 'risk', 'probability']
    },
    'diabetes': {
        'title': 'Diabetes Risk Diagnostics',
        'models': ['XGBoostTuned (Accuracy: 70.8%)'],
        'fields': [
            'HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke', 'HeartDiseaseorAttack',
            'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost',
            'GenHlth', 'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education', 'Income'
        ],
        'keywords': ['diabetes', 'diabetic', 'glycemic', 'glucose', 'insulin', 'sugar', 'highbp', 'highchol', 'cholcheck', 'bmi', 'smoker', 'fruits', 'veggies', 'alcohol', 'healthcare', 'genhlth', 'menthlth', 'physhlth', 'diffwalk', 'income', 'education', 'xgboosttuned', '70.8%']
    },
    'stroke': {
        'title': 'Stroke Vulnerability Diagnostics',
        'models': ['XGBoost (Accuracy: 82.29%)'],
        'fields': [
            'Age', 'Hypertension', 'Heart Disease', 'Average Glucose Level', 'BMI', 'Gender',
            'Ever Married', 'Work Type', 'Residence Type', 'Smoking Status'
        ],
        'keywords': ['stroke', 'brain', 'cerebrovascular', 'hypertension', 'glucose', 'avg_glucose_level', 'bmi', 'gender', 'married', 'work', 'work_type', 'residence', 'smoking', 'xgboost', '82.29%']
    },
    'liver': {
        'title': 'Liver Health Diagnostics',
        'models': ['HistGradientBoostingClassifier (Accuracy: 99.19%)'],
        'fields': [
            'Age', 'Gender', 'Total Bilirubin (BIL)', 'Direct Bilirubin', 'Alkaline Phosphotase (ALP)',
            'Alamine Aminotransferase (ALT/Sgpt)', 'Aspartate Aminotransferase (AST/Sgot)',
            'Total Proteins (PROT)', 'Albumin (ALB)', 'Albumin and Globulin Ratio (A/G Ratio)', 'CHE', 'CHOL', 'CREA', 'GGT'
        ],
        'keywords': ['liver', 'hepatic', 'bilirubin', 'bil', 'alp', 'alt', 'sgpt', 'ast', 'sgot', 'prot', 'alb', 'che', 'chol', 'crea', 'ggt', 'hepatitis', 'fibrosis', 'cirrhosis', 'donor', 'histgradientboosting', '99.19%']
    },
    'kidney': {
        'title': 'Kidney & Renal Diagnostics',
        'models': ['RandomForestClassifier (Accuracy: 100%)'],
        'fields': [
            'Age', 'Blood Pressure (BP)', 'Specific Gravity (SG)', 'Albumin (AL)', 'Sugar (SU)',
            'Blood Glucose Random (BGR)', 'Blood Urea (BU)', 'Serum Creatinine (SC)', 'Sodium (SOD)',
            'Potassium (POT)', 'Hemoglobin (HEMO)', 'Packed Cell Volume (PCV)', 'WBC Count (WC)',
            'RBC Count (RC)', 'Hypertension (HTN)', 'Diabetes Mellitus (DM)', 'CAD', 'Appetite', 'Pedal Edema (PE)', 'Anemia (ANE)'
        ],
        'keywords': ['kidney', 'renal', 'ckd', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 'creatinine', 'sod', 'pot', 'hemo', 'hemoglobin', 'pcv', 'wc', 'rc', 'htn', 'dm', 'cad', 'appetite', 'edema', 'anemia', 'randomforest', '100%']
    },
    'breast-cancer': {
        'title': 'Breast Cancer Diagnostics',
        'models': ['RandomForestClassifier (Accuracy: 96.49%)'],
        'fields': [
            'Radius Mean', 'Texture Mean', 'Perimeter Mean', 'Area Mean',
            'Smoothness Mean', 'Compactness Mean', 'Concavity Mean'
        ],
        'keywords': ['breast', 'cancer', 'tumor', 'benign', 'malignant', 'radius', 'texture', 'perimeter', 'area', 'smoothness', 'compactness', 'concavity', 'biopsy', 'randomforest', '96.49%']
    },
    'obesity': {
        'title': 'Obesity & Body Mass Classification',
        'models': ['HistGradientBoostingClassifier (Accuracy: 97.36%)'],
        'fields': [
            'Gender', 'Age', 'Height (m)', 'Weight (kg)', 'Family History with Overweight',
            'High Caloric Food (FAVC)', 'Vegetable Consumption (FCVC)', 'Number of Main Meals (NCP)',
            'Consumption between Meals (CAEC)', 'Smoke', 'Daily Water Intake (CH2O)',
            'Physical Activity (FAF)', 'Technology Device Time (TUE)', 'Transportation (MTRANS)'
        ],
        'keywords': ['obesity', 'overweight', 'bmi', 'weight', 'height', 'favc', 'fcvc', 'ncp', 'caec', 'smoke', 'ch2o', 'water', 'faf', 'tue', 'mtrans', 'transport', 'histgradientboosting', '97.36%']
    }
}

RESTRICTED_MSG = "I can only help you with information related to this page and its model."

POPULAR_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

def get_candidate_models(requested_model=None, client=None):
    candidates = []
    if requested_model and requested_model != 'auto':
        candidates.append(requested_model)

    if client:
        try:
            m_list = client.models.list()
            active_ids = [m.id for m in m_list.data if getattr(m, 'active', True)]
            for p in POPULAR_GROQ_MODELS:
                if p in active_ids and p not in candidates:
                    candidates.append(p)
            for m in active_ids:
                if m not in candidates and not any(x in m for x in ['whisper', 'guard', 'tts', 'embed']):
                    candidates.append(m)
        except Exception as e:
            print(f"[GroqChatbot] Note: client.models.list() failed: {e}")

    for p in POPULAR_GROQ_MODELS:
        if p not in candidates:
            candidates.append(p)

    return candidates

class GroqChatbot:
    def __init__(self):
        self.active_verified_model = None

    def _is_query_related(self, page_id, query):
        if page_id not in PAGE_CONTEXTS:
            return False

        q_lower = query.lower().strip()

        # Automatic post-prediction triggers, greetings, or report explanation requests
        report_and_general_terms = [
            'auto_post_predict_analysis', 'hi', 'hello', 'hey', 'help', 'explain',
            'what is this page', 'how to use', 'report', 'result', 'score', 'risk',
            'diagnosis', 'probability', 'detail', 'meaning', 'summary',
            'kaisa', 'kya', 'meri', 'mera', 'batao', 'bataiye', 'suno', 'kaise',
            'doctor', 'symptom', 'lifestyle', 'diet', 'medicine', 'exercise',
            'precaution', 'guide', 'guidance', 'advice', 'test', 'value', 'parameter',
            'what should i do', 'why', 'how', 'normal', 'high', 'low', 'severe',
            'danger', 'alert', 'status', 'consult', 'factor', 'metrics'
        ]

        if any(term in q_lower for term in report_and_general_terms):
            return True

        keywords = PAGE_CONTEXTS[page_id]['keywords']
        if any(kw in q_lower for kw in keywords):
            return True

        return len(q_lower) > 2

    def _build_clinical_report_context(self, ctx, user_inputs, model_result):
        if not model_result and not user_inputs:
            return "No patient assessment data submitted yet. The patient is asking general questions about this module."

        sections = []
        sections.append(f"DIAGNOSTIC SUITE: {ctx['title']}")

        if model_result:
            diag = model_result.get('diagnosis') or model_result.get('obesity_level') or 'Assessment Evaluated'
            severity = model_result.get('severity') or 'Evaluated'
            prob = model_result.get('probability_pct', model_result.get('confidence_pct', model_result.get('consensus_prob_pct')))
            prob_str = f"{prob}%" if prob is not None else "N/A"

            sections.append(f"CALCULATED RISK SCORE: {prob_str}")
            sections.append(f"SEVERITY TIER: {severity}")
            sections.append(f"DIAGNOSIS FINDING: {diag}")

            if 'calculated_bmi' in model_result and model_result['calculated_bmi']:
                sections.append(f"CALCULATED BMI: {model_result['calculated_bmi']}")

            if 'lgbm' in model_result:
                l = model_result['lgbm']
                x = model_result.get('xgb', {})
                lr = model_result.get('logreg', {})
                sections.append("MULTI-MODEL BREAKDOWN:")
                sections.append(f"  • LightGBM: {l.get('probability_pct')}% ({l.get('severity')})")
                sections.append(f"  • XGBoost: {x.get('probability_pct')}% ({x.get('severity')})")
                sections.append(f"  • Logistic Regression: {lr.get('probability_pct')}% ({lr.get('severity')})")

            if 'class_probabilities_pct' in model_result:
                probs = model_result['class_probabilities_pct']
                sections.append("CATEGORY PROBABILITIES: " + ", ".join([f"{k}: {v}%" for k, v in probs.items()]))
        else:
            sections.append("ASSESSMENT STATUS: Active form fields filled by patient; calculation pending submission.")

        if user_inputs:
            sections.append("PATIENT SUBMITTED BIOMARKERS & CLINICAL INPUTS:")
            for k, v in user_inputs.items():
                if k != 'model_variant':
                    sections.append(f"  • {k}: {v}")

        return "\n".join(sections)

    def get_response(self, page_id, user_message, user_inputs=None, model_result=None, groq_api_key=None, history=None, model=None):
        if page_id not in PAGE_CONTEXTS or page_id == 'index' or page_id == 'home':
            return RESTRICTED_MSG

        if not self._is_query_related(page_id, user_message):
            return RESTRICTED_MSG

        ctx = PAGE_CONTEXTS[page_id]
        is_auto_analysis = 'auto_post_predict_analysis' in user_message.lower()
        api_key = (groq_api_key or '').strip() or (os.environ.get('GROQ_API_KEY') or '').strip()
        if api_key:
            try:
                res = self._call_groq_api(api_key, page_id, ctx, user_message, user_inputs, model_result, is_auto_analysis, history, model=model)
                if res:
                    return res
            except Exception as e:
                print(f"[GroqChatbot] API call error: {e}")

        return self._generate_rule_fallback(page_id, ctx, user_message, user_inputs, model_result, is_auto_analysis)

    def _call_groq_api(self, api_key, page_id, ctx, user_message, user_inputs, model_result, is_auto_analysis, history=None, model=None):
        report_context = self._build_clinical_report_context(ctx, user_inputs, model_result)

        if is_auto_analysis:
            user_prompt = f"""The patient has just completed their assessment for {ctx['title']}.
Please provide a comprehensive, structured personalized diagnostic briefing:
1. State the calculated risk score / diagnosis and its severity tier ({model_result.get('severity', 'Evaluated') if model_result else 'Evaluated'}).
2. Highlight key risk contributors from their submitted biomarkers (which values are protective vs elevated).
3. Provide 3 clear actionable medical and lifestyle recommendations.
4. Invite them to ask any follow-up questions about their metrics or report."""
        else:
            user_prompt = user_message

        system_prompt = f"""You are Omni, the specialized AI Clinical Diagnostic Companion for the '{ctx['title']}' module on the OmniSalus Platform.

==================== CURRENT PATIENT CLINICAL REPORT & BIOMARKERS ====================
{report_context}
======================================================================================

STRICT OPERATING DIRECTIVES:
1. CITING PATIENT REPORT: You have access to the patient's exact clinical diagnostic report above. Whenever the patient asks about their report, risk, health, scores, or lifestyle advice, ALWAYS directly reference and quote their specific calculated results, biomarkers, and numbers. DO NOT speak in generic terms.
2. EXPLAIN RISK DRIVERS: Identify and explain which specific inputs from their report (e.g., BMI, smoking, sleep hours, glucose, blood pressure) are elevating their risk or keeping them in a safe zone.
3. ACTIONABLE CLINICAL GUIDANCE: Give clear, structured, empathetic health recommendations (lifestyle habits, nutrition, monitoring metrics, questions to ask their doctor).
4. MULTILINGUAL & URDU / ROMAN URDU PROFICIENCY:
   - The user may ask questions in English, Urdu, or Roman Urdu (e.g., "meri report explain karo", "mera score kitna serious hai", "kya mujhe doctor ke paas jana chahiye?").
   - Understand their queries fluently and answer in their chosen language (e.g. natural Roman Urdu or clear English) with empathy and professional medical precision.
5. PROFESSIONAL MEDICAL DISCLAIMER: Remind the user that OmniSalus provides educational machine learning estimates, and they should review this report with a qualified healthcare professional.
"""

        messages = [{"role": "system", "content": system_prompt}]

        if history and isinstance(history, list):
            for turn in history[-8:]:
                if isinstance(turn, dict) and turn.get('role') in ['user', 'assistant'] and turn.get('content'):
                    # Avoid repeating raw system commands in history
                    if 'auto_post_predict_analysis' not in turn.get('content', ''):
                        messages.append({"role": turn['role'], "content": str(turn['content'])})

        messages.append({"role": "user", "content": user_prompt})

        try:
            client = Groq(api_key=api_key)
            candidates = get_candidate_models(model or self.active_verified_model, client=client)

            last_model_err = None
            for m in candidates:
                try:
                    chat_completion = client.chat.completions.create(
                        messages=messages,
                        model=m,
                        temperature=0.35,
                        max_tokens=700
                    )
                    if chat_completion and chat_completion.choices:
                        self.active_verified_model = m
                        return chat_completion.choices[0].message.content
                except Exception as m_err:
                    err_str = str(m_err).lower()
                    if 'model_not_found' in err_str or 'does not exist' in err_str or '404' in err_str or 'not have access' in err_str:
                        print(f"[GroqChatbot] Model '{m}' not accessible on this account. Trying next candidate...")
                        last_model_err = m_err
                        continue
                    raise m_err

            if last_model_err:
                raise last_model_err
        except Exception as e:
            print(f"[GroqChatbot] Groq SDK error: {e}")
            raise e
        return None

    def _generate_rule_fallback(self, page_id, ctx, user_message, user_inputs, model_result, is_auto_analysis=False):
        msg_lower = (user_message or '').lower().strip()
        user_inputs = user_inputs or {}

        # Extract primary metrics from model result
        diag = (model_result.get('diagnosis') or model_result.get('obesity_level') or 'Assessment Evaluated') if model_result else None
        severity = model_result.get('severity') if model_result else None
        prob = (model_result.get('probability_pct', model_result.get('confidence_pct', model_result.get('consensus_prob_pct')))) if model_result else None
        prob_str = f"{prob}%" if prob is not None else "N/A"
        bmi = user_inputs.get('BMI') or (model_result.get('calculated_bmi') if model_result else None)

        is_urdu = any(w in msg_lower for w in ['kya', 'kaisa', 'kaise', 'meri', 'mera', 'batao', 'bataiye', 'karo', 'mujhe', 'theek', 'khatra', 'doctor', 'dawa', 'ilaj', 'khana'])

        # 1. User asks about Score / Risk / Seriousness / Meaning
        if any(w in msg_lower for w in ['score', 'risk', 'probability', 'result', 'status', 'level', 'meaning', 'matlab', 'kaisa', 'khatra', 'safe', 'normal', 'high', 'low', 'serious', 'danger', 'percent']):
            if model_result:
                is_low_risk = (prob is not None and prob < 35.0) or ('low' in str(severity).lower()) or ('normal' in str(severity).lower()) or ('benign' in str(severity).lower())
                if is_urdu:
                    if is_low_risk:
                        return f"Aapki assessment report ke mutabiq aapka calculated score **{prob_str}** hai, jo ke **{severity}** category mein ata hai (Tashkhees: **{diag}**).\n\nAapke darj karda inputs safe aur protective range mein hain. Model ke mutabiq koi fori khatra detect nahi hua. Isi tarah apni healthy routine continue rakhein!"
                    else:
                        return f"Aapki assessment report ke mutabiq aapka calculated score **{prob_str}** hai, jo ke **{severity}** category mein ata hai (Tashkhees: **{diag}**).\n\nModel ne elevated risk identify kiya hai. Hamara mashwara hai ke aap in calculated metrics ko apne physician/doctor ke sath review karein."
                else:
                    if is_low_risk:
                        return f"Based on your assessment report, your calculated score is **{prob_str}** (**{severity}**), with diagnosis: **{diag}**.\n\nYour submitted metrics represent protective, low-risk indicators. The models do not detect elevated danger. Continue maintaining your current healthy habits and schedule routine wellness checkups."
                    else:
                        return f"Based on your assessment report, your calculated score is **{prob_str}** (**{severity}**), with diagnosis: **{diag}**.\n\nThe algorithm detected elevated risk markers based on your submitted inputs. We recommend discussing these findings and scheduling a follow-up consultation with your healthcare provider."
            else:
                return f"You haven't run the assessment yet. Please fill out the form fields on the left and click 'Compute Risk Score' to calculate your {ctx['title']} metrics!"

        # 2. User asks about Diet / Food / Nutrition
        if any(w in msg_lower for w in ['diet', 'food', 'eat', 'nutrition', 'khana', 'sugar', 'salt', 'oil', 'lunch', 'dinner', 'breakfast']):
            bmi_mention = f" (calculated BMI: {bmi})" if bmi else ""
            if is_urdu:
                return f"**{ctx['title']} ke liye Khoraak (Diet) ka Mashwara**{bmi_mention}:\n\n- **Sabziyan aur Fiber**: Taaza sabziyan, daalein aur whole grains ka istemal barhayen.\n- **Namak aur Meetha**: Namak (sodium) aur processed refined cheeni kam se kam karein.\n- **Healthy Fats**: Talay hue khano se parhez karein aur olive oil ya nuts ka munasib istemal karein.\n- **Pani**: Din bhar paani ka munasib intake banaye rakhein."
            else:
                return f"**Dietary Guidance for {ctx['title']}**{bmi_mention}:\n\n- **Whole Foods**: Prioritize fresh vegetables, dietary fiber, legumes, and lean proteins.\n- **Sodium & Sugar Control**: Limit processed snacks, excess sodium, and refined sugars.\n- **Healthy Fats**: Incorporate heart-healthy monounsaturated fats while eliminating trans fats.\n- **Hydration**: Maintain steady daily hydration for optimal cellular and metabolic regulation."

        # 3. User asks about Exercise / Physical Activity
        if any(w in msg_lower for w in ['exercise', 'walk', 'activity', 'varzish', 'gym', 'workout', 'running', 'steps']):
            if is_urdu:
                return f"**{ctx['title']} ke liye Physical Activity**:\n\n- Rozana 30 minute brisk walking (tez chalna) ya moderate cardio bohat mufeed hai.\n- Haftay mein kam az kam 150 minute moderate exercise ka target rakhein.\n- Lambay arsay tak ek hi jagah bethe rehne se parhez karein."
            else:
                return f"**Physical Activity Recommendations for {ctx['title']}**:\n\n- Target at least 150 minutes of moderate aerobic exercise (brisk walking, cycling) per week.\n- Add 2 light resistance or stretching sessions weekly.\n- Avoid prolonged sedentary periods to keep cardiovascular and metabolic circulation optimal."

        # 4. User asks about Doctor / Medical Consultation
        if any(w in msg_lower for w in ['doctor', 'consult', 'hospital', 'dawa', 'medicine', 'ilaj', 'checkup', 'test', 'clinic']):
            if is_urdu:
                return f"**Medical Follow-up ka Mashwara**:\n\n- Yeh assessment ek educational AI prototype hai. Agar aapka score **{prob_str}** ({severity or 'Evaluated'}) hai aur aapko koi takleef mehsoos hoti hai, to doctor se zaroor mashwara karein.\n- Routine blood pressure, blood glucose, aur lipid panel tests karwana faidamand rehta hai."
            else:
                return f"**Clinical Consultation Guidance**:\n\n- With your current result of **{prob_str}** (**{severity or 'Evaluated'}**), discuss these findings with your physician.\n- Key routine screenings to review include blood pressure, fasting lipid panels, and standard metabolic profiles."

        # 5. User specifically asks to summarize or explain the complete report
        if any(w in msg_lower for w in ['summary', 'khulasa', 'overview', 'samjhao', 'explain my report', 'report samjhao', 'meri report']):
            if model_result:
                inputs_items = [f"- **{k}**: `{v}`" for k, v in list(user_inputs.items())[:6] if k != 'model_variant']
                inputs_summary = "\n".join(inputs_items)
                if is_urdu:
                    return f"**Aapki {ctx['title']} Report Ka Khulasa**:\n\n- **Diagnosis**: **{diag}**\n- **Calculated Score**: `{prob_str}` ({severity})\n\n**Ahem Inputs**:\n{inputs_summary}\n\nAap is report ke mutaliq koi bhi specific sawal (maslan diet, varzish, ya score) pooch sakte hain!"
                else:
                    return f"**Summary of your {ctx['title']} Report**:\n\n- **Diagnostic Finding**: **{diag}**\n- **Calculated Score**: `{prob_str}` ({severity})\n\n**Key Submitted Metrics**:\n{inputs_summary}\n\nFeel free to ask specific questions about any of your biomarkers or lifestyle recommendations!"

        # Default conversational answer:
        if is_urdu:
            return f"Aapka calculated score **{prob_str}** ({severity or 'Normal'}) hai. Aap mujhse apni report, khoraak (diet), varzish (exercise), ya kisi bhi biomarker ke baray mein specific sawal pooch sakte hain!"
        else:
            return f"Based on your {ctx['title']} assessment, your calculated score is **{prob_str}** ({severity or 'Normal'}). What specific question can I answer for you regarding your results, diet, or lifestyle recommendations?"

