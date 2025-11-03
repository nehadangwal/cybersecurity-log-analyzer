from sklearn.ensemble import IsolationForest
import pandas as pd

def get_severity(confidence):
    """Maps confidence score to severity level based on a simple scale."""
    if confidence > 0.8:
        return 'CRITICAL'
    if confidence > 0.6:
        return 'HIGH'
    if confidence > 0.4:
        return 'MEDIUM'
    return 'LOW'

def detect_anomalies(logs):
    df = pd.DataFrame(logs)
    if df.empty:
        return []

    ip_counts = df['source_ip'].value_counts()
    total_logs = len(df)
    
    anomalies = []
    
    # Set a realistic threshold: IPs with more than 3 requests (12% of total logs)
    threshold_count = 3 
    
    for ip, count in ip_counts.items():
        if count >= threshold_count:
            # Generate confidence: ratio of logs this IP accounts for
            confidence = min(count / total_logs, 1.0)
            severity = get_severity(confidence)

            # Find a single log entry associated with this IP for detail context
            first_entry = df[df['source_ip'] == ip].iloc[0].to_dict() 
            
            anomalies.append({
                "log_entry": first_entry, 
                "anomaly_type": "High Request Volume",
                "description": f"IP {ip} made {count} requests. Potential scanning or brute-force attack.",
                "confidence_score": confidence,
                "severity": severity
            })

    return anomalies