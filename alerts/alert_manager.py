def assign_severity(row):
    rt = row['response_time']
    is_error = row['level'] == 'ERROR'
    is_warn = row['level'] == 'WARN'
    anomaly = row.get('anomaly', 0)

    score = 0

    # --- response time impact ---
    if rt > 600:
        score += 2
    elif rt > 400:
        score += 1

    # --- log level impact ---
    if is_error:
        score += 2
    elif is_warn:
        score += 1

    # --- anomaly signal ---
    if anomaly == 1:
        score += 2

    # --- final severity ---
    if score >= 5:
        return "HIGH"
    elif score >= 3:
        return "MEDIUM"
    else:
        return "LOW"

def generate_alerts(df):
    alerts = df[df['anomaly'] == 1].copy()
    alerts['severity'] = alerts.apply(assign_severity, axis=1)
    return alerts