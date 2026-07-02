import pandas as pd

# same dependency map (keep consistent with correlation)
SERVICE_DEPENDENCIES = {
    "Auth Service": ["Database"],
    "Payment API": ["Database"],
    "User Service": ["Auth Service"],
    "Cache Layer": ["Database"]
}


def find_root_cause(df, incidents):
    """
    PAPER-LEVEL RCA:
    - Works on correlated incidents
    - Multi-factor scoring
    """

    results = []

    for inc in incidents:

        incident_df = df[
            (df['timestamp'] >= inc['start_time']) &
            (df['timestamp'] <= inc['end_time'])
        ]

        if len(incident_df) == 0:
            continue

        scores = {}

        for svc in inc['primary_services']:
            svc_df = incident_df[incident_df['service'] == svc]

            if len(svc_df) == 0:
                continue

            # --- FACTOR 1: anomaly density ---
            anomaly_ratio = svc_df['anomaly'].mean()

            # --- FACTOR 2: response degradation ---
            avg_rt = svc_df['response_time'].mean()
            request_impact = svc_df['request_id'].nunique() if 'request_id' in svc_df.columns else 0

            # --- FACTOR 3: error contribution ---
            error_ratio = (svc_df['level'] == 'ERROR').mean()

            # --- FACTOR 4: dependency impact ---
            dependency_penalty = 0
            for other in inc['primary_services']:
                if other in SERVICE_DEPENDENCIES and svc in SERVICE_DEPENDENCIES[other]:
                    dependency_penalty += 0.2

            # --- FINAL SCORE ---
            score = (
                0.35 * anomaly_ratio +
                0.25 * (avg_rt / 1000) +
                0.2 * error_ratio +
                0.1 * dependency_penalty +
                0.1 * (request_impact / 10)
            )

            scores[svc] = score

        if len(scores) == 0:
            continue

        root_service = max(scores, key=scores.get)
        confidence = scores[root_service] / (sum(scores.values()) + 1e-5)

        results.append({
            "start_time": inc['start_time'],
            "end_time": inc['end_time'],
            "root_cause": root_service,
            "confidence": round(confidence, 2),
            "scores": scores
        })

    return results