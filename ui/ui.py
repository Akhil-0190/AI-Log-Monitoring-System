import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd

def system_pipeline():
    st.subheader("🔄 Processing Pipeline")

    st.markdown("""
    <div class="card">
    Logs → Preprocessing → Feature Extraction → ML → Alerts → Dashboard
    </div>
    """, unsafe_allow_html=True)

def throughput_card(throughput, recent):
    return f"""<div style="height:220px;border-radius:16px;padding:24px;display:flex;flex-direction:column;justify-content:center;background:rgba(0,255,255,0.05);border:1px solid rgba(0,255,255,0.15);box-shadow:0 0 20px rgba(0,255,255,0.08);font-family:sans-serif;">

<div style="font-size:14px;opacity:0.6;letter-spacing:0.5px;">
⚡ Logs / Second
</div>

<div style="font-size:52px;font-weight:800;color:#00f2ff;margin-top:8px;">
{throughput:.2f}
</div>

<div style="font-size:12px;opacity:0.5;margin-top:6px;">
Based on last {len(recent)} logs
</div>

</div>"""

def throughput_meter(df):
    st.subheader("⚡ System Throughput")

    recent = df.tail(200)

    # ✅ Ensure datetime
    recent['timestamp'] = pd.to_datetime(recent['timestamp'], errors='coerce')

    time_span = (
        recent['timestamp'].max() - recent['timestamp'].min()
    ).total_seconds()

    throughput = len(recent) / time_span if time_span > 0 else len(recent)

    # ✅ Important: strip() fixes rendering bug sometimes
    st.markdown(
        throughput_card(throughput, recent).strip(),
        unsafe_allow_html=True
    )

def anomaly_heatmap(df):
    st.subheader("🔥 Anomaly Heatmap")

    heat_df = df.copy()

    # 🔥 better aggregation (less noise)
    heat_df = heat_df.groupby(
        ['service', pd.Grouper(key='timestamp', freq='30s')]
    )['response_time'].mean().reset_index()

    pivot = heat_df.pivot(
        index='service',
        columns='timestamp',
        values='response_time'
    )

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=[
            "#0f172a",   # dark
            "#1e3a8a",   # blue
            "#3b82f6",
            "#22c55e",   # green
            "#facc15",   # yellow
            "#ef4444"    # red (hot)
        ],
        title="Response Intensity (Low → High)"
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Time",
        yaxis_title="Service"
    )

    st.plotly_chart(fig, use_container_width=True)
    
def anomaly_trend(df):
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go

    st.subheader("📊 Anomaly Trend Over Time")

    if len(df) == 0 or 'anomaly' not in df.columns:
        st.info("Not enough data")
        return

    temp = df.copy()
    temp = temp.sort_values('timestamp')
    temp['timestamp'] = pd.to_datetime(temp['timestamp'])

    # 🔥 aggregate
    trend = (
        temp.set_index('timestamp')['anomaly']
        .resample('2s')
        .sum()
        .fillna(0)
        .reset_index()
    )

    # 🔥 smooth internally (but DON'T expose name)
    trend['smooth'] = trend['anomaly'].rolling(3).mean()

    fig = go.Figure()

    # 🔹 main line
    fig.add_trace(go.Scatter(
        x=trend['timestamp'],
        y=trend['smooth'],
        mode='lines',
        name='Anomalies',
        line=dict(color='#00f2ff', width=2),
        hovertemplate="Time: %{x}<br>Anomalies: %{y:.2f}<extra></extra>"
    ))

    # 🔥 spike markers
    spikes = trend[trend['anomaly'] > 0]
    fig.add_trace(go.Scatter(
        x=spikes['timestamp'],
        y=spikes['smooth'],
        mode='markers',
        marker=dict(size=6, color='red'),
        name='Spikes',
        hovertemplate="⚠ %{y:.2f} anomalies<extra></extra>"
    ))

    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Time",
        yaxis_title="Anomaly Count"
    )

    st.plotly_chart(fig, use_container_width=True)