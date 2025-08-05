import streamlit as st
from streamlit_chat import message
import google.generativeai as genai
import datetime

with open("keys/.gemini_key", "r") as f:
    genai.configure(api_key=f.read().strip())

model = genai.GenerativeModel("gemini-1.5-flash")
visual_model = genai.GenerativeModel("gemini-1.5-flash")

def run_model(prompt: str) :
    print("#########################################################################")
    print(f"{datetime.datetime.now()} ----- Agent is running the prompt {prompt}")
    return model.generate_content(prompt)

cvf = f""" 
The Client Value Framework is how we sell, shape and talk about our deals. 
It provides an outline for Oral Presentations and written Executive Summaries. 
It requires a client-first focus. 
We must understand and validate our understanding of their current/future plans, their challenges, and their expectations from a partner. 
The first 5 steps for Client Value Framework focusses on -
1. Client Mission: The client’s market-facing message, branding
2. Defined business outcomes and goals: Current state of business, operations and IT environments
4. What prevents future state from happening
5. Key Capabilities Required to Succeed:
6. Corporate Profile(s) & Credentials (including Partners): Our Corporate summary and 3rd Party testimonials to our efficacy (analysis, other clients, etc.) 
7. Key Capability References (Repeat once for each Key Capability in Step 5): 
• State our past performance (similar size and scope) 
• Explain the business / technical challenge that the reference client experienced 
• Explain the Solution Approached that was used 
• Describe the client's business results / outcomes (with metrics) 
• Detail how our prospective client will benefit from our experience, e.g. same delivery center, software, process, artifact, and/or best of all People - must be validated with the client.
8. Delivery Leadership Team (DLT): 
• The goal is that 60% of the DLT comes from the client references in Step 7
9. Our Solution Approach (designed by DLT): 
• Explain the Solution Approach (concept of design, build, operate) 
• Low Risk Transition and/or Transformation Plan 
• Low Risk Operations Plan 
• Top 5 Client-Validated Risks and how we mitigate those risks 
• How we will continue to drive innovation over the Contract life 
• Our proven multi-supplier Governance Model
10. Compelling Client Business Case: 
• Explain the Explain how our solution provides the value the client desired
11. Our Corporate and Individual Commitments to the Client's Success: 
• Not just a corporate commitment, a personal commitment on the part of the DLT to the project's success.
Please align your storyline with our Client Value Framework. Please tabutate the response for each slides."""

# Session state setup
if "storyline" not in st.session_state:
    st.session_state.storyline = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "editing" not in st.session_state:
    st.session_state.editing = False


st.set_page_config(page_title="🤖 Agentic SDLC Assistant", layout="wide")
st.title("📽️ RFP Storyline Chatbot")

itr = 0
# Step 1: Initial RFP prompt
if st.session_state.storyline == "":
    rfp_input = st.text_area("Paste the RFP prompt from the customer:")
    if st.button("Generate Initial Storyline") and rfp_input:
        prompt = f"""
        Act as a strategist preparing an RFP response. Keep in mind the {cvf}
        Create a slide-by-slide storyline based on: "{rfp_input}"
        Return clear slide titles with slide content in details in a tabular format. """
        with st.spinner(f"Agent is preparing initial story line"):
            response = run_model(prompt=prompt)
            st.session_state.storyline = response.text
            # Save chat
            st.session_state.chat_history.append({"user": rfp_input, "ai": st.session_state.storyline})
            st.session_state.editing = True

# Step 2: Chat interface for feedback
if st.session_state.storyline and st.session_state.editing:
    st.write("💬 Provide feedback or request revisions:")
    itr = itr + 1
    user_feedback = st.chat_input("Suggest edits or ask to expand a slide...", key = itr)
    if user_feedback:
        # Construct new prompt including previous storyline and latest feedback
        chat_prompt = f"""Given the current RFP storyline:{st.session_state.storyline}
        Modify or expand based on this user feedback: "{user_feedback}"
        Return the updated storyline in full. Please tabutate the response for each slides."""
        with st.spinner(f"Agent is updating story line"):
            response = model.generate_content(chat_prompt)
            updated_storyline = response.text
            st.session_state.editing = True
            # Save chat
            st.session_state.chat_history.append({"user": user_feedback, "ai": updated_storyline})

        # Show conversation
        #for entry in st.session_state.chat_history[::-1]:
        #    message(entry["user"], is_user=True)
        #    message(entry["ai"])

        # Update storyline for further tweaks
        st.session_state.storyline = updated_storyline

    # Display full chat history
    for entry in (st.session_state.chat_history):
        message(entry["user"], is_user=True)
        message(entry["ai"])

    if st.button("✅ Finish Editing"):
        st.session_state.editing = False
        st.success("Editing completed. You can now export or reuse the storyline!")

# Optional: Display final storyline
if not st.session_state.editing:
    st.write("📘 Final Storyline:")
    st.write(st.session_state.storyline)