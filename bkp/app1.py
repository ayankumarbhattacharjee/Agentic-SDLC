import streamlit as st

from export_utils import *
from orchestrator import *

# 🧠 Agents available in the system
AGENTS = ["Analyst", "Estimator", "Designer", "Developer", "Reviewer", "Tester", "Deployer"]
selected_agent = st.sidebar.radio("🧠 Choose Agent", AGENTS)

# Agent-specific keys
agent_key = selected_agent
history_key = f"{agent_key}_history"
stage_key = f"{agent_key}_stage"
spec_key = f"{agent_key}_spec"
questions_key = f"{agent_key}_questions"
responses_key = f"{agent_key}_responses"
index_key = f"{agent_key}_question_index"
feedback_key = f"{agent_key}_user_feedback"

# Initialize session state
if stage_key not in st.session_state:
    st.session_state[stage_key] = "awaiting_spec"

if history_key not in st.session_state:
    st.session_state[history_key] = []

if spec_key not in st.session_state:
    st.session_state[spec_key] = ""

if questions_key not in st.session_state:
    st.session_state[questions_key] = []

if responses_key not in st.session_state:
    st.session_state[responses_key] = {}

if index_key not in st.session_state:
    st.session_state[index_key] = 0

# 🔄 Reset
if st.button("🔄 Reset Conversation"):
    for key in [stage_key, history_key, spec_key, questions_key, responses_key, index_key, feedback_key]:
        st.session_state.pop(key, None)
    st.rerun()

# 🧠 Display history
st.markdown(f"## 💬 Chat with `{selected_agent.title()}` Agent")
for entry in st.session_state[history_key]:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

# ✏️ Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state[history_key].append({"role": "user", "content": user_input})

    # 🟢 First input becomes spec
    if st.session_state[stage_key] == "awaiting_spec":
        st.session_state[spec_key] = user_input
        st.session_state[questions_key] = get_agent_questions(agent_key, user_input)
        st.session_state[stage_key] = "asking_questions"

        # Ask first question
        first_q = st.session_state[questions_key][0]
        st.chat_message("assistant").markdown(first_q)
        st.session_state[history_key].append({"role": "assistant", "content": first_q})

    # 🟡 Q&A session: ask one question at a time
    elif st.session_state[stage_key] == "asking_questions":
        current_index = st.session_state[index_key]
        current_q = st.session_state[questions_key][current_index]
        st.session_state[responses_key][current_q] = user_input

        st.session_state[index_key] += 1
        next_index = st.session_state[index_key]

        if next_index < len(st.session_state[questions_key]):
            next_q = st.session_state[questions_key][next_index]
            st.chat_message("assistant").markdown(next_q)
            st.session_state[history_key].append({"role": "assistant", "content": next_q})
        else:
            # Move to feedback stage
            st.session_state[stage_key] = "awaiting_feedback"
            st.rerun()

# 🧠 Prompt suggestions AFTER last question
if st.session_state[stage_key] == "awaiting_feedback":
    st.markdown("### 📚 Optional: Select feedback prompts for better output")
    selected_prompts = st.multiselect(
        f"Suggestions for the `{agent_key.title()}` Agent",
        AGENT_FEEDBACK_LIBRARY.get(agent_key, []),
        key=f"{agent_key}_selected_prompts"
    )

    if selected_prompts:
        st.session_state[feedback_key] = "\n".join(selected_prompts).strip()

    if st.button("🚀 Generate Output"):
        user_feedback = st.session_state.get(feedback_key, "")
        with st.spinner("Agent Thinking..."):
            response = generate_agent_output( agent_name=agent_key, spec_text=st.session_state[spec_key],
                user_feedback=user_feedback, qa=st.session_state[responses_key])

        st.chat_message("assistant").markdown(response)
        st.session_state[history_key].append({"role": "assistant", "content": response})
        st.session_state[stage_key] = "completed"