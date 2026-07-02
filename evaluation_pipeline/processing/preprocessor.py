def preprocess(df):
    df['error_flag'] = (df['level'] == 'ERROR').astype(int)
    df['warn_flag'] = (df['level'] == 'WARN').astype(int)

    features = df[['response_time', 'error_flag', 'warn_flag']]

    return features