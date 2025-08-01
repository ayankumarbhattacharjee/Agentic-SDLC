import streamlit as st
from orchestrator import *
from export_utils import *

st.set_page_config(page_title="🤖 Agentic SDLC Assistant", layout="wide")
st.markdown("<h1 style='margin-top: 10px;'>🤖 Agentic SDLC Assistant </h1>", unsafe_allow_html=True)
#st.markdown("""<table border="none"><tr><td><img src="https://www.cognizant.com/us/media_1808da395be9f77c0124de824530b0338915414a8.svg?width=2000&format=webply&optimize=medium" width="100"></td><td><h1 style='margin: 0;'>🤖 Agentic SDLC Companion</h1></td></tr></table>""", unsafe_allow_html=True)

st.markdown("""
<style>
.header-bar {position: fixed; top: 0; width: 100%; z-index: 999; padding: 0.6rem 1rem;
    display: flex; align-items: center; justify-content: flex-start; font-family: 'Segoe UI', sans-serif; border-bottom: 2px solid #004080;}
.header-logo { height: 32px;  margin-right: 12px;}
body, html { padding-top: 70px;  /* Ensures content doesn’t hide behind the fixed header */
    background: linear-gradient(to right, #fdfbfb, #ebedee);}
.footer {position: fixed; bottom: 0; width: 100%; text-align: center; padding: 0.75rem; margin-top: 2rem;
    font-size: 0.9rem; color: #666; border-top: 1px solid #ccc; background-color: #f8f9fa;
    left: 0; right: 0;  height: 50px; border-top: 1px solid #ccc; text-align: center;}
.footer a {color: #0077cc; text-decoration: none;}
.footer a:hover {text-decoration: underline;}       
.element-container:has(#mkr) + div button {background-color: #181970; color: white; border-radius: 6px; font-weight: bold; transition: 0.3s;}
.element-container:has(#mkr) + div button:hover { background-color: #04211b; transform: scale(1.15);}
.element-container:has(#pkr) + div button {background-color: #187019; color: white; border-radius: 6px; font-weight: bold; transition: 0.3s;}
.element-container:has(#pkr) + div button:hover { background-color: #04211b; transform: scale(1.15);}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<style>
.agent-status { padding: 6px 12px; margin-bottom: 6px; border-radius: 8px; animation: pulse 2s infinite; }
.agent-current {background-color: #e0f7fa;}
.agent-complete {background-color: #e8f5e9;}
.agent-pending {background-color: none;}
@keyframes pulse {  0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; }}
</style>
""", unsafe_allow_html=True)


with st.expander("### 🧠 Overview", expanded=False):
    st.markdown("""
        This Cognizant homegrown intelligent assistant guides you through a multi-stage AI workflow for transforming raw requirements into production-ready solutions.  
        Each agent contributes to a specific phase — from specification analysis to deployment strategy — with editable outputs that can be consumed by team members.
        
        Use the buttons below to run each agent in sequence:
        
        - 📋 **Analyst Agent**: Converts raw ideas into structured specs  
        - 🧱 **Design Agent**: Generates architectural plans and diagrams 
        - 🧮 **Estimator Agent**: Identifies the total effort required for the work  
        - 💻 **Backend Agent**: Produces executable code based on the design  
        - 👓 **Review Agent**: Provides feedback and identifies improvements  
        - 🧪 **Test Agent**: Creates test cases and validation logic  
        - 🚀 **Deploy Agent**: Suggests deployment strategies and environments
        """
    )

AGENTS = ["Analyst", "Designer", "Estimator", "Coder", "Reviewer", "Tester", "Deployer"]
AGENT_EMOJIS = {"Analyst": "📋", "Designer": "🧱", "Estimator": "🧮",
    "Coder": "💻", "Reviewer": "👓", "Tester": "🧪", "Deployer": "🚀"}

if "workflow_index" not in st.session_state:
    st.session_state["workflow_index"] = 0
current_index = st.session_state["workflow_index"]

