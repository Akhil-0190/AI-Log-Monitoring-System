import streamlit as st
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
import requests
import subprocess
from sklearn.preprocessing import StandardScaler
from utils.storage import save_text

import streamlit as st
import threading

def replay_system(df):
    import streamlit as st
    import pandas as pd

    st.subheader("🎞 Incident Replay")

    # --- Freeze dataset ---
    if "replay_df" not in st.session_state:
        st.session_state.replay_df = df.copy()

    replay_df = st.session_state.replay_df.reset_index(drop=True)

    # --- Persist slider ---
    if "replay_step" not in st.session_state:
        st.session_state.replay_step = int(len(replay_df) / 2)

    # --- Reload button ---
    clicked = st.button("🔄 Reload")

    st.markdown(
        '<div style="font-size:13px; opacity:0.5; margin-bottom:-5px;">Replay timeline</div>',
        unsafe_allow_html=True
    )

    if clicked:
        st.session_state.replay_df = df.copy()
        st.session_state.replay_step = 0

    # --- Timeline slider ---
    step = st.slider(
        " ",
        0,
        len(replay_df) - 1,
        st.session_state.replay_step,
        key="replay_slider"
    )

    st.session_state.replay_step = step

    subset = replay_df.iloc[:step]

    # ============================
    # 🔥 LIVE STATS (THIS FIXES EMPTY SPACE)
    # ============================
    c1, c2, c3 = st.columns(3)

    total = len(subset)
    anomalies = subset['anomaly'].sum() if 'anomaly' in subset else 0
    avg_rt = subset['response_time'].mean() if len(subset) else 0

    c1.metric("Logs Seen", total)
    c2.metric("Anomalies", int(anomalies))
    c3.metric("Avg Response", f"{avg_rt:.1f} ms")

    st.write(f"Showing logs up to step: {step}")

    # ============================
    # 📋 CLEAN TABLE
    # ============================
    st.markdown("### Latest Logs")

    st.dataframe(
        subset.tail(10),
        use_container_width=True,
        height=300
    )

