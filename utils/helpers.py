def get_summary(df):
    return {
        "total_logs": len(df),
        "anomalies": int(df['anomaly'].sum()),
        "services": df['service'].nunique()
    }