# ▶️ Run current agent logic
active_agent = AGENTS[current_index]

#st.sidebar.image("https://www.cognizant.com/us/media_1808da395be9f77c0124de824530b0338915414a8.svg?width=2000&format=webply&optimize=medium", width=200)  # adjust width as needed
#st.sidebar.markdown(f"---")
st.sidebar.markdown("## 🔄 Workflow Progress")

for i, agent in enumerate(AGENTS):
    current = (i == current_index)
    output_key = f"{agent}_output"
    question_key = f"{agent}_questions"
    responses_key = f"{agent}_responses"

    # Determine status
    if output_key in st.session_state and st.session_state[output_key]:
        status_text = "✅ Completed"
        status_class = "agent-complete"
    elif question_key in st.session_state and len(st.session_state.get(responses_key, {})) < len(st.session_state[question_key]):
        status_text = "🧠 Asking Questions"
        status_class = "agent-status"
    elif question_key in st.session_state:
        status_text = "📚 Awaiting Feedback"
        status_class = "agent-status"
    else:
        status_text = "⏳ Awaiting Spec"
        status_class = "agent-pending"

    current_class = "agent-current" if current else ""
    agent_label = f"{AGENT_EMOJIS.get(agent, '')} {agent.title()}"

    st.sidebar.markdown(
        f"<div class='agent-status {status_class} {current_class}'><strong>{agent_label}</strong><br /><sub>-- {status_text}</sub></div>",
        unsafe_allow_html=True
    )
#st.sidebar.markdown(f"---")
#st.sidebar.markdown(f"Agent in action: {AGENT_EMOJIS[active_agent]} {active_agent}")


