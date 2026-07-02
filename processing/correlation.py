import pandas as pd

# Simple service dependency map (can expand later)
SERVICE_DEPENDENCIES = {
    "Auth Service": ["Database"],
    "Payment API": ["Database"],
    "User Service": ["Auth Service"],
    "Cache Layer": ["Database"]
}


def correlate_events(df, time_window_sec=10, min_anomalies=2):
    """
    PAPER-LEVEL correlation:
    - Time-based grouping
    - Cross-service aggregation
    - Dependency-aware enrichment
    """

    if len(df) == 0:
        return []

    df = df.copy()
    df = df.sort_values("timestamp")

    anomalies = df[df['anomaly'] == 1]

    incidents = []

    i = 0
    while i < len(anomalies):
        start_time = anomalies.iloc[i]['timestamp']
        window_end = start_time + pd.Timedelta(seconds=time_window_sec)

        window = anomalies[
            (anomalies['timestamp'] >= start_time) &
            (anomalies['timestamp'] <= window_end)
        ]

        if len(window) >= min_anomalies:

            services = window['service'].unique().tolist()

            # 🔥 Dependency expansion (context awareness)
            expanded_services = set(services)
            for svc in services:
                if svc in SERVICE_DEPENDENCIES:
                    expanded_services.update(SERVICE_DEPENDENCIES[svc])
                    
            request_count = window['request_id'].nunique() if 'request_id' in window.columns else 0

            incident = {
                "start_time": window.iloc[0]['timestamp'],
                "end_time": window.iloc[-1]['timestamp'],
                "services": list(expanded_services),
                "primary_services": services,
                "anomaly_count": int(len(window)),
                "avg_response": float(window['response_time'].mean()),
                "severity": assign_incident_severity(window),
                "affected_requests": int(request_count)
            }

            incidents.append(incident)

            i += len(window)  # skip window (avoid duplicates)
        else:
            i += 1

    return incidents


def assign_incident_severity(window):
    """
    Multi-factor severity (paper-level improvement)
    """

    avg_rt = window['response_time'].mean()
    error_ratio = (window['level'] == 'ERROR').mean()

    if avg_rt > 600 or error_ratio > 0.5:
        return "HIGH"
    elif avg_rt > 400 or error_ratio > 0.3:
        return "MEDIUM"
    else:
        return "LOW"