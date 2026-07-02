import pandas as pd
import numpy as np

def extract_features(df):
    df = df.copy()

    # --- nonlinear transforms ---
    df["rt_squared"] = df["response_time"] ** 2
    df["rt_log"] = np.log1p(df["response_time"])

    # --- interactions ---
    df["rt_x_error"] = df["response_time"] * df["error_flag"]
    df["rt_x_warn"] = df["response_time"] * df["warn_flag"]

    # --- temporal features ---
    df["rt_diff"] = df["response_time"].diff().fillna(0)
    df["rt_mean_5"] = df["response_time"].rolling(5, min_periods=1).mean()
    df["rt_std_5"] = df["response_time"].rolling(5, min_periods=1).std().fillna(0)

    return df[
        [
            "response_time",
            "error_flag",
            "warn_flag",
            "rt_squared",
            "rt_log",
            "rt_x_error",
            "rt_x_warn",
            "rt_diff",
            "rt_mean_5",
            "rt_std_5"
        ]
    ].fillna(0)