def get_ai_response(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("response", "No response")
    else:
        return f"HTTP Error: {response.status_code}"

def run_insights_task(prompt, result_container):
    try:
        result = get_ai_response(prompt)
        result_container["result"] = result
    except Exception as e:
        result_container["result"] = f"Error: {e}"
        
def ai_explanation(df, incidents=None, root_causes=None):
    import streamlit as st

    st.subheader("🧠 AI Explanation Engine")

    anomalies = df[df['anomaly'] == 1]

    if len(anomalies) == 0:
        st.info("No anomalies detected")
        return

    if "ai_insight_result" not in st.session_state:
        st.session_state["ai_insight_result"] = None

    if "ai_running" not in st.session_state:
        st.session_state.ai_running = False

    if st.button("⚡ Generate", key="insights_btn"):
        if not st.session_state.ai_running:
            st.session_state.ai_running = True
            st.session_state["ai_insight_result"] = None

            sample = anomalies.tail(10)[['service','response_time','level']].to_string()

            incident_text = str(incidents[-3:]) if incidents else ""
            rca_text = str(root_causes[-3:]) if root_causes else ""

            prompt = f""" 
            You are a real-time monitoring assistant. 
            Recent anomalies: {sample} 
            Correlated incidents: {incident_text} 
            Root cause analysis: {rca_text} 
            Provide:
            - 2–3 key observations 
            - What is happening in system 
            - Likely cause (based on RCA) 
            - Immediate action suggestion 
            Keep it: 
            - short 
            - operational 
            - not verbose 
            """

            st.session_state["insight_temp"] = {}

            thread = threading.Thread(
                target=run_insights_task,
                args=(prompt, st.session_state["insight_temp"])
            )
            thread.start()

    st.caption("AI-generated incident diagnosis")

    # 🔄 Loading
    if st.session_state.ai_running:
        temp = st.session_state.get("insight_temp", {})

        if "result" in temp:
            st.session_state["ai_insight_result"] = temp["result"]
            save_text("insights.txt", temp["result"])
            st.session_state.ai_running = False
        else:
            st.markdown("""
            <div style="
                padding:12px;
                border-radius:10px;
                background:rgba(255,165,0,0.08);
                font-size:14px;
            ">
                ⚡ Generating insights...
            </div>
            """, unsafe_allow_html=True)

    # =========================
    # 🔥 BEAUTIFIED OUTPUT
    # =========================
    if st.session_state["ai_insight_result"]:
        text = st.session_state["ai_insight_result"]

        st.markdown(f"""
        <div style="
            padding:18px;
            border-radius:12px;
            background:rgba(0,255,150,0.06);
            line-height:1.6;
            font-size:14px;
        ">
            {text.replace("\n", "<br>")}
        </div>
        """, unsafe_allow_html=True)

def incident_timeline(df):
    import streamlit as st

    st.subheader("📜 Incident Timeline")

    anomalies = df[df['anomaly'] == 1].tail(6)

    if len(anomalies) == 0:
        st.info("No incidents detected")
        return

    for _, row in anomalies.iterrows():
        st.markdown(
            f"""
    <div style="display:flex;align-items:center;gap:12px;padding:10px;margin-bottom:8px;border-radius:10px;background:rgba(255,77,77,0.05);">

    <div style="width:10px;height:10px;border-radius:50%;background:#ff4d4d;"></div>

    <div style="font-size:13px;">
    <b>{row['service']}</b> anomaly<br>
    <span style="opacity:0.6;">{row['timestamp']}</span>
    </div>

    </div>
    """,
            unsafe_allow_html=True
        )

def clustering_view(df):
    import streamlit as st
    import plotly.express as px
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans

    st.subheader("🎯 Anomaly Clustering")

    try:
        if len(df) < 10:
            st.warning("Not enough data")
            return

        # ================================
        # 🔧 FEATURE ENGINEERING
        # ================================
        df['error_flag'] = (df['level'] == 'ERROR').astype(int)
        df['warn_flag'] = (df['level'] == 'WARN').astype(int)

        X = df[['response_time', 'error_flag', 'warn_flag']].fillna(0)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)

        df['cluster'] = clusters  # ✅ keep as int (important fix)

        # ================================
        # 🧠 CLUSTER LABELING
        # ================================
        cluster_summary = {}

        for i in range(3):
            cdf = df[df['cluster'] == i]

            avg_rt = cdf['response_time'].mean()
            error_rate = cdf['error_flag'].mean()
            warn_rate = cdf['warn_flag'].mean()

            if error_rate > 0.3:
                label = "High Error"
            elif warn_rate > 0.3:
                label = "Warning Heavy"
            elif avg_rt > 300:
                label = "High Latency"
            else:
                label = "Normal"

            cluster_summary[i] = label

        # Map labels
        df['cluster_label'] = df['cluster'].map(cluster_summary)

        # ================================
        # 🎨 COLOR MAP (consistent UI)
        # ================================
        colors = {
            "High Error": "#ff4d4d",
            "Warning Heavy": "#ffaa00",
            "High Latency": "#00ccff",
            "Normal": "#00ffcc"
        }

        # ================================
        # 📊 COMPACT CLUSTER SUMMARY
        # ================================
        col1, col2, col3 = st.columns(3)

        for i, col in enumerate([col1, col2, col3]):
            cluster_df = df[df['cluster'] == i]
            label = cluster_summary[i]

            with col:
                # Label (colored)
                st.markdown(f"""
                <div style="font-weight:600;color:{colors[label]};font-size:14px;">
                {label}
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-top:4px;
                ">

                <div style="font-size:20px;font-weight:700;">
                {len(cluster_df)}
                </div>

                <div style="font-size:12px;opacity:0.6;">
                {cluster_df['response_time'].mean():.0f} ms
                </div>

                </div>
                """, unsafe_allow_html=True)

        # spacing
        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

        # ================================
        # 📈 SCATTER PLOT
        # ================================
        fig = px.scatter(
            df,
            x='response_time',
            y='cluster_label',
            color='cluster_label',
            size='response_time',
            hover_data=['service', 'level'],
            title="Cluster Distribution (Behavior Segmentation)",
            color_discrete_map=colors  # ✅ consistent colors
        )

        # Fix axis type
        fig.update_yaxes(type='category')

        fig.update_traces(marker=dict(opacity=0.8))

        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text="Cluster Type"
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Clustering error: {e}")
        
def training_simulation(df):
    import streamlit as st
    import time
    from sklearn.ensemble import IsolationForest

    st.subheader("🧪 Model Training")

    # 🔥 progress bar
    progress = st.progress(0, text="Initializing model...")

    start = time.time()

    for i in range(3):
        time.sleep(0.2)
        progress.progress((i + 1) * 30, text="Training in progress...")

    X = df[['response_time', 'error_flag', 'warn_flag']]

    model = IsolationForest(contamination=0.02, random_state=42)
    model.fit(X)

    duration = time.time() - start

    progress.progress(100, text="Training complete ✅")

    # 🔥 clean success card
    st.markdown(f"""
    <div style="
        padding:16px;
        border-radius:12px;
        background:rgba(0,255,120,0.08);
        margin-top:10px;
    ">
        <div style="font-size:14px; opacity:0.7;">
            Model Status
        </div>
        <div style="font-size:20px; font-weight:700;">
            Training completed in {duration:.2f}s
        </div>
        <div style="font-size:12px; opacity:0.6;">
            Model trained on current batch
        </div>
    </div>
    """, unsafe_allow_html=True)