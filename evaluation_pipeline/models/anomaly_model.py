from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd


class AnomalyDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(
            n_estimators=200,
            max_samples=0.8,
            contamination=contamination,
            random_state=42
        )
        self.is_fitted = False

    # ---------------- INTERNAL FEATURE MAGIC ----------------
    def _enhance_features(self, X):
        """
        Adds nonlinear features WITHOUT changing preprocess()
        """
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=["response_time", "error_flag", "warn_flag"])

        X = X.copy()

        # --- Nonlinear transforms ---
        X["rt_squared"] = X["response_time"] ** 2
        X["rt_log"] = np.log1p(X["response_time"])

        # --- Interactions ---
        X["rt_x_error"] = X["response_time"] * X["error_flag"]
        X["rt_x_warn"] = X["response_time"] * X["warn_flag"]

        # --- Simple temporal behavior (no preprocess change) ---
        X["rt_diff"] = X["response_time"].diff().fillna(0)
        X["rt_mean_5"] = X["response_time"].rolling(5, min_periods=1).mean()
        X["rt_std_5"] = X["response_time"].rolling(5, min_periods=1).std().fillna(0)

        return X.fillna(0)

    # ---------------- TRAIN ----------------
    def train(self, X):
        X = self._enhance_features(X)
        self.model.fit(X)
        self.is_fitted = True

    # ---------------- PREDICT ----------------
    def predict(self, X):
        if not self.is_fitted:
            raise Exception("Model not trained yet. Call train() first.")

        X = self._enhance_features(X)

        # IsolationForest score
        scores = self.model.decision_function(X)

        # --- Add nonlinear statistical signal ---
        dist = np.linalg.norm(X - X.mean(), axis=1)
        dist = (dist - dist.mean()) / (dist.std() + 1e-5)

        final_score = scores - 0.25 * dist

        # --- Stable adaptive threshold ---
        threshold = np.mean(final_score) - 1.0 * np.std(final_score)

        return (final_score < threshold).astype(int).tolist()