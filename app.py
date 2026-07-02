<<<<<<< HEAD
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import time
from sklearn.exceptions import NotFittedError
import threading
import plotly.graph_objects as go
import math

# CORE IMPORTS
from ingestion.log_generator import generate_logs
from processing.preprocessor import preprocess
from models.anomaly_model import AnomalyDetector
from alerts.alert_manager import generate_alerts
from utils.helpers import get_summary
from processing.correlation import correlate_events
from analysis.root_cause import find_root_cause
from processing.feature_engineering import extract_features
from utils.storage import save_anomalies, save_incidents, save_root_causes

# UI IMPORTS
from ui.ui import system_pipeline, throughput_meter, anomaly_heatmap
from ui.features import replay_system, ai_explanation, incident_timeline, clustering_view, training_simulation
from ui.ui import anomaly_trend
from report import login_system, download_logs, generate_report, alert_sound, generate_ai_report

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_system()
    st.stop()

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Sidebar width */
section[data-testid="stSidebar"] {
    width: 220px !important;
}

/* ---------- CARD SYSTEM ---------- */
.card {
    background: #111827;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 10px;
    transition: all 0.2s ease-in-out;
}

.card:hover {
    transform: translateY(-2px);
    border: 1px solid rgba(0,255,255,0.3);
}

/* ---------- METRICS ---------- */
[data-testid="stMetric"] {
    background: #111827;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* ---------- ALERT FEED ---------- */
.alert-box {
    padding: 8px;
    margin-bottom: 6px;
    border-radius: 10px;
    font-size: 13px;
}

/* ---------- SCROLL AREAS ---------- */
.scroll-box {
    max-height: 300px;
    overflow-y: auto;
}

/* ---------- TABS ---------- */
.stTabs [role="tab"] {
    font-size: 14px;
}

/* ---------- REMOVE PLOT BACKGROUND ---------- */
.js-plotly-plot {
    border-radius: 12px;
}

/* ---------- SIDEBAR UPGRADE ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    border-right: 1px solid rgba(255,255,255,0.05);
    padding-top: 10px;
}

section[data-testid="stSidebar"] .card {
    box-shadow: 0 0 10px rgba(0,255,255,0.05);
}

/* REMOVE EMPTY SIDEBAR CARDS */
section[data-testid="stSidebar"] .card:empty {
    display: none !important;
}

section[data-testid="stSidebar"] .element-container:has(.card:empty) {
    display: none !important;
}

section[data-testid="stSidebar"] .element-container {
    margin-bottom: 4px !important;
}

/* METRIC CARD ENHANCEMENT */
.metric-card {
    position: relative;
    overflow: hidden;
}

.metric-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top right, rgba(0,255,255,0.15), transparent 60%);
    opacity: 0;
    transition: 0.3s;
}

.metric-card:hover::after {
    opacity: 1;
}

/* ---------- REGION CARDS ---------- */
.region-card {
    transition: all 0.2s ease-in-out;
    position: relative;
}

.region-card:hover {
    transform: translateY(-2px);
    border: 1px solid rgba(0,255,255,0.3);
}

/* Status text */
.region-status {
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.5px;
}

/* Subtext */
.region-meta {
    font-size: 12px;
    opacity: 0.7;
}

/* Subtle glow effect */
.region-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top right, rgba(0,255,255,0.12), transparent 60%);
    opacity: 0;
    transition: 0.3s;
}

.region-card:hover::after {
    opacity: 1;
}

/* ---------- NODE CARDS ---------- */
.node-card {
    text-align: center;
    transition: all 0.2s ease-in-out;
    position: relative;
}

/* Hover effect (stronger than region cards) */
.node-card:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 0 15px rgba(0,255,255,0.15);
}

/* Status styling */
.node-status {
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 0.5px;
}

/* Glow pulse for critical (optional visual depth) */
.node-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, rgba(0,255,255,0.12), transparent 70%);
    opacity: 0;
    transition: 0.3s;
}

.node-card:hover::after {
    opacity: 1;
}

</style>
""", unsafe_allow_html=True)

# Auto refresh every 5 seconds
# ---------------- REFRESH CONTROL ----------------
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if "ai_running" not in st.session_state:
    st.session_state.ai_running = False
    
if "report_running" not in st.session_state:
    st.session_state.report_running = False

if "ai_done_event" not in st.session_state:
    st.session_state.ai_done_event = threading.Event()

# ---------------- TITLE ----------------
st.title("🚀 AI-Powered Log Monitoring System")

st.sidebar.markdown(f"""
<div class="card">
    👤 <b>User</b><br>
    {st.session_state.role}
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="card">
    <b>🧠 System Status</b><br><br>
    🟢 Model: Active<br>
    ⚡ Stream: Running<br>
    🔄 Refresh: 5s
</div>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
if "log_store" not in st.session_state:
    st.session_state["log_store"] = pd.DataFrame()

# ---------------- DATA STREAM ----------------

if "log_store" not in st.session_state:
    st.session_state["log_store"] = pd.DataFrame()

# --- STREAM CONTROL ---
st.sidebar.markdown('<div class="card">', unsafe_allow_html=True)

st.sidebar.markdown("### ⚙️ Stream Control")

logs_per_sec = st.sidebar.slider("Logs/sec", 5, 50, 10)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

refresh_interval = 5
batch_size = logs_per_sec * refresh_interval

# Generate new logs
# ---------------- CONTROLLED LOG GENERATION ----------------
if "last_log_gen" not in st.session_state:
    st.session_state.last_log_gen = 0

now = time.time()
REFRESH_INTERVAL = 5

if now - st.session_state.last_log_gen >= REFRESH_INTERVAL:
    new_logs = generate_logs(batch_size=batch_size)
    st.session_state.last_log_gen = now
else:
    new_logs = pd.DataFrame(columns=st.session_state["log_store"].columns)

# Temporary dataset for training
temp_df = pd.concat(
    [st.session_state["log_store"], new_logs],
    ignore_index=True
)

# ---------------- PREPROCESS ----------------
X = preprocess(temp_df)
X = extract_features(X)

# ---------------- MODEL ----------------
if "model" not in st.session_state:
    st.session_state["model"] = AnomalyDetector(contamination=0.05)

model = st.session_state["model"]

RETRAIN_THRESHOLD = max(100, int(0.1 * len(temp_df)))

if "last_trained_size" not in st.session_state:
    st.session_state["last_trained_size"] = 0

