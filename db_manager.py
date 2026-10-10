import sqlite3
import json
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'omnisalus.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite database and creates the assessment_records table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessment_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_type TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            severity TEXT,
            risk_score REAL,
            inputs_json TEXT NOT NULL,
            result_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            timespan_formatted TEXT NOT NULL,
            ip_address TEXT
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_type ON assessment_records(model_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON assessment_records(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON assessment_records(severity)')
    conn.commit()
    conn.close()
    print(f"[Database] SQLite initialized at: {DB_PATH}")

def save_assessment(model_type, inputs, result, ip_address=None):
    """Saves a new patient assessment record to the database."""
    now_utc = datetime.now(timezone.utc)
    created_at = now_utc.isoformat(timespec='seconds')
    # Local formatted timespan string: YYYY-MM-DD HH:MM:SS
    now_local = datetime.now()
    timespan_formatted = now_local.strftime('%Y-%m-%d %I:%M:%S %p')

    # Extract primary diagnosis
    diagnosis = result.get('diagnosis') or result.get('obesity_level') or 'Assessment Evaluated'
    severity = result.get('severity') or 'Evaluated'

    # Extract risk score / probability
    risk_score = result.get('probability_pct')
    if risk_score is None:
        risk_score = result.get('confidence_pct')
    if risk_score is None:
        risk_score = result.get('consensus_prob_pct')
    if risk_score is None and 'calculated_bmi' in result:
        risk_score = result.get('calculated_bmi')

    inputs_json = json.dumps(inputs, ensure_ascii=False)
    result_json = json.dumps(result, ensure_ascii=False)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO assessment_records (
            model_type, diagnosis, severity, risk_score,
            inputs_json, result_json, created_at, timespan_formatted, ip_address
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        model_type,
        str(diagnosis),
        str(severity),
        float(risk_score) if risk_score is not None else None,
        inputs_json,
        result_json,
        created_at,
        timespan_formatted,
        ip_address
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_assessments(model_type=None, severity=None, search=None, limit=100, offset=0):
    """Retrieves assessment records with optional filtering and search."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM assessment_records WHERE 1=1'
    params = []

    if model_type and model_type.lower() != 'all':
        query += ' AND LOWER(model_type) = ?'
        params.append(model_type.lower())

    if severity and severity.lower() != 'all':
        query += ' AND LOWER(severity) LIKE ?'
        params.append(f"%{severity.lower()}%")

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query += ' AND (LOWER(diagnosis) LIKE ? OR LOWER(model_type) LIKE ? OR LOWER(inputs_json) LIKE ? OR CAST(id AS TEXT) = ?)'
        params.extend([term, term, term, search.strip()])

    query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    records = []
    for r in rows:
        records.append({
            'id': r['id'],
            'model_type': r['model_type'],
            'diagnosis': r['diagnosis'],
            'severity': r['severity'],
            'risk_score': r['risk_score'],
            'created_at': r['created_at'],
            'timespan_formatted': r['timespan_formatted'],
            'ip_address': r['ip_address']
        })

    conn.close()
    return records

def get_assessment_by_id(record_id):
    """Retrieves full details of a single assessment record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM assessment_records WHERE id = ?', (record_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    try:
        inputs_data = json.loads(row['inputs_json'])
    except Exception:
        inputs_data = row['inputs_json']

    try:
        result_data = json.loads(row['result_json'])
    except Exception:
        result_data = row['result_json']

    return {
        'id': row['id'],
        'model_type': row['model_type'],
        'diagnosis': row['diagnosis'],
        'severity': row['severity'],
        'risk_score': row['risk_score'],
        'inputs': inputs_data,
        'result': result_data,
        'created_at': row['created_at'],
        'timespan_formatted': row['timespan_formatted'],
        'ip_address': row['ip_address']
    }

def delete_assessment(record_id):
    """Deletes an assessment record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM assessment_records WHERE id = ?', (record_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_stats_summary():
    """Generates aggregate statistics for the Admin Dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total records
    cursor.execute('SELECT COUNT(*) FROM assessment_records')
    total_count = cursor.fetchone()[0]

    # Today's records
    today_str = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT COUNT(*) FROM assessment_records WHERE timespan_formatted LIKE ?', (f"{today_str}%",))
    today_count = cursor.fetchone()[0]

    # Count by model_type
    cursor.execute('SELECT model_type, COUNT(*) as cnt FROM assessment_records GROUP BY model_type')
    by_model = {r['model_type']: r['cnt'] for r in cursor.fetchall()}

    # High risk count
    cursor.execute("SELECT COUNT(*) FROM assessment_records WHERE LOWER(severity) LIKE '%high%' OR LOWER(severity) LIKE '%danger%' OR LOWER(severity) LIKE '%malignant%'")
    high_risk_count = cursor.fetchone()[0]

    conn.close()

    # Determine top active model
    top_model = 'None'
    if by_model:
        top_model = max(by_model, key=by_model.get)

    return {
        'total_assessments': total_count,
        'today_assessments': today_count,
        'high_risk_alerts': high_risk_count,
        'top_active_module': top_model,
        'by_model': by_model
    }

def export_all_records_csv():
    """Exports all assessment records as CSV format string."""
    import csv
    import io

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, created_at, timespan_formatted, model_type, diagnosis, severity, risk_score, inputs_json FROM assessment_records ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Record ID', 'Timestamp (UTC)', 'Local Timespan', 'Disease Module', 'Diagnosis', 'Severity Tier', 'Calculated Score', 'Patient Inputs'])

    for r in rows:
        writer.writerow([
            r['id'],
            r['created_at'],
            r['timespan_formatted'],
            r['model_type'],
            r['diagnosis'],
            r['severity'],
            r['risk_score'] if r['risk_score'] is not None else 'N/A',
            r['inputs_json']
        ])

    return output.getvalue()
