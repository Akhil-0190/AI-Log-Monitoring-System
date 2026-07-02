import pandas as pd
import numpy as np
import random
from config import LOG_COUNT, SERVICES, ANOMALY_RATE, LOG_LEVELS

def generate_logs(batch_size=20):
    current_time = pd.Timestamp.now()

    logs = []

    for _ in range(batch_size):

        service = random.choice(SERVICES)
        level = np.random.choice(LOG_LEVELS, p=[0.7, 0.2, 0.1])

        response_time = np.random.normal(200, 50)

        # dynamic anomaly probability
        dynamic_rate = ANOMALY_RATE + random.uniform(-0.01, 0.02)
        
        is_anomaly = 1 if np.random.rand() < max(0.01, dynamic_rate) else 0

        if is_anomaly:
            if random.random() < max(0.01, dynamic_rate):
                response_time *= random.uniform(3, 5)
            else:
                # slight noise for realism
                response_time *= random.uniform(0.9, 1.1)

        logs.append({
            "timestamp": current_time,
            "service": service,
            "level": level,
            "response_time": response_time,
            "true_anomaly": is_anomaly
        })

    return pd.DataFrame(logs)