if "model_trained" not in st.session_state:
    st.session_state["model_trained"] = False

# 🔥 ALWAYS TRAIN IF NOT TRAINED OR DATA IS SMALL
if not st.session_state["model_trained"] or len(temp_df) < 50:
    model.train(X)
    st.session_state["last_trained_size"] = len(temp_df)
    st.session_state["model_trained"] = True

# 🔁 PERIODIC RETRAIN
elif len(temp_df) - st.session_state["last_trained_size"] > RETRAIN_THRESHOLD:
    model.train(X)
    st.session_state["last_trained_size"] = len(temp_df)

# ---------------- PREDICT ONLY NEW LOGS ----------------
if len(new_logs) > 0:
    new_X = preprocess(new_logs)
    new_X = extract_features(new_X)

    preds = model.predict(new_X)
    scores = model.get_scores(new_X)

    # ✅ Use safe default values instead of None
    new_logs['anomaly'] = 0
    new_logs['anomaly_score'] = scores.mean() if len(scores) > 0 else 0.0

    # ✅ Fill only valid rows
    new_logs.loc[new_X.index, 'anomaly'] = preds
    new_logs.loc[new_X.index, 'anomaly_score'] = scores

# ---------------- STORE FINAL DATA ----------------
st.session_state["log_store"] = pd.concat(
    [st.session_state["log_store"], new_logs],
    ignore_index=True
)

# limit size
MAX_LOGS = 10000
if len(st.session_state["log_store"]) > MAX_LOGS:
    st.session_state["log_store"] = st.session_state["log_store"].tail(MAX_LOGS)

df = st.session_state["log_store"]

# feature flags
df['error_flag'] = (df['level']=='ERROR').astype(int)
df['warn_flag'] = (df['level']=='WARN').astype(int)

alerts = generate_alerts(df)
stats = get_summary(df)

st.sidebar.markdown('<div class="card">', unsafe_allow_html=True)
st.sidebar.markdown("**📊 Live Stats**")

st.sidebar.write(f"Logs: {stats['total_logs']}")
st.sidebar.write(f"Anomalies: {stats['anomalies']}")
st.sidebar.write(f"Services: {stats['services']}")

st.sidebar.markdown('</div>', unsafe_allow_html=True)

correlated_incidents = correlate_events(df)
root_causes = find_root_cause(df, correlated_incidents)

save_anomalies(df)
save_incidents(correlated_incidents)
save_root_causes(root_causes)

tabs = st.tabs(["Overview", "System", "Analytics", "Intelligence", "Data"])

with tabs[0]:
    # ---------------- TOP METRICS ----------------
    c1,c2,c3,c4 = st.columns(4)

    def metric_card(title, value, color="#ffffff"):
        return f"""
        <div class="card metric-card">
            <div style="font-size:12px; opacity:0.6;">{title}</div>
            <div style="font-size:32px; font-weight:800; color:{color}; margin-top:5px;">
                {value}
            </div>
        </div>
        """

    c1.markdown(metric_card("Logs", stats['total_logs'], "#00f2ff"), unsafe_allow_html=True)
    c2.markdown(metric_card("Anomalies", stats['anomalies'], "#ff4d4d"), unsafe_allow_html=True)
    c3.markdown(metric_card("Services", stats['services'], "#ffaa00"), unsafe_allow_html=True)
    c4.markdown(metric_card("Status", "RUNNING", "#00ffcc"), unsafe_allow_html=True)

    # ---------------- GLOBAL VIEW ----------------
    st.subheader("🌍 Global System View")
    
    def region_card(region, status, anomaly, color):
        return f"""<div class="card region-card">
    <b>🌍 {region}</b><br>
    <span class="region-status" style="color:{color};">{status}</span><br>
    <span class="region-meta">Anomalies: {anomaly}</span>
    </div>"""

    region_map = {
        "Auth Service": "US-East",
        "Payment API": "EU-West",
        "Database": "India",
        "User Service": "Asia",
        "Cache Layer": "India"
    }

    df['region'] = df['service'].map(region_map)

    region_stats = df.groupby('region')['anomaly'].sum().reset_index()

    cols = st.columns(4)

    for i, (_, row) in enumerate(region_stats.iterrows()):
        ratio = row['anomaly'] / len(df)

        if ratio < 0.03:
            color = "#00ffcc"
            status = "HEALTHY"
        elif ratio < 0.08:
            color = "#ffaa00"
            status = "DEGRADED"
        else:
            color = "#ff4d4d"
            status = "CRITICAL"

        cols[i].markdown(
            region_card(row['region'], status, int(row['anomaly']), color),
            unsafe_allow_html=True
        )

    # ---------------- NODES ----------------
    st.subheader("🌐 Service Nodes")
    
    def node_card(service, status, color):
        return f"""<div class="card node-card">
    <b>{service}</b><br>
    <span class="node-status" style="color:{color};">{status}</span>
    </div>"""

    cols = st.columns(5)
    services = df['service'].unique()

    for i, svc in enumerate(services):
        svc_df = df[df['service'] == svc]

        if len(svc_df) == 0:
            status = "UNKNOWN"
            color = "#888"
        else:
            ratio = svc_df['anomaly'].sum() / len(svc_df)

            if ratio < 0.05:
                status = "HEALTHY"
                color = "#00ffcc"
            elif ratio < 0.12:
                status = "DEGRADED"
                color = "#ffaa00"
            else:
                status = "CRITICAL"
                color = "#ff4d4d"

        cols[i].markdown(
            node_card(svc, status, color),
            unsafe_allow_html=True
        )

