<<<<<<< HEAD
import streamlit as st
from ui.features import get_ai_response
from utils.storage import save_text

import threading

def run_report_task(prompt, result_container):
    try:
        result = get_ai_response(prompt)
        result_container["result"] = result
    except Exception as e:
        result_container["result"] = f"Error: {e}"

# ---------------- LOGIN ----------------
def login_system():
    st.title("🔐 Secure System Access")

    with st.form("login_form", clear_on_submit=False):
        role = st.selectbox("Select Role", ["Admin"])
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:
            if user == "admin" and pwd == "admin":
                st.session_state.logged_in = True
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------------- DOWNLOAD ----------------
def download_logs(df):
    st.subheader("📊 Export Logs")

    csv = df.to_csv(index=False).encode()
    st.download_button("Download Logs", csv, "logs.csv", "text/csv")

# ---------------- REPORT ----------------
def generate_report(df, incidents=None, root_causes=None):
    import streamlit as st
    import threading

    st.markdown("### 📄 System Report")

    total = len(df)
    anomalies = int(df['anomaly'].sum())

    anomaly_ratio = anomalies / total if total else 0
    avg_response = df['response_time'].mean()
    max_response = df['response_time'].max()

    service_stats = df.groupby('service')['anomaly'].sum()

    most_affected = service_stats.idxmax()
    least_affected = service_stats.idxmin()

    # 🔥 SUMMARY CARDS
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Logs", total)
    col2.metric("Anomalies", anomalies)
    col3.metric("Avg Response", f"{avg_response:.0f} ms")
    col4.metric("Max Response", f"{max_response:.0f} ms")

    st.markdown("")

    # 🔥 SYSTEM INSIGHT CARD
    st.markdown(f"""<div style="padding:16px;border-radius:12px;background:rgba(255,255,255,0.03);">

<div style="font-size:14px;opacity:0.7;">
Service Impact
</div>

<div style="margin-top:6px;">
🔴 Most affected: <b>{most_affected}</b><br>
🟢 Least affected: <b>{least_affected}</b>
</div>

<div style="margin-top:10px;font-size:12px;opacity:0.6;">
Anomaly Rate: {anomaly_ratio:.2%}
</div>

</div>""", unsafe_allow_html=True)

    st.markdown("")

def generate_ai_report(df, incidents=None, root_causes=None):
    # ---------------- AI REPORT ----------------
    st.subheader("🧠 AI Analysis")
    
    total = len(df)
    anomalies = int(df['anomaly'].sum())

    anomaly_ratio = anomalies / total if total else 0
    avg_response = df['response_time'].mean()
    max_response = df['response_time'].max()

    service_stats = df.groupby('service')['anomaly'].sum()

    most_affected = service_stats.idxmax()
    least_affected = service_stats.idxmin()

    if "ai_report_result" not in st.session_state:
        st.session_state["ai_report_result"] = None

    # BUTTON TRIGGER
    if st.button("Generate AI Report", key="report_btn"):

        if not st.session_state.ai_running and not st.session_state.report_running:
            st.session_state.report_running = True
            st.session_state["ai_report_result"] = None  # clear old

            sample = df.tail(25)[['service','response_time','level']].to_string()
            
            incident_text = ""
            if incidents:
                incident_text = str(incidents[-3:])

            rca_text = ""
            if root_causes:
                rca_text = str(root_causes[-3:])

            prompt = f"""
            You are generating a structured system report.

            System metrics:
            - Total logs: {total}
            - Anomalies: {anomalies}
            - Avg response: {avg_response:.2f}
            - Max response: {max_response:.2f}
            - Most affected service: {most_affected}

            Recent logs:
            {sample}

            Correlated incidents:
            {incident_text}

            Root cause analysis:
            {rca_text}

            Provide:

            1. System performance summary
            2. Key trends observed
            3. Root cause analysis (based on RCA provided)
            4. Impacted services explanation
            5. Recommendations

            Keep it:
            - structured
            - analytical
            - concise
            - dont ask anything else, only present the report
            """

            # temp storage
            st.session_state["report_temp"] = {}

            thread = threading.Thread(
                target=run_report_task,
                args=(prompt, st.session_state["report_temp"])
            )
            thread.start()
            
    # Check if result ready
    if st.session_state.report_running:
        temp = st.session_state.get("report_temp", {})
        
        if "result" in temp:
            st.session_state["ai_report_result"] = temp["result"]
            save_text("reports.txt", temp["result"])
            
            st.session_state.report_running = False
            
    if st.session_state.report_running:
        st.warning("AI is generating report... please wait ⏳")

    # DISPLAY (persistent)
    if st.session_state["ai_report_result"]:
        st.success(st.session_state["ai_report_result"])

