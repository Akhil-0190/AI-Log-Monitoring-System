import os
from datetime import datetime
import json

def save_text(filename, content):
    os.makedirs("outputs", exist_ok=True)

    path = f"outputs/{filename}"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n--- {timestamp} ---\n")
        f.write(content)
        f.write("\n")
        
def save_anomalies(df):
    anomalies = df[df['anomaly'] == 1]

    if len(anomalies) == 0:
        return

    path = "outputs/anomalies.json"

    data = anomalies.tail(50).to_dict(orient="records")

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, default=str))
        f.write("\n")


def save_incidents(incidents):
    if not incidents:
        return

    path = "outputs/incidents.json"

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(incidents, default=str))
        f.write("\n")


def save_root_causes(root_causes):
    if not root_causes:
        return

    path = "outputs/root_causes.json"

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(root_causes, default=str))
        f.write("\n")