with tabs[1]:
    subtab1, subtab2 = st.tabs([
        "🔗 System Graph",
        "🚨 Alerts"
    ])
    
    with subtab1:
        st.markdown("## 🔗 Service Dependency Graph")

        edges = [
            ("User Service", "Auth Service"),
            ("User Service", "Payment API"),

            ("Cache Layer", "User Service"),

            ("Auth Service", "Database"),
            
            ("Cache Layer", "Database"),
            ("User Service", "Database"),
        ]

        # unique nodes
        nodes = list(set([n for edge in edges for n in edge]))

        positions = {
            "User Service": (1.6, 0),

            "Auth Service": (0.3, 0.9),
            "Database": (0.3, -1.0),

            "Payment API": (-1.3, 0.5),
            "Cache Layer": (-1.3, -0.5),
        }

        # edges
        edge_x, edge_y = [], []
        for src, dst in edges:
            x0, y0 = positions[src]
            x1, y1 = positions[dst]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        # nodes
        node_x = [positions[n][0] for n in nodes]
        node_y = [positions[n][1] for n in nodes]

        fig = go.Figure()

        # ✨ GLOW LAYER (background edges)
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=8, color='rgba(0,255,255,0.08)'),
            hoverinfo='none',
            mode='lines'
        ))

        # 🔥 MAIN EDGES
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=3, color='rgba(0,255,255,0.5)'),
            hoverinfo='skip',  # 🔥 prevents hover junk
            mode='lines'
        ))

        # ✨ NODE GLOW LAYER
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker=dict(
                size=45,
                color='rgba(0,255,255,0.15)'
            ),
            hoverinfo='none'
        ))

        # 🔵 MAIN NODES
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=nodes,
            textposition="bottom center",
            hovertemplate="<b>%{text}</b><extra></extra>",  # 🔥 THIS LINE FIXES IT
            marker=dict(
                size=28,
                color="#00f2ff",
                line=dict(width=2, color='white')
            )
        ))

        fig.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
        )

        # ✅ REMOVED EMPTY CARD WRAPPER (fixes that rectangle)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

    with subtab2:
        # ---------------- ALERTS ----------------
        st.markdown("## 🚨 Alerts")

        st.markdown('<div class="scroll-box">', unsafe_allow_html=True)

        for _, row in alerts.tail(10).iterrows():
            color = {
                "HIGH": "#ff4d4d",
                "MEDIUM": "#ffaa00",
                "LOW": "#00ffcc"
            }[row['severity']]

            bg = {
                "HIGH": "rgba(255,77,77,0.06)",
                "MEDIUM": "rgba(255,170,0,0.06)",
                "LOW": "rgba(0,255,204,0.06)"
            }[row['severity']]

            st.markdown(f"""
        <div class="alert-box" style="
            border-left:3px solid {color};
            background:{bg};
            padding:8px 10px;
            border-radius:8px;
            margin-bottom:6px;
        ">

        <div style="font-size:13px; font-weight:600;">
            {row['service']}
        </div>

        <div style="
            margin-top:4px;
            font-size:11px;
            padding:2px 6px;
            display:inline-block;
            border-radius:6px;
            background:{color}20;
            color:{color};
            font-weight:600;
        ">
        Severity: {row['severity']}
        </div>

        <div style="font-size:11px; opacity:0.7; margin-top:4px;">
        Response Time: {row['response_time']:.1f} ms
        </div>

        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if len(alerts) > 5:
            alert_sound()

with tabs[2]:
    subtab1, subtab2, subtab3, subtab4 = st.tabs([
        "📈 Trends & Load",
        "📊 Score Distribution",
        "⚡ Throughput & Heatmap",
        "📉 Anomaly Trend"
    ])
    # ---------------- CHARTS ----------------
    with subtab1:
        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(
                df,
                x="timestamp",
                y="response_time",
                title="Response Time Trend"
            )

            fig.update_traces(line=dict(width=2))

            fig.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis_title="Response Time (ms)"
            )

            st.plotly_chart(fig, use_container_width=True)


        with col2:
            # 🔥 FIX: proper dataframe instead of raw value_counts
            service_counts = df['service'].value_counts().reset_index()
            service_counts.columns = ["service", "requests"]

            fig2 = px.bar(
                service_counts,
                x="service",
                y="requests",
                title="Service Request Load"
            )

            fig2.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis_title="Requests"
            )

            st.plotly_chart(fig2, use_container_width=True)

    with subtab2:
        st.subheader("📈 Anomaly Score Distribution")

        if 'anomaly_score' in df.columns:

            # ================================
            # 📊 Histogram
            # ================================
            fig = px.histogram(
                df,
                x="anomaly_score",
                nbins=40,
                opacity=0.85
            )

            # ================================
            # 📌 Stats
            # ================================
            mean_val = df["anomaly_score"].mean()

            x0 = df["anomaly_score"].quantile(0.05)
            x1 = df["anomaly_score"].quantile(0.99)

            normal_pct = (
                (df["anomaly_score"] >= x0) &
                (df["anomaly_score"] <= x1)
            ).mean() * 100

            # ================================
            # 🟢 NORMAL ZONE (CLEAN VERSION)
            # ================================
            fig.add_vrect(
                x0=x0,
                x1=x1,
                fillcolor="green",
                opacity=0.08,
                layer="below",
                line_width=0,
                annotation_text=f"Normal ({normal_pct:.0f}%)",
                annotation_position="top left"
            )

            # ================================
            # 📍 Boundary Lines (IMPORTANT)
            # ================================
            fig.add_vline(x=x0, line_color="green", opacity=0.4)
            fig.add_vline(x=x1, line_color="green", opacity=0.4)

            # ================================
            # 🔴 Mean Line
            # ================================
            fig.add_vline(
                x=mean_val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean {mean_val:.2f}",
                annotation_position="top"
            )

            # ================================
            # 🎨 Styling (BIG IMPACT)
            # ================================
            fig.update_layout(
                title=None,
                margin=dict(l=10, r=10, t=20, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Anomaly Score",
                yaxis_title="Frequency",
                hovermode="x unified",
                bargap=0.05
            )

            # smoother bars
            fig.update_traces(
                marker=dict(
                    line=dict(width=0),
                )
            )

            # ================================
            # 🚀 Render
            # ================================
            st.plotly_chart(fig, use_container_width=True)
            
    with subtab3:
        # ---------------- ADVANCED ----------------

        colA, colB = st.columns(2)

        with colA:
            throughput_meter(df)

        with colB:
            anomaly_heatmap(df)

    with subtab4:
        anomaly_trend(df)

with tabs[3]:
    # ---------------- ULTRA ----------------

    df['error_flag'] = (df['level'] == 'ERROR').astype(int)
    df['warn_flag'] = (df['level'] == 'WARN').astype(int)

    tab1, tab2, tab3, tab4 = st.tabs(["Replay","Insights","Clustering","Correlation"])

    with tab1:
        replay_system(df)

    with tab2:
        colL, colR = st.columns(2)

        with colL:
            ai_explanation(df, correlated_incidents, root_causes)

        with colR:
            incident_timeline(df)

    with tab3:
        colL, colR = st.columns(2)

        with colL:
            clustering_view(df)

        with colR:
            training_simulation(df)

    with tab4:
        def render_incident_card(inc, sev_color):
            return f"""<div style="padding:16px;margin-bottom:16px;border-radius:12px;background:rgba(255,255,255,0.02);border-left:5px solid {sev_color};">

        <div style="display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:15px;font-weight:600;">
        🔴 Incident Window
        </div>
        <div style="font-size:12px;opacity:0.6;">
        {inc['start_time']} → {inc['end_time']}
        </div>
        </div>

        <div style="margin-top:10px;font-size:13px;opacity:0.8;">
        ⚙️ <b>Primary:</b> {", ".join(inc['primary_services'])}<br>
        🔗 <b>Affected:</b> {", ".join(inc['services'])}
        </div>

        <div style="display:flex;gap:20px;margin-top:12px;font-size:13px;">
        <div>📊 <b>{inc['anomaly_count']}</b> anomalies</div>
        <div>⏱ <b>{inc['avg_response']:.0f} ms</b></div>
        <div style="color:{sev_color};">
        🚨 <b>{inc['severity']}</b>
        </div>
        </div>

        </div>"""
        
        def render_rca_card(rc):
            return f"""<div style="margin-top:-10px;margin-bottom:15px;padding:14px;border-radius:10px;background:linear-gradient(90deg, rgba(0,150,255,0.08), rgba(0,255,200,0.05));">

        <div style="font-size:13px;opacity:0.7;">
        🧠 Root Cause Analysis
        </div>

        <div style="font-size:16px;font-weight:600;margin-top:4px;">
        {rc['root_cause']}
        </div>

        <div style="font-size:12px;opacity:0.6;margin-top:4px;">
        Confidence: {rc['confidence'] * 100:.1f}%
        </div>

        </div>"""
        
        def render_bar(svc, score):
            return f"""<div style="margin-bottom:6px;">
        <div style="font-size:12px;">{svc}</div>
        <div style="height:6px;border-radius:5px;background:rgba(255,255,255,0.08);overflow:hidden;">
        <div style="width:{score*100}%;height:100%;background:#00f2ff;"></div>
        </div>
        </div>"""
        
        if len(correlated_incidents) == 0:
            st.info("No correlated incidents detected")

        else:
            for i, inc in enumerate(correlated_incidents[-5:]):
                sev_color = {
                    "LOW": "🟢",
                    "MEDIUM": "🟡",
                    "HIGH": "🔴"
                }.get(inc['severity'], "🟢")

                with st.container():

                    # =========================
                    # 🔥 HEADER (INLINE)
                    # =========================
                    c1, c2 = st.columns([2, 3])

                    c1.markdown(f"**{sev_color} Incident**")
                    c2.markdown(
                        f"<div style='font-size:11px;opacity:0.6;text-align:right;'>{inc['start_time']} → {inc['end_time']}</div>",
                        unsafe_allow_html=True
                    )

                    # =========================
                    # 🔥 SERVICES (INLINE)
                    # =========================
                    primary = ", ".join(inc['primary_services'])
                    affected = ", ".join(inc['services'])

                    st.markdown(
                        f"<div style='font-size:12px;opacity:0.8;'>"
                        f"⚙️ <b>Primary services:</b> {primary} &nbsp;&nbsp; | &nbsp;&nbsp; "
                        f"🔗 <b>Affected services:</b> {affected}"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    # =========================
                    # 🔥 STATS (ONE LINE)
                    # =========================
                    st.markdown(
                        f"<div style='font-size:13px;margin-top:4px;'>"
                        f"📊 <b>{inc['anomaly_count']}</b> &nbsp;&nbsp; "
                        f"⏱ <b>{inc['avg_response']:.0f} ms</b> &nbsp;&nbsp; "
                        f"{sev_color} <b>{inc['severity']}</b>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    # =========================
                    # 🧠 RCA (COLLAPSED ONLY)
                    # =========================
                    if i < len(root_causes):
                        rc = root_causes[i]

                        with st.expander("🧠 RCA"):
                            svc = rc['root_cause']
                            confidence = rc['confidence'] * 100

                            # 🔥 HUMAN-READABLE EXPLANATION
                            if confidence > 70:
                                tone = "Strong indication"
                            elif confidence > 40:
                                tone = "Moderate indication"
                            else:
                                tone = "Possible cause"

                            st.markdown(f"""
                        **{tone} that {svc} is driving the anomaly**

                        <span style="font-size:12px; opacity:0.7;">
                        Unusual behavior is centered around <b>{svc}</b>, impacting connected services and overall system performance.
                        </span>
                        """, unsafe_allow_html=True)

                            st.caption(f"{confidence:.1f}% confidence")

                            # 🔥 keep your breakdown bars
                            for svc, score in rc['scores'].items():
                                st.progress(score, text=svc)

                    st.markdown("---")

with tabs[4]:

    subtab1, subtab2, subtab3 = st.tabs([
        "📄 Logs",
        "⚡ Actions",
        "📊 System Report"
    ])

    # =========================================
    # 📄 LOGS
    # =========================================
    with subtab1:

        st.subheader("📄 Logs")

        colF, colS = st.columns([2,1])

        with colF:
            service_filter = st.selectbox(
                "Filter Service",
                ["All"] + list(df['service'].unique())
            )

        filtered_df = df if service_filter == "All" else df[df['service'] == service_filter]

        st.dataframe(filtered_df.tail(25), use_container_width=True)

    # =========================================
    # ⚡ ACTIONS (DOWNLOAD + AI)
    # =========================================
    with subtab2:

        download_logs(df)
        generate_ai_report(df, correlated_incidents, root_causes)

    # =========================================
    # 📊 SYSTEM REPORT
    # =========================================
    with subtab3:

        generate_report(df, correlated_incidents, root_causes)

    
# ---------------- GLOBAL REFRESH LOOP ----------------
REFRESH_INTERVAL = 5  # seconds
now = time.time()

# Only refresh if AI NOT running
if not st.session_state.ai_running and not st.session_state.report_running:
    if now - st.session_state.last_refresh >= REFRESH_INTERVAL:
        st.session_state.refresh_count += 1
        st.session_state.last_refresh = now

# Heartbeat loop
if st.session_state.ai_running or st.session_state.report_running:
    time.sleep(1)
    st.rerun()
else:
    time.sleep(2)
=======
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import time
from sklearn.exceptions import NotFittedError
import threading
import plotly.graph_objects as go
import math

# CORE IMPORTS
from ingestion.log_generator import generate_logs
from processing.preprocessor import preprocess
from models.anomaly_model import AnomalyDetector
from alerts.alert_manager import generate_alerts
from utils.helpers import get_summary
from processing.correlation import correlate_events
from analysis.root_cause import find_root_cause
from processing.feature_engineering import extract_features
from utils.storage import save_anomalies, save_incidents, save_root_causes

# UI IMPORTS
from ui.ui import system_pipeline, throughput_meter, anomaly_heatmap
from ui.features import replay_system, ai_explanation, incident_timeline, clustering_view, training_simulation
from ui.ui import anomaly_trend
from report import login_system, download_logs, generate_report, alert_sound, generate_ai_report

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_system()
    st.stop()

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Sidebar width */
section[data-testid="stSidebar"] {
    width: 220px !important;
}

/* ---------- CARD SYSTEM ---------- */
.card {
    background: #111827;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 10px;
    transition: all 0.2s ease-in-out;
}

.card:hover {
    transform: translateY(-2px);
    border: 1px solid rgba(0,255,255,0.3);
}

/* ---------- METRICS ---------- */
[data-testid="stMetric"] {
    background: #111827;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* ---------- ALERT FEED ---------- */
.alert-box {
    padding: 8px;
    margin-bottom: 6px;
    border-radius: 10px;
    font-size: 13px;
}

/* ---------- SCROLL AREAS ---------- */
.scroll-box {
    max-height: 300px;
    overflow-y: auto;
}

/* ---------- TABS ---------- */
.stTabs [role="tab"] {
    font-size: 14px;
}

/* ---------- REMOVE PLOT BACKGROUND ---------- */
.js-plotly-plot {
    border-radius: 12px;
}

/* ---------- SIDEBAR UPGRADE ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    border-right: 1px solid rgba(255,255,255,0.05);
    padding-top: 10px;
}

section[data-testid="stSidebar"] .card {
    box-shadow: 0 0 10px rgba(0,255,255,0.05);
}

/* REMOVE EMPTY SIDEBAR CARDS */
section[data-testid="stSidebar"] .card:empty {
    display: none !important;
}

section[data-testid="stSidebar"] .element-container:has(.card:empty) {
    display: none !important;
}

section[data-testid="stSidebar"] .element-container {
    margin-bottom: 4px !important;
}

/* METRIC CARD ENHANCEMENT */
.metric-card {
    position: relative;
    overflow: hidden;
}

.metric-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top right, rgba(0,255,255,0.15), transparent 60%);
    opacity: 0;
    transition: 0.3s;
}

.metric-card:hover::after {
    opacity: 1;
}

/* ---------- REGION CARDS ---------- */
.region-card {
    transition: all 0.2s ease-in-out;
    position: relative;
}

.region-card:hover {
    transform: translateY(-2px);
    border: 1px solid rgba(0,255,255,0.3);
}

/* Status text */
.region-status {
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.5px;
}

/* Subtext */
.region-meta {
    font-size: 12px;
    opacity: 0.7;
}

/* Subtle glow effect */
.region-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top right, rgba(0,255,255,0.12), transparent 60%);
    opacity: 0;
    transition: 0.3s;
}

.region-card:hover::after {
    opacity: 1;
}

/* ---------- NODE CARDS ---------- */
.node-card {
    text-align: center;
    transition: all 0.2s ease-in-out;
    position: relative;
}

/* Hover effect (stronger than region cards) */
.node-card:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 0 15px rgba(0,255,255,0.15);
}

/* Status styling */
.node-status {
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 0.5px;
}

/* Glow pulse for critical (optional visual depth) */
.node-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, rgba(0,255,255,0.12), transparent 70%);
    opacity: 0;
    transition: 0.3s;
}

.node-card:hover::after {
    opacity: 1;
}

</style>
""", unsafe_allow_html=True)

