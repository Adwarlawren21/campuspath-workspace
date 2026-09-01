import streamlit as st
import pandas as pd
import plotly.express as px
from anthropic import Anthropic

st.set_page_config(page_title="CampusPath Strategy Workspace", page_icon="🎓", layout="wide")

# 1. SIDEBAR & API SETUP
st.sidebar.title("🎓 Project Controls")
st.sidebar.markdown("---")
api_key = st.sidebar.text_input("Enter Anthropic API Key", type="password")

if not api_key:
    st.info("👈 Enter your Anthropic API Key in the sidebar to load the workspace.")
    st.stop()

client = Anthropic(api_key=api_key)

# State Variables
if "stage" not in st.session_state:
    st.session_state.stage = 1
if "messages" not in st.session_state:
    st.session_state.messages = []

st.sidebar.write(f"**Current Phase:** Stage {st.session_state.stage} of 4")

if st.sidebar.button("Advance to Next Stage ➔"):
    if st.session_state.stage < 4:
        st.session_state.stage += 1
        st.rerun()

if st.sidebar.button("Reset Project 🔄"):
    st.session_state.stage = 1
    st.session_state.messages = []
    st.rerun()

# 2. TOP DASHBOARD
st.title("CampusPath Technologies: Product Strategy Workspace")

stages_data = [
    {"Stage": "Stage 1", "Name": "Company Profile & Vision", "Status": "Completed" if st.session_state.stage > 1 else ("In Progress" if st.session_state.stage == 1 else "Pending")},
    {"Stage": "Stage 2", "Name": "Problem Canvas & Bottlenecks", "Status": "Completed" if st.session_state.stage > 2 else ("In Progress" if st.session_state.stage == 2 else "Pending")},
    {"Stage": "Stage 3", "Name": "Workflow & Journey Mapping", "Status": "Completed" if st.session_state.stage > 3 else ("In Progress" if st.session_state.stage == 3 else "Pending")},
    {"Stage": "Stage 4", "Name": "PRD & MVP Requirements", "Status": "Completed" if st.session_state.stage > 4 else ("In Progress" if st.session_state.stage == 4 else "Pending")},
]
df = pd.DataFrame(stages_data)

col_metrics, col_chart = st.columns([1, 2])

with col_metrics:
    progress_pct = int((st.session_state.stage / 4) * 100)
    st.metric(label="Overall Project Completion", value=f"{progress_pct}%")
    st.progress(progress_pct)
    
    st.markdown("### 💡 Recommended Focus")
    stage_guidance = {
        1: "Define CampusPath's core mission statement, target higher-ed audience, and key value proposition.",
        2: "Identify pain points in university student onboarding, application flows, and admin verification.",
        3: "Map out step-by-step user workflows for students and admissions administrators.",
        4: "Formulate complete functional specifications, user stories, and MVP backlog items."
    }
    st.info(stage_guidance[st.session_state.stage])

with col_chart:
    color_map = {"Completed": "#2ECC71", "In Progress": "#3498DB", "Pending": "#BDC3C7"}
    fig = px.bar(
        df, 
        x="Name", 
        y=[1]*len(df), 
        color="Status", 
        color_discrete_map=color_map,
        title="Project Milestone Status",
        labels={"y": "Stage", "Name": "Milestone"}
    )
    fig.update_layout(height=230, showlegend=True, yaxis_visible=False, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 3. CLAUDE CHAT INTERFACE
st.subheader("💬 AI Product Strategy Advisor")

SYSTEM_PROMPT = f"""
You are an AI Product Strategy Advisor for CampusPath Technologies.
The workspace is currently executing Stage {st.session_state.stage} of 4:
- Stage 1: Company Profile & Vision Alignment
- Stage 2: Problem Definition & Higher-Ed Enrollment Bottlenecks
- Stage 3: User Journey Mapping & Workflow Architecture
- Stage 4: Product Requirements Document (PRD) & MVP Specs

Guide the user through Stage {st.session_state.stage}. Ask targeted questions, suggest framework improvements, and generate clear structured markdown outputs.
"""

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Enter prompt for Stage {st.session_state.stage}..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=api_messages
        )
        
        reply = response.content[0].text
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