def run_agent(agent_name: str, context_inputs=None):
    """
    Runs the interactive UI workflow for a single agent in the SDLC pipeline.

    Parameters:
    -----------
    agent_name : str
        The name of the agent (e.g. 'designer', 'analyst').
    context_inputs : dict, optional
        A dictionary of upstream agent outputs passed into this agent's context.

    Workflow Stages:
    ----------------
    1. Accepts user spec input if not yet provided.
    2. Asks agent-specific clarification questions one at a time.
    3. Collects user responses and stores them in session state.
    4. Displays prompt suggestion multiselect once all questions are answered.
    5. Synthesizes final output via `generate_agent_output()` using:
        - Spec
        - User feedback
        - Q&A response dict
        - Upstream context
    6. Renders full conversational history with styled left/right alignment.
    7. Provides export button to download entire chat and output as HTML.

    Session State Keys Used:
    ------------------------
    - f"{agent}_spec" → Initial spec provided by user
    - f"{agent}_questions" → List of clarification questions
    - f"{agent}_responses" → Dict of Q&A responses
    - f"{agent}_user_feedback" → Prompt suggestions
    - f"{agent}_output" → Final generated agent output
    - f"{agent}_history" → All chat messages (agent + user)
    - f"{agent}_question_index" → Tracks which question is being asked
    """
    key = agent_name
    history_key = f"{key}_history"
    index_key = f"{key}_question_index"
    qa_done = f"{key}_qa_done"

    # Initialize state
    for state_key in [f"{key}_spec", f"{key}_questions", f"{key}_responses",
                      f"{key}_output", f"{key}_user_feedback"]:
        if state_key not in st.session_state:
            st.session_state[state_key] = "" if "_responses" not in state_key else {}

    if qa_done not in st.session_state:
        st.session_state[qa_done] = False

    if history_key not in st.session_state:
        st.session_state[history_key] = []

    if index_key not in st.session_state:
        st.session_state[index_key] = 0

    # 🧠 Render full chat history so far
    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(render_messag(msg["content"], msg["role"], key), unsafe_allow_html=True)
    
    #st.markdown(f"### You are now interacting with {AGENT_EMOJIS[key]} {key} agent")
    st.markdown(f"""<div class="header-bar"><h5>You are now interacting with {AGENT_EMOJIS[key]} {key} agent</h5></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="footer"><h6>AGENT in action: {AGENT_EMOJIS[key]} {key}</h6></div>""", unsafe_allow_html=True)
    
    # 🌱 Get spec input
    if not st.session_state[f"{key}_spec"]:
        if current_index == 0 :
            spec = st.text_area("Enter goal or spec", key=f"{key}_spec_input")
            if spec.strip():
                st.markdown('<span id="pkr"></span>', unsafe_allow_html=True)
                if st.button("➡️ Continue", key="{key}_continue"):
                    with st.spinner(f"{AGENT_EMOJIS[key]} {key} Agent is thinking of clarification questions ..."):
                        st.session_state[f"{key}_spec"] = spec
                        st.session_state[history_key].append({"role": "user", "content": spec})
                        
                        next_msg = reason_with_agent(agent_name, st.session_state, **context_inputs)
                        st.session_state[history_key].append({"role": "ai", "content": next_msg})
                        st.rerun()
            return
        else: 
            spec = f"Generate {key} agent output based on the following questionnaire"
            if spec.strip():
                with st.spinner(f"{AGENT_EMOJIS[key]} {key} Agent is thinking of clarification questions ..."):
                    st.session_state[f"{key}_spec"] = spec
                    #st.session_state[history_key].append({"role": "user", "content": spec})

                    next_msg = reason_with_agent(agent_name, st.session_state, **context_inputs)
                    st.session_state[history_key].append({"role": "ai", "content": next_msg})
                    st.rerun()
            return

    # 🌿 One-by-one question flow
    #index = st.session_state[index_key]
    #questions = st.session_state[f"{key}_questions"]
    #responses = st.session_state[f"{key}_responses"]
    
    #if index < len(questions):
    #    q = questions[index]
    #    
    #    # 🧠 Show the agent's question visibly
    #    with st.chat_message("ai"):
    #        st.markdown(render_messag(q, "ai", key), unsafe_allow_html=True)
    #    # Don't store this in history until user responds
    #    a = st.chat_input(f"Your response")
    #    if a:
    #        responses[q] = a
    #        st.chat_message("user").markdown(render_messag(a, "user", ""), unsafe_allow_html=True)
    #        st.session_state[history_key].append({"role": "ai", "content": q})
    #        st.session_state[history_key].append({"role": "user", "content": a})
    #        st.session_state[index_key] += 1
    #        st.rerun()
    #    return

    
    # Agent decides next step
    last_agent_msg = next((msg for msg in reversed(st.session_state[history_key]) if msg["role"] == "ai"), None)
    if (last_agent_msg["content"] if last_agent_msg else "").strip().startswith("I AM SATISFIED"):
        st.session_state[qa_done] = True

    if not st.session_state[qa_done]:
    # Show input for user reply
        ans = st.chat_input("Your response")
        if ans:
            st.session_state[history_key].append({"role": "user", "content": ans})
            next_msg = reason_with_agent(agent_name, st.session_state, **context_inputs)
            st.session_state[history_key].append({"role": "ai", "content": next_msg})
            st.rerun()

    if st.session_state[qa_done]:
        # 🌺 Prompt suggestions after Q&A
        if not st.session_state[f"{key}_user_feedback"]:
            st.markdown(f"#### 💬 {key} Feedback")
            feedback_mode = st.radio("Choose input method:", ["Write your own", "Select from prompt library"], 
                                    key=f"{key}_feedback_mode")
            if feedback_mode == "Write your own":
                feedback = st.text_area("✏️ Your feedback", key=f"{key}_feedback_text", height=68)
            else:
                selected_prompts = st.multiselect("📚 Choose one or more predefined prompt(s)",
                    AGENT_FEEDBACK_LIBRARY.get(f"{key}", []),
                    key=f"{key}_feedback_select"
                )
                feedback = "\n".join(selected_prompts).strip()
            
            if feedback.strip():
                st.markdown('<span id="pkr"></span>', unsafe_allow_html=True)
                if st.button("➡️ Continue", key="{key}_feedback_continue"):
                    st.session_state[f"{key}_user_feedback"] = feedback
                    st.session_state[history_key].append({"role": "user", "content": f"User feedback:\n{feedback}"})
                    st.rerun()
                return
            

        # 🌻 Generate final output
        st.markdown('<span id="mkr"></span>', unsafe_allow_html=True)
        if not st.session_state[f"{key}_output"] and st.button(f"🚀 Generate {agent_name.title()} Output"):
            with st.spinner(f"{AGENT_EMOJIS[key]} {key} Agent is running ..."):
                output = generate_agent_output(agent_name, st.session_state, **context_inputs)["text"]
                st.session_state[f"{key}_output"] = output
                export_agent_output(f"{key}", output)
                st.session_state[history_key].append({"role": "ai", "content": output})

        # 🌟 Display output + export
        if st.session_state[f"{key}_output"]:
            with st.expander("View agent Output", expanded=False):
                #st.markdown(render_message(st.session_state[f"{key}_output"], "agent"), unsafe_allow_html=True)
                with open(f"exports/{key}_agent_out.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                # Prefer st.html if available, else fallback
                st.html(html_content)
                st.download_button(label="📥 Download", data=html_content, 
                            file_name=f"{key}_agent_out.html", mime="text/html", 
                            key=f"download_{key}")
            
            # Create diagram
            #with st.spinner("🧠 Generating diagram..."):
            #    try:
            #        st.image(create_diagram(key,st.session_state), caption="🧩 Agent System Diagram", use_column_width=True)
            #    except:
            #        st.error("Could not create diagram")

# Context passing logic
def get_context(agent):
    ctx = {}
    if agent == "Designer":
        ctx["Analyst_output"] = st.session_state["Analyst_output"]
    elif agent == "Estimator":
        ctx["Designer_output"] = st.session_state["Designer_output"]
        ctx["Analyst_output"] = st.session_state["Analyst_output"]
    elif agent == "Coder":
        ctx["Designer_output"] = st.session_state["Designer_output"]
        ctx["Analyst_output"] = st.session_state["Analyst_output"]
    elif agent == "Reviewer":
        ctx["Coder_output"] = st.session_state["Coder_output"]
    elif agent == "Tester":
        ctx["Designer_output"] = st.session_state["Designer_output"]
        ctx["Analyst_output"] = st.session_state["Analyst_output"]
    elif agent == "Deployer":
        for upstream in AGENTS[:-1]:
            ctx[f"{upstream}_output"] = st.session_state[f"{upstream}_output"]
    return ctx




# #####################
# START OF EXECUTION for agents
# #####################
# 📘 Show all completed agents' conversation history as expanders
for i in range(current_index):
    agent = AGENTS[i]
    history = st.session_state.get(f"{agent}_history", [])
    with st.expander(f"🕘 Conversation with `{agent.title()}` Agent (Completed)", expanded=False):
        for msg in history:
            with st.chat_message(msg["role"]):
                st.markdown(render_messag(msg["content"], msg["role"], agent), unsafe_allow_html=True)

# 🧠 Run current agent
context_inputs = get_context(active_agent)
#st.header(f"🔵 Active Agent: `{active_agent.title()}`")
run_agent(active_agent, context_inputs)

# 🔜 Button to proceed to next agent
if st.session_state.get(f"{active_agent}_output") and current_index < len(AGENTS) - 1:
    st.markdown('<span id="pkr"></span>', unsafe_allow_html=True)
    if st.button("➡️ Proceed to Next Agent"):
        st.session_state["workflow_index"] += 1
        st.rerun()

if all(st.session_state.get(f"{agent}_output") for agent in AGENTS):
    full_html = export_all_agents_html(AGENTS, st.session_state)
    st.download_button(
        label="📥 Download Full Agent Studio Report",
        data=full_html,
        file_name="multi_agent_studio.html",
        mime="text/html"
    )
# #####################
# END OF EXECUTION
# #####################