# ---------------- SOUND ----------------
def alert_sound():
    st.markdown("""
    <audio autoplay>
    <source src="https://www.soundjay.com/button/beep-07.wav">
    </audio>
=======
import streamlit as st
from ui.features import get_ai_response
from utils.storage import save_text

import threading

def run_report_task(prompt, result_container):
    try:
        result = get_ai_response(prompt)
        result_container["result"] = result
    except Exception as e:
        result_container["result"] = f"Error: {e}"

# ---------------- LOGIN ----------------
def login_system():
    st.title("🔐 Secure System Access")

    with st.form("login_form", clear_on_submit=False):
        role = st.selectbox("Select Role", ["Admin"])
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:
            if user == "admin" and pwd == "admin":
                st.session_state.logged_in = True
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------------- DOWNLOAD ----------------
def download_logs(df):
    st.subheader("📊 Export Logs")

    csv = df.to_csv(index=False).encode()
    st.download_button("Download Logs", csv, "logs.csv", "text/csv")

# ---------------- REPORT ----------------
def generate_report(df, incidents=None, root_causes=None):
    import streamlit as st
    import threading

    st.markdown("### 📄 System Report")

    total = len(df)
    anomalies = int(df['anomaly'].sum())

    anomaly_ratio = anomalies / total if total else 0
    avg_response = df['response_time'].mean()
    max_response = df['response_time'].max()

    service_stats = df.groupby('service')['anomaly'].sum()

    most_affected = service_stats.idxmax()
    least_affected = service_stats.idxmin()

    # 🔥 SUMMARY CARDS
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Logs", total)
    col2.metric("Anomalies", anomalies)
    col3.metric("Avg Response", f"{avg_response:.0f} ms")
    col4.metric("Max Response", f"{max_response:.0f} ms")

    st.markdown("")

    # 🔥 SYSTEM INSIGHT CARD
    st.markdown(f"""<div style="padding:16px;border-radius:12px;background:rgba(255,255,255,0.03);">

<div style="font-size:14px;opacity:0.7;">
Service Impact
</div>

<div style="margin-top:6px;">
🔴 Most affected: <b>{most_affected}</b><br>
🟢 Least affected: <b>{least_affected}</b>
</div>

<div style="margin-top:10px;font-size:12px;opacity:0.6;">
Anomaly Rate: {anomaly_ratio:.2%}
</div>

</div>""", unsafe_allow_html=True)

    st.markdown("")

def generate_ai_report(df, incidents=None, root_causes=None):
    # ---------------- AI REPORT ----------------
    st.subheader("🧠 AI Analysis")
    
    total = len(df)
    anomalies = int(df['anomaly'].sum())

    anomaly_ratio = anomalies / total if total else 0
    avg_response = df['response_time'].mean()
    max_response = df['response_time'].max()

    service_stats = df.groupby('service')['anomaly'].sum()

    most_affected = service_stats.idxmax()
    least_affected = service_stats.idxmin()

    if "ai_report_result" not in st.session_state:
        st.session_state["ai_report_result"] = None

    # BUTTON TRIGGER
    if st.button("Generate AI Report", key="report_btn"):

        if not st.session_state.ai_running and not st.session_state.report_running:
            st.session_state.report_running = True
            st.session_state["ai_report_result"] = None  # clear old

            sample = df.tail(25)[['service','response_time','level']].to_string()
            
            incident_text = ""
            if incidents:
                incident_text = str(incidents[-3:])

            rca_text = ""
            if root_causes:
                rca_text = str(root_causes[-3:])

            prompt = f"""
            You are generating a structured system report.

            System metrics:
            - Total logs: {total}
            - Anomalies: {anomalies}
            - Avg response: {avg_response:.2f}
            - Max response: {max_response:.2f}
            - Most affected service: {most_affected}

            Recent logs:
            {sample}

            Correlated incidents:
            {incident_text}

            Root cause analysis:
            {rca_text}

            Provide:

            1. System performance summary
            2. Key trends observed
            3. Root cause analysis (based on RCA provided)
            4. Impacted services explanation
            5. Recommendations

            Keep it:
            - structured
            - analytical
            - concise
            - dont ask anything else, only present the report
            """

            # temp storage
            st.session_state["report_temp"] = {}

            thread = threading.Thread(
                target=run_report_task,
                args=(prompt, st.session_state["report_temp"])
            )
            thread.start()
            
    # Check if result ready
    if st.session_state.report_running:
        temp = st.session_state.get("report_temp", {})
        
        if "result" in temp:
            st.session_state["ai_report_result"] = temp["result"]
            save_text("reports.txt", temp["result"])
            
            st.session_state.report_running = False
            
    if st.session_state.report_running:
        st.warning("AI is generating report... please wait ⏳")

    # DISPLAY (persistent)
    if st.session_state["ai_report_result"]:
        st.success(st.session_state["ai_report_result"])

# ---------------- SOUND ----------------
def alert_sound():
    st.markdown("""
    <audio autoplay>
    <source src="https://www.soundjay.com/button/beep-07.wav">
    </audio>
>>>>>>> c6ce973896de6344d39dfdb3b27aa16fbc20feab
    """, unsafe_allow_html=True)