import pandas as pd

def preprocess(df):
    df = df.copy()

    # --- 1. timestamp normalization ---
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # --- 2. drop invalid rows ---
    df = df.dropna(subset=['timestamp', 'response_time', 'service', 'level'])

    # --- 3. enforce types ---
    df['response_time'] = pd.to_numeric(df['response_time'], errors='coerce')

    # --- 4. handle missing after conversion ---
    df = df.dropna(subset=['response_time'])

    # --- 5. normalize categorical values ---
    df['level'] = df['level'].str.upper().str.strip()
    df['service'] = df['service'].str.strip()

    # --- 6. remove unrealistic noise ---
    df = df[df['response_time'] > 0]
    df = df[df['response_time'] < 5000]  # cap extreme outliers

    # --- 7. create flags ---
    df['error_flag'] = (df['level'] == 'ERROR').astype(int)
    df['warn_flag'] = (df['level'] == 'WARN').astype(int)

    # --- 8. sort for temporal consistency ---
    df = df.sort_values('timestamp')
    
    if 'request_id' not in df.columns:
        df['request_id'] = 'unknown'

    return df[['timestamp', 'request_id', 'service', 'level', 'response_time', 'error_flag', 'warn_flag']]