# Auto refresh every 5 seconds
# ---------------- REFRESH CONTROL ----------------
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if "ai_running" not in st.session_state:
    st.session_state.ai_running = False
    
if "report_running" not in st.session_state:
    st.session_state.report_running = False

if "ai_done_event" not in st.session_state:
    st.session_state.ai_done_event = threading.Event()

# ---------------- TITLE ----------------
st.title("🚀 AI-Powered Log Monitoring System")

st.sidebar.markdown(f"""
<div class="card">
    👤 <b>User</b><br>
    {st.session_state.role}
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="card">
    <b>🧠 System Status</b><br><br>
    🟢 Model: Active<br>
    ⚡ Stream: Running<br>
    🔄 Refresh: 5s
</div>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
if "log_store" not in st.session_state:
    st.session_state["log_store"] = pd.DataFrame()

# ---------------- DATA STREAM ----------------

if "log_store" not in st.session_state:
    st.session_state["log_store"] = pd.DataFrame()

# --- STREAM CONTROL ---
st.sidebar.markdown('<div class="card">', unsafe_allow_html=True)

st.sidebar.markdown("### ⚙️ Stream Control")

logs_per_sec = st.sidebar.slider("Logs/sec", 5, 50, 10)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

refresh_interval = 5
batch_size = logs_per_sec * refresh_interval

# Generate new logs
# ---------------- CONTROLLED LOG GENERATION ----------------
if "last_log_gen" not in st.session_state:
    st.session_state.last_log_gen = 0

now = time.time()
REFRESH_INTERVAL = 5

if now - st.session_state.last_log_gen >= REFRESH_INTERVAL:
    new_logs = generate_logs(batch_size=batch_size)
    st.session_state.last_log_gen = now
else:
    new_logs = pd.DataFrame(columns=st.session_state["log_store"].columns)

# Temporary dataset for training
temp_df = pd.concat(
    [st.session_state["log_store"], new_logs],
    ignore_index=True
)

# ---------------- PREPROCESS ----------------
X = preprocess(temp_df)
X = extract_features(X)

# ---------------- MODEL ----------------
if "model" not in st.session_state:
    st.session_state["model"] = AnomalyDetector(contamination=0.05)

model = st.session_state["model"]

RETRAIN_THRESHOLD = max(100, int(0.1 * len(temp_df)))

if "last_trained_size" not in st.session_state:
    st.session_state["last_trained_size"] = 0

if "model_trained" not in st.session_state:
    st.session_state["model_trained"] = False

# 🔥 ALWAYS TRAIN IF NOT TRAINED OR DATA IS SMALL
if not st.session_state["model_trained"] or len(temp_df) < 50:
    model.train(X)
    st.session_state["last_trained_size"] = len(temp_df)
    st.session_state["model_trained"] = True

# 🔁 PERIODIC RETRAIN
elif len(temp_df) - st.session_state["last_trained_size"] > RETRAIN_THRESHOLD:
    model.train(X)
    st.session_state["last_trained_size"] = len(temp_df)

# ---------------- PREDICT ONLY NEW LOGS ----------------
if len(new_logs) > 0:
    new_X = preprocess(new_logs)
    new_X = extract_features(new_X)

    preds = model.predict(new_X)
    scores = model.get_scores(new_X)

    # ✅ Use safe default values instead of None
    new_logs['anomaly'] = 0
    new_logs['anomaly_score'] = scores.mean() if len(scores) > 0 else 0.0

    # ✅ Fill only valid rows
    new_logs.loc[new_X.index, 'anomaly'] = preds
    new_logs.loc[new_X.index, 'anomaly_score'] = scores

# ---------------- STORE FINAL DATA ----------------
st.session_state["log_store"] = pd.concat(
    [st.session_state["log_store"], new_logs],
    ignore_index=True
)

# limit size
MAX_LOGS = 10000
if len(st.session_state["log_store"]) > MAX_LOGS:
    st.session_state["log_store"] = st.session_state["log_store"].tail(MAX_LOGS)

df = st.session_state["log_store"]

# feature flags
df['error_flag'] = (df['level']=='ERROR').astype(int)
df['warn_flag'] = (df['level']=='WARN').astype(int)

alerts = generate_alerts(df)
stats = get_summary(df)

st.sidebar.markdown('<div class="card">', unsafe_allow_html=True)
st.sidebar.markdown("**📊 Live Stats**")

st.sidebar.write(f"Logs: {stats['total_logs']}")
st.sidebar.write(f"Anomalies: {stats['anomalies']}")
st.sidebar.write(f"Services: {stats['services']}")

st.sidebar.markdown('</div>', unsafe_allow_html=True)

correlated_incidents = correlate_events(df)
root_causes = find_root_cause(df, correlated_incidents)

save_anomalies(df)
save_incidents(correlated_incidents)
save_root_causes(root_causes)

tabs = st.tabs(["Overview", "System", "Analytics", "Intelligence", "Data"])

with tabs[0]:
    # ---------------- TOP METRICS ----------------
    c1,c2,c3,c4 = st.columns(4)

    def metric_card(title, value, color="#ffffff"):
        return f"""
        <div class="card metric-card">
            <div style="font-size:12px; opacity:0.6;">{title}</div>
            <div style="font-size:32px; font-weight:800; color:{color}; margin-top:5px;">
                {value}
            </div>
        </div>
        """

    c1.markdown(metric_card("Logs", stats['total_logs'], "#00f2ff"), unsafe_allow_html=True)
    c2.markdown(metric_card("Anomalies", stats['anomalies'], "#ff4d4d"), unsafe_allow_html=True)
    c3.markdown(metric_card("Services", stats['services'], "#ffaa00"), unsafe_allow_html=True)
    c4.markdown(metric_card("Status", "RUNNING", "#00ffcc"), unsafe_allow_html=True)

    # ---------------- GLOBAL VIEW ----------------
    st.subheader("🌍 Global System View")
    
    def region_card(region, status, anomaly, color):
        return f"""<div class="card region-card">
    <b>🌍 {region}</b><br>
    <span class="region-status" style="color:{color};">{status}</span><br>
    <span class="region-meta">Anomalies: {anomaly}</span>
    </div>"""

    region_map = {
        "Auth Service": "US-East",
        "Payment API": "EU-West",
        "Database": "India",
        "User Service": "Asia",
        "Cache Layer": "India"
    }

    df['region'] = df['service'].map(region_map)

    region_stats = df.groupby('region')['anomaly'].sum().reset_index()

    cols = st.columns(4)

    for i, (_, row) in enumerate(region_stats.iterrows()):
        ratio = row['anomaly'] / len(df)

        if ratio < 0.03:
            color = "#00ffcc"
            status = "HEALTHY"
        elif ratio < 0.08:
            color = "#ffaa00"
            status = "DEGRADED"
        else:
            color = "#ff4d4d"
            status = "CRITICAL"

        cols[i].markdown(
            region_card(row['region'], status, int(row['anomaly']), color),
            unsafe_allow_html=True
        )

    # ---------------- NODES ----------------
    st.subheader("🌐 Service Nodes")
    
    def node_card(service, status, color):
        return f"""<div class="card node-card">
    <b>{service}</b><br>
    <span class="node-status" style="color:{color};">{status}</span>
    </div>"""

    cols = st.columns(5)
    services = df['service'].unique()

    for i, svc in enumerate(services):
        svc_df = df[df['service'] == svc]

        if len(svc_df) == 0:
            status = "UNKNOWN"
            color = "#888"
        else:
            ratio = svc_df['anomaly'].sum() / len(svc_df)

            if ratio < 0.05:
                status = "HEALTHY"
                color = "#00ffcc"
            elif ratio < 0.12:
                status = "DEGRADED"
                color = "#ffaa00"
            else:
                status = "CRITICAL"
                color = "#ff4d4d"

        cols[i].markdown(
            node_card(svc, status, color),
            unsafe_allow_html=True
        )

with tabs[1]:
    subtab1, subtab2 = st.tabs([
        "🔗 System Graph",
        "🚨 Alerts"
    ])
    
    with subtab1:
        st.markdown("## 🔗 Service Dependency Graph")

        edges = [
            ("User Service", "Auth Service"),
            ("User Service", "Payment API"),

            ("Cache Layer", "User Service"),

            ("Auth Service", "Database"),
            
            ("Cache Layer", "Database"),
            ("User Service", "Database"),
        ]

        # unique nodes
        nodes = list(set([n for edge in edges for n in edge]))

        positions = {
            "User Service": (1.6, 0),

            "Auth Service": (0.3, 0.9),
            "Database": (0.3, -1.0),

            "Payment API": (-1.3, 0.5),
            "Cache Layer": (-1.3, -0.5),
        }

        # edges
        edge_x, edge_y = [], []
        for src, dst in edges:
            x0, y0 = positions[src]
            x1, y1 = positions[dst]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        # nodes
        node_x = [positions[n][0] for n in nodes]
        node_y = [positions[n][1] for n in nodes]

        fig = go.Figure()

        # ✨ GLOW LAYER (background edges)
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=8, color='rgba(0,255,255,0.08)'),
            hoverinfo='none',
            mode='lines'
        ))

        # 🔥 MAIN EDGES
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=3, color='rgba(0,255,255,0.5)'),
            hoverinfo='skip',  # 🔥 prevents hover junk
            mode='lines'
        ))

        # ✨ NODE GLOW LAYER
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker=dict(
                size=45,
                color='rgba(0,255,255,0.15)'
            ),
            hoverinfo='none'
        ))

        # 🔵 MAIN NODES
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=nodes,
            textposition="bottom center",
            hovertemplate="<b>%{text}</b><extra></extra>",  # 🔥 THIS LINE FIXES IT
            marker=dict(
                size=28,
                color="#00f2ff",
                line=dict(width=2, color='white')
            )
        ))

        fig.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
        )

        # ✅ REMOVED EMPTY CARD WRAPPER (fixes that rectangle)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

    with subtab2:
        # ---------------- ALERTS ----------------
        st.markdown("## 🚨 Alerts")

        st.markdown('<div class="scroll-box">', unsafe_allow_html=True)

        for _, row in alerts.tail(10).iterrows():
            color = {
                "HIGH": "#ff4d4d",
                "MEDIUM": "#ffaa00",
                "LOW": "#00ffcc"
            }[row['severity']]

            bg = {
                "HIGH": "rgba(255,77,77,0.06)",
                "MEDIUM": "rgba(255,170,0,0.06)",
                "LOW": "rgba(0,255,204,0.06)"
            }[row['severity']]

            st.markdown(f"""
        <div class="alert-box" style="
            border-left:3px solid {color};
            background:{bg};
            padding:8px 10px;
            border-radius:8px;
            margin-bottom:6px;
        ">

        <div style="font-size:13px; font-weight:600;">
            {row['service']}
        </div>

        <div style="
            margin-top:4px;
            font-size:11px;
            padding:2px 6px;
            display:inline-block;
            border-radius:6px;
            background:{color}20;
            color:{color};
            font-weight:600;
        ">
        Severity: {row['severity']}
        </div>

        <div style="font-size:11px; opacity:0.7; margin-top:4px;">
        Response Time: {row['response_time']:.1f} ms
        </div>

        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if len(alerts) > 5:
            alert_sound()

with tabs[2]:
    subtab1, subtab2, subtab3, subtab4 = st.tabs([
        "📈 Trends & Load",
        "📊 Score Distribution",
        "⚡ Throughput & Heatmap",
        "📉 Anomaly Trend"
    ])
    # ---------------- CHARTS ----------------
    with subtab1:
        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(
                df,
                x="timestamp",
                y="response_time",
                title="Response Time Trend"
            )

            fig.update_traces(line=dict(width=2))

            fig.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis_title="Response Time (ms)"
            )

            st.plotly_chart(fig, use_container_width=True)


        with col2:
            # 🔥 FIX: proper dataframe instead of raw value_counts
            service_counts = df['service'].value_counts().reset_index()
            service_counts.columns = ["service", "requests"]

            fig2 = px.bar(
                service_counts,
                x="service",
                y="requests",
                title="Service Request Load"
            )

            fig2.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis_title="Requests"
            )

            st.plotly_chart(fig2, use_container_width=True)

    with subtab2:
        st.subheader("📈 Anomaly Score Distribution")

        if 'anomaly_score' in df.columns:

            # ================================
            # 📊 Histogram
            # ================================
            fig = px.histogram(
                df,
                x="anomaly_score",
                nbins=40,
                opacity=0.85
            )

            # ================================
            # 📌 Stats
            # ================================
            mean_val = df["anomaly_score"].mean()

            x0 = df["anomaly_score"].quantile(0.05)
            x1 = df["anomaly_score"].quantile(0.99)

            normal_pct = (
                (df["anomaly_score"] >= x0) &
                (df["anomaly_score"] <= x1)
            ).mean() * 100

            # ================================
            # 🟢 NORMAL ZONE (CLEAN VERSION)
            # ================================
            fig.add_vrect(
                x0=x0,
                x1=x1,
                fillcolor="green",
                opacity=0.08,
                layer="below",
                line_width=0,
                annotation_text=f"Normal ({normal_pct:.0f}%)",
                annotation_position="top left"
            )

            # ================================
            # 📍 Boundary Lines (IMPORTANT)
            # ================================
            fig.add_vline(x=x0, line_color="green", opacity=0.4)
            fig.add_vline(x=x1, line_color="green", opacity=0.4)

            # ================================
            # 🔴 Mean Line
            # ================================
            fig.add_vline(
                x=mean_val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean {mean_val:.2f}",
                annotation_position="top"
            )

            # ================================
            # 🎨 Styling (BIG IMPACT)
            # ================================
            fig.update_layout(
                title=None,
                margin=dict(l=10, r=10, t=20, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Anomaly Score",
                yaxis_title="Frequency",
                hovermode="x unified",
                bargap=0.05
            )

            # smoother bars
            fig.update_traces(
                marker=dict(
                    line=dict(width=0),
                )
            )

            # ================================
            # 🚀 Render
            # ================================
            st.plotly_chart(fig, use_container_width=True)
            
    with subtab3:
        # ---------------- ADVANCED ----------------

        colA, colB = st.columns(2)

        with colA:
            throughput_meter(df)

        with colB:
            anomaly_heatmap(df)

    with subtab4:
        anomaly_trend(df)

with tabs[3]:
    # ---------------- ULTRA ----------------

    df['error_flag'] = (df['level'] == 'ERROR').astype(int)
    df['warn_flag'] = (df['level'] == 'WARN').astype(int)

    tab1, tab2, tab3, tab4 = st.tabs(["Replay","Insights","Clustering","Correlation"])

    with tab1:
        replay_system(df)

    with tab2:
        colL, colR = st.columns(2)

        with colL:
            ai_explanation(df, correlated_incidents, root_causes)

        with colR:
            incident_timeline(df)

    with tab3:
        colL, colR = st.columns(2)

        with colL:
            clustering_view(df)

        with colR:
            training_simulation(df)

    with tab4:
        def render_incident_card(inc, sev_color):
            return f"""<div style="padding:16px;margin-bottom:16px;border-radius:12px;background:rgba(255,255,255,0.02);border-left:5px solid {sev_color};">

        <div style="display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:15px;font-weight:600;">
        🔴 Incident Window
        </div>
        <div style="font-size:12px;opacity:0.6;">
        {inc['start_time']} → {inc['end_time']}
        </div>
        </div>

        <div style="margin-top:10px;font-size:13px;opacity:0.8;">
        ⚙️ <b>Primary:</b> {", ".join(inc['primary_services'])}<br>
        🔗 <b>Affected:</b> {", ".join(inc['services'])}
        </div>

        <div style="display:flex;gap:20px;margin-top:12px;font-size:13px;">
        <div>📊 <b>{inc['anomaly_count']}</b> anomalies</div>
        <div>⏱ <b>{inc['avg_response']:.0f} ms</b></div>
        <div style="color:{sev_color};">
        🚨 <b>{inc['severity']}</b>
        </div>
        </div>

        </div>"""
        
        def render_rca_card(rc):
            return f"""<div style="margin-top:-10px;margin-bottom:15px;padding:14px;border-radius:10px;background:linear-gradient(90deg, rgba(0,150,255,0.08), rgba(0,255,200,0.05));">

        <div style="font-size:13px;opacity:0.7;">
        🧠 Root Cause Analysis
        </div>

        <div style="font-size:16px;font-weight:600;margin-top:4px;">
        {rc['root_cause']}
        </div>

        <div style="font-size:12px;opacity:0.6;margin-top:4px;">
        Confidence: {rc['confidence'] * 100:.1f}%
        </div>

        </div>"""
        
        def render_bar(svc, score):
            return f"""<div style="margin-bottom:6px;">
        <div style="font-size:12px;">{svc}</div>
        <div style="height:6px;border-radius:5px;background:rgba(255,255,255,0.08);overflow:hidden;">
        <div style="width:{score*100}%;height:100%;background:#00f2ff;"></div>
        </div>
        </div>"""
        
        if len(correlated_incidents) == 0:
            st.info("No correlated incidents detected")

        else:
            for i, inc in enumerate(correlated_incidents[-5:]):
                sev_color = {
                    "LOW": "🟢",
                    "MEDIUM": "🟡",
                    "HIGH": "🔴"
                }.get(inc['severity'], "🟢")

                with st.container():

                    # =========================
                    # 🔥 HEADER (INLINE)
                    # =========================
                    c1, c2 = st.columns([2, 3])

                    c1.markdown(f"**{sev_color} Incident**")
                    c2.markdown(
                        f"<div style='font-size:11px;opacity:0.6;text-align:right;'>{inc['start_time']} → {inc['end_time']}</div>",
                        unsafe_allow_html=True
                    )

                    # =========================
                    # 🔥 SERVICES (INLINE)
                    # =========================
                    primary = ", ".join(inc['primary_services'])
                    affected = ", ".join(inc['services'])

                    st.markdown(
                        f"<div style='font-size:12px;opacity:0.8;'>"
                        f"⚙️ <b>Primary services:</b> {primary} &nbsp;&nbsp; | &nbsp;&nbsp; "
                        f"🔗 <b>Affected services:</b> {affected}"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    # =========================
                    # 🔥 STATS (ONE LINE)
                    # =========================
                    st.markdown(
                        f"<div style='font-size:13px;margin-top:4px;'>"
                        f"📊 <b>{inc['anomaly_count']}</b> &nbsp;&nbsp; "
                        f"⏱ <b>{inc['avg_response']:.0f} ms</b> &nbsp;&nbsp; "
                        f"{sev_color} <b>{inc['severity']}</b>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    # =========================
                    # 🧠 RCA (COLLAPSED ONLY)
                    # =========================
                    if i < len(root_causes):
                        rc = root_causes[i]

                        with st.expander("🧠 RCA"):
                            svc = rc['root_cause']
                            confidence = rc['confidence'] * 100

                            # 🔥 HUMAN-READABLE EXPLANATION
                            if confidence > 70:
                                tone = "Strong indication"
                            elif confidence > 40:
                                tone = "Moderate indication"
                            else:
                                tone = "Possible cause"

                            st.markdown(f"""
                        **{tone} that {svc} is driving the anomaly**

                        <span style="font-size:12px; opacity:0.7;">
                        Unusual behavior is centered around <b>{svc}</b>, impacting connected services and overall system performance.
                        </span>
                        """, unsafe_allow_html=True)

                            st.caption(f"{confidence:.1f}% confidence")

                            # 🔥 keep your breakdown bars
                            for svc, score in rc['scores'].items():
                                st.progress(score, text=svc)

                    st.markdown("---")

with tabs[4]:

    subtab1, subtab2, subtab3 = st.tabs([
        "📄 Logs",
        "⚡ Actions",
        "📊 System Report"
    ])

    # =========================================
    # 📄 LOGS
    # =========================================
    with subtab1:

        st.subheader("📄 Logs")

        colF, colS = st.columns([2,1])

        with colF:
            service_filter = st.selectbox(
                "Filter Service",
                ["All"] + list(df['service'].unique())
            )

        filtered_df = df if service_filter == "All" else df[df['service'] == service_filter]

        st.dataframe(filtered_df.tail(25), use_container_width=True)

    # =========================================
    # ⚡ ACTIONS (DOWNLOAD + AI)
    # =========================================
    with subtab2:

        download_logs(df)
        generate_ai_report(df, correlated_incidents, root_causes)

    # =========================================
    # 📊 SYSTEM REPORT
    # =========================================
    with subtab3:

        generate_report(df, correlated_incidents, root_causes)

    
# ---------------- GLOBAL REFRESH LOOP ----------------
REFRESH_INTERVAL = 5  # seconds
now = time.time()

# Only refresh if AI NOT running
if not st.session_state.ai_running and not st.session_state.report_running:
    if now - st.session_state.last_refresh >= REFRESH_INTERVAL:
        st.session_state.refresh_count += 1
        st.session_state.last_refresh = now

# Heartbeat loop
if st.session_state.ai_running or st.session_state.report_running:
    time.sleep(1)
    st.rerun()
else:
    time.sleep(2)
>>>>>>> c6ce973896de6344d39dfdb3b27aa16fbc20feab
    st.rerun()