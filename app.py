import os
from functools import wraps
from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer, BadSignature
from pdf_report import build_report
from flask import Flask, render_template, request, jsonify, Response, session, redirect, url_for
from model_engine import ModelEngine
from groq_chatbot import GroqChatbot
from db_manager import (
    init_db, save_assessment, get_assessments, get_assessment_by_id,
    delete_assessment, get_stats_summary, export_all_records_csv
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('OMNISALUS_SECRET_KEY') or os.urandom(32)
report_signer = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='assessment-report')

# Hardcoded Admin Authentication Credentials
ADMIN_USERNAME = os.environ.get('OMNI_ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.environ.get('OMNI_ADMIN_PASSWORD', 'admin123')

def is_admin_authenticated():
    return session.get('admin_logged_in') is True

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_authenticated():
            if request.path.startswith('/api/admin/'):
                return jsonify({'status': 'error', 'message': 'Unauthorized. Admin authentication required.'}), 401
            return redirect(url_for('admin_login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# Initialize SQLite Database
init_db()

# Initialize Model Engine & Chatbot Engine
engine = ModelEngine()
chatbot = GroqChatbot()

# -------------------------------------------------------------------
# PAGE ROUTES
# -------------------------------------------------------------------

@app.route('/')
def index():
    """Home Page - Command Center Dashboard (No Chatbot)"""
    return render_template('index.html', page_id='index', title="OmniSalus - AI Health Command Center")

@app.route('/heart')
def heart():
    return render_template('heart.html', page_id='heart', title="Heart Disease Risk Calculator")

@app.route('/diabetes')
def diabetes():
    return render_template('diabetes.html', page_id='diabetes', title="Diabetes Risk Calculator")

@app.route('/stroke')
def stroke():
    return render_template('stroke.html', page_id='stroke', title="Stroke Vulnerability Calculator")

@app.route('/liver')
def liver():
    return render_template('liver.html', page_id='liver', title="Liver Health Diagnostics")

@app.route('/kidney')
def kidney():
    return render_template('kidney.html', page_id='kidney', title="Kidney & Renal Disease Calculator")

@app.route('/breast-cancer')
def breast_cancer():
    return render_template('breast_cancer.html', page_id='breast-cancer', title="Breast Cancer Risk Calculator")

@app.route('/obesity')
def obesity():
    return render_template('obesity.html', page_id='obesity', title="Obesity Level Classifier")

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_authenticated():
        return redirect(url_for('admin_panel'))
    error_msg = None
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('admin_panel'))
        error_msg = f"Invalid Admin ID or Password. Default is '{ADMIN_USERNAME}' / '{ADMIN_PASSWORD}'."
    return render_template('admin_login.html', page_id='admin-login', title="Admin Login - OmniSalus", error=error_msg)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin.html', page_id='admin', title="OmniSalus - Unified Clinical Admin Panel")

# -------------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------------

@app.route('/api/predict/<model_type>', methods=['POST'])
def predict(model_type):
    data = request.get_json() or {}
    try:
        if model_type == 'heart':
            model_variant = data.get('model_variant', 'all')
            if model_variant == 'all':
                res = engine.predict_heart_all(data)
            else:
                res = engine.predict_heart(data, model_variant)
        elif model_type == 'diabetes':
            res = engine.predict_diabetes(data)
        elif model_type == 'stroke':
            res = engine.predict_stroke(data)
        elif model_type == 'liver':
            res = engine.predict_liver(data)
        elif model_type == 'kidney':
            res = engine.predict_kidney(data)
        elif model_type == 'breast-cancer':
            res = engine.predict_breast_cancer(data)
        elif model_type == 'obesity':
            res = engine.predict_obesity(data)
        else:
            return jsonify({'error': f'Unknown model type: {model_type}'}), 400

        # Save assessment to SQLite database
        record_id = None
        try:
            record_id = save_assessment(model_type, data, res, ip_address=request.remote_addr)
        except Exception as db_err:
            print(f"[Database Error] Could not save assessment: {db_err}")

        snapshot = {'model_type': model_type, 'inputs': data, 'result': res, 'created_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
        return jsonify({
            'status': 'success',
            'result': res,
            'record_id': record_id,
            'report_token': report_signer.dumps(snapshot)
        })
    except Exception as e:
        print(f"[API Predict Error] {model_type}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/report', methods=['POST'])
def download_report():
    try:
        snapshot = report_signer.loads(request.form.get('report_token', ''), max_age=86400)
    except BadSignature:
        return 'Report expired or server restarted. Return to the assessment and run it again.', 400
    pdf = build_report(snapshot)
    filename = 'OmniSalus-' + snapshot['model_type'] + '-report.pdf'
    return Response(pdf, mimetype='application/pdf', headers={
        'Content-Disposition': 'attachment; filename="' + filename + '"',
        'Cache-Control': 'no-store'
    })

@app.after_request
def prevent_stale_ui(response):
    if response.mimetype in ('text/html', 'application/javascript', 'text/javascript', 'text/css'):
        response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/api/chat/page', methods=['POST'])
def chat_page():
    payload = request.get_json() or {}
    page_id = payload.get('page_id')
    user_message = payload.get('message', '')
    user_inputs = payload.get('user_inputs')
    model_result = payload.get('model_result')
    groq_key = payload.get('groq_api_key')
    history = payload.get('history') or []
    model = payload.get('model')

    if not page_id or page_id == 'index' or page_id == 'home':
        return jsonify({
            'status': 'success',
            'reply': "I can only help you with information related to this page and its model."
        })

    reply = chatbot.get_response(
        page_id=page_id,
        user_message=user_message,
        user_inputs=user_inputs,
        model_result=model_result,
        groq_api_key=groq_key,
        history=history,
        model=model
    )

    return jsonify({'status': 'success', 'reply': reply})

@app.route('/api/test-key', methods=['POST'])
def test_key():
    payload = request.get_json() or {}
    key = (payload.get('groq_api_key') or '').strip()
    if not key:
        key = os.environ.get('GROQ_API_KEY', '').strip()
    if not key:
        return jsonify({'status': 'error', 'message': 'API key cannot be empty. Please enter your Groq API key.'}), 400

    requested_model = (payload.get('model') or '').strip() or 'auto'

    try:
        from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError, APIError
        from groq_chatbot import get_candidate_models

        client = Groq(api_key=key)
        candidates = get_candidate_models(requested_model, client=client)

        verified_model = None
        last_error = None

        for m_id in candidates:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "user", "content": "Explain the importance of fast language models"}
                    ],
                    model=m_id,
                    max_tokens=20,
                )
                if chat_completion and chat_completion.choices:
                    verified_model = m_id
                    chatbot.active_verified_model = m_id
                    break
            except Exception as e:
                err_str = str(e).lower()
                if 'model_not_found' in err_str or 'does not exist' in err_str or '404' in err_str or 'not have access' in err_str:
                    last_error = e
                    continue
                # If authentication or rate limit error, raise immediately
                raise e

        if verified_model:
            if requested_model not in ['auto', ''] and requested_model != verified_model:
                msg = f"Groq connected successfully using '{verified_model}'! Note: '{requested_model}' is not accessible on your Groq tier, so '{verified_model}' was selected automatically."
            elif verified_model != "llama-3.3-70b-versatile":
                msg = f"Groq connected successfully using '{verified_model}'! (Active on your account tier)."
            else:
                msg = f"Groq connection verified successfully using {verified_model}!"

            return jsonify({
                'status': 'success',
                'message': msg,
                'verified_model': verified_model
            })

        if last_error:
            raise last_error

        return jsonify({'status': 'error', 'message': 'Groq API returned an empty response.'}), 500

    except AuthenticationError as e:
        return jsonify({'status': 'error', 'message': f'Authentication failed: Invalid Groq API key ({str(e)})'}), 401
    except RateLimitError as e:
        return jsonify({'status': 'error', 'message': f'Rate limit exceeded: {str(e)}'}), 429
    except APIConnectionError as e:
        return jsonify({'status': 'error', 'message': f'Connection failed to Groq: {str(e)}'}), 504
    except APIError as e:
        return jsonify({'status': 'error', 'message': f'Groq API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# -------------------------------------------------------------------
# ADMIN REST API ENDPOINTS
# -------------------------------------------------------------------

@app.route('/api/admin/records', methods=['GET'])
@admin_required
def admin_get_records():
    model_type = request.args.get('model_type', 'all')
    severity = request.args.get('severity', 'all')
    search = request.args.get('search', '')
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
    except ValueError:
        limit, offset = 100, 0
    records = get_assessments(model_type=model_type, severity=severity, search=search, limit=limit, offset=offset)
    return jsonify({'status': 'success', 'records': records, 'count': len(records)})

@app.route('/api/admin/records/<int:record_id>', methods=['GET'])
@admin_required
def admin_get_record_detail(record_id):
    rec = get_assessment_by_id(record_id)
    if not rec:
        return jsonify({'status': 'error', 'message': 'Record not found'}), 404
    return jsonify({'status': 'success', 'record': rec})

@app.route('/api/admin/records/<int:record_id>', methods=['DELETE'])
@admin_required
def admin_delete_record(record_id):
    deleted = delete_assessment(record_id)
    if not deleted:
        return jsonify({'status': 'error', 'message': 'Record not found or could not be deleted'}), 404
    return jsonify({'status': 'success', 'message': f'Record #{record_id} deleted successfully.'})

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_get_stats():
    stats = get_stats_summary()
    return jsonify({'status': 'success', 'stats': stats})

@app.route('/api/admin/export', methods=['GET'])
@admin_required
def admin_export_csv():
    csv_data = export_all_records_csv()
    filename = f"omnisalus-patient-assessments-{datetime.now().strftime('%Y%m%d-%H%M')}.csv"
    return Response(csv_data, mimetype='text/csv', headers={
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Cache-Control': 'no-store'
    })

@app.route('/api/health-check')
def health_check():
    return jsonify({
        'status': 'online',
        'platform': 'OmniSalus',
        'models_loaded': len(engine.models),
        'version': '1.0.0-hackathon'
    })

if __name__ == '__main__':
    print("[OmniSalus] Starting Flask server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
