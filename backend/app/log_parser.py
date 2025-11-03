import pandas as pd

def parse_log(filepath):
    logs = []
    with open(filepath, "r") as f:
        for line in f.readlines():
            line = line.strip()
            
            # 1. Skip blank lines and remove file-specific source markers
            if not line or line.startswith('['):
                continue
            # The faulty line that caused a SyntaxError has been removed.
            
            parts = line.split(" ")
            
            try:
                # Based on the Apache log format: [IP] - - [TIME] "REQUEST" [STATUS] [BYTES] "[REFERRER]" "[USER_AGENT]"
                source_ip = parts[0]
                timestamp = parts[3].strip('[')
                status_code = parts[8]
                bytes_sent = int(parts[9]) if parts[9].isdigit() else 0
                
                action = parts[5].strip('"')
                url = parts[6]
                
                # Extract User Agent
                user_agent_end = line.rfind('"')
                user_agent_start = line.rfind('"', 0, user_agent_end - 1)
                user_agent = line[user_agent_start + 1:user_agent_end].strip()

                logs.append({
                    "timestamp": timestamp,
                    "source_ip": source_ip,
                    "destination_ip": None,
                    "url": url,
                    "action": action,
                    "status_code": status_code,
                    "bytes_sent": bytes_sent,
                    "user_agent": user_agent,
                    "raw_log": line
                })
            except (IndexError, ValueError, TypeError):
                continue
                
    return logs