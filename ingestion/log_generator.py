import pandas as pd
import numpy as np
import random
import uuid
from config import LOG_COUNT, SERVICES, ANOMALY_RATE, LOG_LEVELS

SYSTEM_STATE = {
    "incident_active": False,
    "incident_type": None,
    "incident_timer": 0
}

def generate_logs(batch_size=20):
    current_time = pd.Timestamp.now()

    logs = []
    
    # randomly trigger incident
    if not SYSTEM_STATE["incident_active"] and random.random() < 0.05:
        SYSTEM_STATE["incident_active"] = True
        SYSTEM_STATE["incident_type"] = random.choice(["spike", "outage", "cascade"])
        SYSTEM_STATE["incident_timer"] = random.randint(5, 15)

    for _ in range(batch_size):
        request_id = str(uuid.uuid4())[:8]

        service = random.choice(SERVICES)
        level = np.random.choice(LOG_LEVELS, p=[0.7, 0.2, 0.1])

        response_time = np.random.normal(200, 50)

        # dynamic anomaly probability
        dynamic_rate = ANOMALY_RATE + random.uniform(-0.01, 0.02)

        if SYSTEM_STATE["incident_active"]:

            SYSTEM_STATE["incident_timer"] -= 1

            if SYSTEM_STATE["incident_type"] == "spike":
                response_time *= random.uniform(3, 6)

            elif SYSTEM_STATE["incident_type"] == "outage":
                if random.random() < 0.5:
                    response_time *= random.uniform(5, 10)

            elif SYSTEM_STATE["incident_type"] == "cascade":
                if service in ["Database", "Auth Service"]:
                    response_time *= random.uniform(4, 8)

            if SYSTEM_STATE["incident_timer"] <= 0:
                SYSTEM_STATE["incident_active"] = False

        else:
            if random.random() < max(0.01, dynamic_rate):
                response_time *= random.uniform(2, 3.5)
            else:
                response_time *= random.uniform(0.9, 1.1)

        logs.append({
            "timestamp": current_time,
            "request_id": request_id,
            "service": service,
            "level": level,
            "response_time": response_time
        })

    return pd.DataFrame(logs)