import pandas as pd
import matplotlib.pyplot as plt

from data.log_generator import generate_logs
from processing.preprocessor import preprocess
from models.anomaly_model import AnomalyDetector
from evaluation.metrics import compute_metrics

# ---------------- CONFIG ----------------
TOTAL_LOGS = 8000

print("Generating dataset...")
df = generate_logs(batch_size=TOTAL_LOGS)

print("Preprocessing...")
X = preprocess(df)

print("Training model...")
model = AnomalyDetector(contamination=0.05)
model.train(X)

print("Predicting...")
df["anomaly"] = model.predict(X)

print("Evaluating...")
metrics = compute_metrics(df)

print("\n--- RESULTS ---")
for k, v in metrics.items():
    print(f"{k.upper()}: {v:.4f}")

# ---------------- SAVE TABLE ----------------
df.to_csv("evaluation_pipeline/outputs/full_results.csv", index=False)

df[["service", "response_time", "true_anomaly", "anomaly"]]\
    .to_csv("evaluation_pipeline/outputs/results_table.csv", index=False)

# ---------------- GRAPH ----------------
trend = df.groupby(df.index // 50)["anomaly"].sum()

plt.figure(figsize=(8, 5))
plt.plot(trend)
plt.title("Anomaly Detection Trend")
plt.xlabel("Time Window")
plt.ylabel("Anomaly Count")
plt.tight_layout()
plt.savefig("evaluation_pipeline/outputs/anomaly_trend.png")

print("\nSaved outputs to /outputs")