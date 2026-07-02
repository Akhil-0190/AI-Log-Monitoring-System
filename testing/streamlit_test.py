import streamlit as st
import time
import threading

st.title("Reliable Pause + Resume (No Stuck State)")

# ---- GLOBAL THREAD SIGNAL ----
if "done_event" not in st.session_state:
    st.session_state.done_event = threading.Event()

# ---- STATE ----
if "task_running" not in st.session_state:
    st.session_state.task_running = False

if "count" not in st.session_state:
    st.session_state.count = 0

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# ---- BACKGROUND TASK ----
def long_task(done_event):
    time.sleep(20)
    done_event.set()  # ✅ signal completion safely

# ---- BUTTON ----
def start_task():
    if not st.session_state.task_running:
        st.session_state.task_running = True
        st.session_state.done_event.clear()

        thread = threading.Thread(
            target=long_task,
            args=(st.session_state.done_event,)
        )
        thread.start()

st.button("Run 20s Task", on_click=start_task)

# ---- CHECK COMPLETION (SAFE) ----
if st.session_state.task_running and st.session_state.done_event.is_set():
    st.session_state.task_running = False

# ---- REFRESH LOGIC ----
REFRESH_INTERVAL = 5
now = time.time()

if not st.session_state.task_running:
    if now - st.session_state.last_refresh >= REFRESH_INTERVAL:
        st.session_state.count += 1
        st.session_state.last_refresh = now

# ---- UI ----
st.write("Task running:", st.session_state.task_running)
st.write("Refresh count:", st.session_state.count)
st.write("Time:", time.strftime("%H:%M:%S"))

# ---- HEARTBEAT ----
time.sleep(1)
st.rerun()