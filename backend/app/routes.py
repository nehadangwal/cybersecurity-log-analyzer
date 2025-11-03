from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import traceback
from .log_parser import parse_log
from .anomaly_detector import detect_anomalies
from . import db
from .models import LogAnalysis, LogEntry, Anomaly

api = Blueprint("api", __name__)

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERS = {"admin": "password"}

@api.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        if username in USERS and USERS[username] == password:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "failure", "error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route("/upload-log", methods=["POST"])
def upload_log():
    try:
        # 1. Validate file upload
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"✅ File saved: {filepath}")

        # 2. Parse Logs
        try:
            parsed_logs = parse_log(filepath)
            print(f"✅ Parsed {len(parsed_logs)} log entries")
        except Exception as e:
            print(f"❌ Parse error: {str(e)}")
            return jsonify({"error": f"Failed to parse log file: {str(e)}"}), 400
        
        if not parsed_logs:
            return jsonify({"error": "No valid log entries found in file"}), 400
        
        # 3. Create LogAnalysis Record
        analysis = LogAnalysis(
            filename=filename,
            total_entries=len(parsed_logs),
            summary="Analysis in progress...",
            status='processing'
        )
        db.session.add(analysis)
        db.session.flush()
        print(f"✅ Created analysis record: {analysis.id}")

        # 4. Save Log Entries
        log_entry_objects = []
        for log_data in parsed_logs:
            log_entry = LogEntry(analysis_id=analysis.id, **log_data)
            log_entry_objects.append(log_entry)
            
        db.session.add_all(log_entry_objects)
        db.session.commit() # IDs are generated here!
        print(f"✅ Saved {len(log_entry_objects)} log entries")
        
        # 5. Detect Anomalies
        try:
            detected_anomalies = detect_anomalies([e.to_dict() for e in log_entry_objects])
            print(f"✅ Detected {len(detected_anomalies)} anomalies")
        except Exception as e:
            print(f"❌ Anomaly detection error: {str(e)}")
            return jsonify({"error": f"Anomaly detection failed: {str(e)}"}), 500
        
        # 6. Save Anomalies
        anomalies_to_save = []
        for anomaly_data in detected_anomalies:
            # Get the ID directly from the anomaly data
            log_entry_id = anomaly_data['log_entry']['id']
            
            new_anomaly = Anomaly(
                analysis_id=analysis.id,
                log_entry_id=log_entry_id,
                anomaly_type=anomaly_data['anomaly_type'],
                description=anomaly_data['description'],
                confidence_score=anomaly_data['confidence_score'],
                severity=anomaly_data['severity']
            )
            anomalies_to_save.append(new_anomaly)

        db.session.add_all(anomalies_to_save)
        analysis.anomaly_count = len(anomalies_to_save)
        analysis.summary = f"Analysis complete. Found {analysis.anomaly_count} potential anomalies."
        analysis.status = 'analyzed'
        db.session.commit()
        print(f"✅ Analysis complete. Returning {len(anomalies_to_save)} anomalies")
        
        # 7. Return Results
        return jsonify({
            "status": "success",
            "analysis_id": analysis.id,
            "total_entries": analysis.total_entries,
            "anomaly_count": analysis.anomaly_count,
            "anomalies": [a.to_dict() for a in anomalies_to_save]
        }), 200
        
    except Exception as e:
        # Rollback database changes on error
        db.session.rollback()
        error_trace = traceback.format_exc()
        print(f"❌ Upload error: {error_trace}")
        return jsonify({
            "error": f"Server error: {str(e)}",
            "details": error_trace if os.environ.get('DEBUG') else None
        }), 500