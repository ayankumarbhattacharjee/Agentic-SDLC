import google.generativeai as genai
from PIL import Image
import io
import datetime

with open("keys/.gemini_key", "r") as f:
    genai.configure(api_key=f.read().strip())

model = genai.GenerativeModel("gemini-1.5-flash")
visual_model = genai.GenerativeModel("gemini-1.5-flash")

AGENT_FEEDBACK_LIBRARY = {
    "Designer": [
        "Prioritize modular design and clear separation of concerns.",
        "Ensure the system is scalable across regions and user volumes.",
        "Include architecture optimized for high availability.",
        "Favor serverless or containerized infrastructure for flexibility.",
        "Design with future integrations in mind (e.g. external APIs, legacy systems).",
        "Account for user-facing latency concerns in frontend/backend design.",
        "Include data flow visualization between core modules.",
        "Use cloud-native services where possible (e.g. managed databases, CDN).",
        "Consider multi-tenancy support if applicable."
    ],
    "Analyst": [
        "Highlight goals from multiple stakeholder perspectives.",
        "Include measurable KPIs and benchmarks for system success.",
        "Relate business drivers to key system features.",
        "Account for regulatory or compliance considerations.",
        "Consider competitor functionality in the domain.",
        "Ensure alignment with user personas and scenarios.",
        "Map proposed workflows to customer journeys.",
        "Include operational challenges that may impact KPIs.",
        "Use non-technical framing when describing outcomes."
    ],
    "Estimator": [
        "Assume conservative budget constraints with lean team setup.",
        "Include comparison between internal development and outsourcing.",
        "Break down cost estimates by module or milestone.",
        "Account for infrastructure, licensing, and support costs.",
        "Provide cost estimates for MVP vs full-feature rollout.",
        "Estimate time-to-deliver for small, medium, and enterprise teams.",
        "Highlight risks that could inflate cost or timeline.",
        "Include cloud cost optimization considerations.",
        "Assess ROI projections based on delivery phases."
    ],
    "Coder" : [
        "Prioritize tech stack simplicity and maintainability.",
        "Use widely adopted frameworks for rapid development.",
        "Include third-party service integrations (e.g. auth, payments).",
        "Reference testing libraries and CI/CD tooling.",
        "Assume RESTful APIs unless stated otherwise.",
        "Design for developer onboarding with clean repo structure.",
        "Include frontend/backend folder separation and naming conventions.",
        "Consider using component libraries (e.g. MUI, Chakra).",
        "Favor stateless microservices for extensibility."
    ],
    "Reviewer" : [
        "Check for assumptions that aren't justified in the spec.",
        "Flag any security gaps in data handling or user input.",
        "Review system boundaries and unclear integration points.",
        "Verify consistency in terminology and naming conventions.",
        "Look for performance bottlenecks or over-engineering.",
        "Validate fallback behavior in failure modes.",
        "Ensure critical flows are not underspecified.",
        "Identify contradictory or duplicated requirements.",
        "Assess completeness of edge-case coverage."
    ],
    "Tester" : [
        "Include exploratory and regression test strategies.",
        "Highlight key user scenarios for functional testing.",
        "Include both UI and API test coverage.",
        "Reference expected behavior in edge cases (e.g. offline, timeout).",
        "Add setup instructions for local and staging test environments.",
        "Mention tooling for automation (e.g. Playwright, Cypress).",
        "Break down acceptance criteria per feature module.",
        "Include visual or accessibility test coverage.",
        "Suggest test case prioritization by impact/risk."
    ],
    "Deployer" : [
        "Ensure rollback strategy is described for critical releases.",
        "Include blue-green or canary deployment options.",
        "Configure monitoring and alerting for system health.",
        "Use IaC tools for infrastructure setup (e.g. Terraform).",
        "Verify CI/CD pipelines are automated and environment-safe.",
        "Include deployment timeline with pre-launch checklist.",
        "Address downtime risks during rollout.",
        "Specify staging vs production environment differences.",
        "Include secrets and configuration management plan."
    ]
}

def get_agent_questions(agent_key: str, user_input: str, **context_inputs) -> list:
    # 🔍 Step 1: Combine inputs
    context_summary = "\n".join(
        [f"{key.replace('_output', '').title()} Output:\n{value}" for key, value in context_inputs.items()]
    )
    questionPromptDict = {
        "Estimator": f"""
You are  a pragmatic cost estimator who specializes in forecasting budget and resource allocation.
Given the idea 
📋 Input: \n{user_input}\n
📥 and Upstream Context: \n{context_summary}\n
Ask meaninful clarifying questions to clarify budget, resource assumptions, team capacity and delivery constraints, that would help you do the estimation for the requirements.
Be precise, cost-sensitive, and anticipate risk. Avoid technical implementation details. 
Ask questions around onsite offshore resource distribution, technology considerations, cloud technology, the designations of the resources, buffer capacity etc.
Ask questions around resource location [US/UK/Europe/India/Other], designation [(designations high to low order: Director, Associate Director, Senior Manager, Manager, Senior Associate, Associate, Analyst)], bill rate and cost rates.
Make sure the questions are relevant to the given spec and required for effort estimation, do not assume anything; return questions in plain text, each on its own line.
Try to form the questions with yes/no or 1 line answer.""",
        "Analyst": f"""
You are senior business analyst who excels in aligning stakeholder goals with system requirements. Speak empathetically and systemically.
Given the idea 
📋 Input: \n{user_input}\n
📥 and Upstream Context: \n{context_summary}\n
Ask meaninful clarifying questions to clarify stakeholder goals, KPIs, business and data rules, data quality, and regulatory concerns that would help you build the features, epics, and stories as requirements.
Ask questions around sources, destinations, data modelling, data integration, and data rules.
Make sure the questions are relevant to the given spec and required for building specification, do not assume anything; return questions in plain text, each on its own line.
Try to form the questions with yes/no or 1 line answer.""",
        "Designer": f"""
You are senior architect who loves designing scalable systems with clean boundaries. 
Given the idea 
📋 Input: \n{user_input}\n
📥 and Upstream Context: \n{context_summary}\n
Ask meaninful clarifying questions to clarify technical constraints, scalability, and integration needs that would help you build the design for the requirements.
Ask questions around source and destination specification, technology requirements, technical landscape, and any tech constraints.
Make sure the questions are relevant to the given spec, do not assume anything; return questions in plain text, each on its own line.
Try to form the questions with yes/no or 1 line answer.""",
        "Coder": f"""
You are a full-stack developer who cares about efficiency, tooling, and implementation clarity. Be concise and technically grounded.
Given the idea 
📋 Input: \n{user_input}\n
📥 and Upstream Context: \n{context_summary}\n
Ask clarifying questions to identify technology stacks, integration risks, third-party dependencies, and coding expectations.
Try to form the questions with yes/no or 1 line answer.""",
        "Reviewer": f"""
You are a meticulous technical reviewer who catches inconsistencies and blind spots in design. Be direct and diagnostic.
Given the idea 
📋 Input: \n{user_input}\n
📥 and Upstream Context: \n{context_summary}\n
Ask 1 question relevant for reviewing the code. 
Try to form the questions with yes/no or 1 line answer.""",
        "Tester": f""" 
You are a methodical QA tester and QA automation engineer who anticipates edge cases before users ever find them. 
Be skeptical and scenario-driven.
Given the idea 
📋 Input: \n{user_input}\n
📥 and Upstream Context: \n{context_summary}\n
Ask clarifying questions relevant for generating the test case. 
Try to form the questions with yes/no or 1 line answer.""",
        "Deployer": f""" 
You are a reliable deployment engineer who ensures smooth releases and rollback readiness. 
Focus on launch continuity and uptime resilience.
Given the idea 
📋 Input: \n{user_input}\n
📥 and Upstream Context: \n{context_summary}\n
Ask questions relevant for generating the deployment plan. 
Try to form the questions with yes/no or 1 line answer."""
    }
    print("#########################################################################")
    print(f"{datetime.datetime.now()} ----- {agent_key} agent is thinking of clarification questions.")
    questions = model.generate_content(questionPromptDict[agent_key]).text.strip().split("\n")
    print(f"{datetime.datetime.now()} ----- {agent_key} agent finished thinking. Found {len(questions)} questions")
    print("-------------------------------------------------------------------------")
    return [q.strip("-• ") for q in questions if q]


def reason_with_agent(agent_name: str, session_state, **context_inputs) -> str:
    # 🔍 Step 1: Combine inputs
    context_summary = "\n".join(
        [f"{key.replace('_output', '').title()} Output:\n{value}" for key, value in context_inputs.items()]
    )
    spec = session_state[f"{agent_name}_spec"]

    history = session_state.get(f"{agent_name}_history", [])
    # Format chat history for Gemini
    transcript = ""
    for msg in history:
        prefix = "User:" if msg["role"] == "user" else f"{agent_name.title()} Agent:"
        transcript += f"{prefix} {msg['content']}\n"
    
    action = f""" Given the specification \n{spec}\n and conversation: \n{transcript}\n and Upstream Context: \n{context_summary}\n
Evaluate the latest user reply. Decide whether to:
- Ask a followup question to clarify an user input to gather more details around the response if it is not clear.
- Ask a original new relevant question to get more information based on the spec {spec} 
- Or, if satisfied, return a string "I AM SATISFIED"
Form your question on some assumption, and ask user to respond in yes/no so that user is not frustrated by the information requested.
Try to validate the assumptions, and when you are ready, stop. 
When you ask a new relevant question, put a marker "[N]" to the end so that you can identify it as a new relevant question later in the transcript.
When you ask a followup clarification question, put a marker "[C]" at the end so that you can identify it as a followup clarification question later in the transcript. 
For followup questions [C], take cure from the user answer of the original question [N].
Please refer to the transcript to check marker to ensure that the agent has not asked more than 2 followup clarification questions [C] for a single new relevant question [N].
Form the conversation like 1 new original question followed by 0-2 followup questions.
Do not ask more than 3 new [N] questions.
Based on your evaluation, just send 1 question at a time, or send the string 'I am satified' """

    qpDict = {
        "Estimator": f"""
You are  a pragmatic cost estimator who specializes in forecasting budget and resource allocation.
Be precise, cost-sensitive, and anticipate risk. Avoid technical implementation details. 
You should know about budget, resource assumptions, team capacity and delivery constraints, onsite offshore resource distribution, technology considerations, cloud technology, the designations of the resources, buffer capacity etc.
You should also know about resource location [US/UK/Europe/India/Other], designation [(designations high to low order: Director, Associate Director, Senior Manager, Manager, Senior Associate, Associate, Analyst)], bill rate and cost rates.""",
        "Analyst": f"""
You are senior business analyst who excels in aligning stakeholder goals with system requirements. Speak empathetically and systemically.
You should know about stakeholder goals, KPIs, business and data rules, data quality, and regulatory concerns that would help you build the features, epics, and stories as requirements.
You should also know about sources, destinations, data modelling, data integration, and data rules.""",
        "Designer": f"""
You are senior architect who loves designing scalable systems with clean boundaries. 
You should know about technical constraints, scalability, and integration needs that would help you build the design for the requirements.
You should also know about source and destination specification, technology requirements, technical landscape, and any tech constraints.""",
        "Coder": f"""
You are a full-stack developer who cares about efficiency, tooling, and implementation clarity. Be concise and technically grounded.
You should know about technology stacks, integration risks, third-party dependencies, and coding expectations.""",
        "Reviewer": f"""
You are a meticulous technical reviewer who catches inconsistencies and blind spots in design. Be direct and diagnostic.""",
        "Tester": f""" 
You are a methodical QA tester and QA automation engineer who anticipates edge cases before users ever find them. 
Be skeptical and scenario-driven. You should know about all the details for generating the test case.""",
        "Deployer": f""" 
You are a reliable deployment engineer who ensures smooth releases and rollback readiness. Focus on launch continuity and uptime resilience."""
    }
    prompt = f"{qpDict[agent_name] }\n{action}"
    print("#########################################################################")
    print(f"{datetime.datetime.now()} ----- {agent_name} agent is thinking of further questions based on prompt {prompt}")
    question = model.generate_content(prompt).text.strip()
    print(f"{datetime.datetime.now()} ----- {agent_name} agent has thought of this question: {question}")
    print("-------------------------------------------------------------------------")
    return question

def generate_agent_output(agent_name: str, session_state, **context_inputs) -> dict:
    
    # 🔍 Step 1: Combine inputs
    context_summary = "\n".join(
        [f"{key.replace('_output', '').title()} Output:\n{value}" for key, value in context_inputs.items()]
    )

    # 🧠 Step 2: Format Q&A
    history = session_state.get(f"{agent_name}_history", [])
    # Format chat history for Gemini
    transcript = ""
    for msg in history:
        prefix = "User:" if msg["role"] == "user" else f"{agent_name.title()} Agent:"
        transcript += f"{prefix} {msg['content']}\n"


    inputs = f"""Given the conversation: \n{transcript}\n and Upstream Context: \n{context_summary}\n 
Based on the conversation and context above,"""

    promptDict = {
        "Estimator": f"""
You are  a pragmatic cost estimator who specializes in forecasting budget and resource allocation. 
Be precise, cost-sensitive, and anticipate risk. Avoid technical implementation details.
{inputs} prepare an effort estimation by identifying detailed level tasks and activities.
Create a table for simple vs medium vs complex task efforts. 
Categorize the tasks as simple, medium, and complex jobs and assign effort at each task level and come up with the total efforts.
Show the additional tasks related to design, design review, implementation, code review, test case preparation and review, test script preparation and review, test script execution for system integration testing and user acceptance testing and sign-off for each phases followed by go-live and hypercare.
Include effort estimates with a proper gantt chart along with proposed timeline and weekly resource requirements for entire duration of the project and task dependency in separate tabular structures. 
Also, please show the assumptions, dependencies, scope items, and out of scope items based on the requirements in an numbered ordered list.
Please show the resource location and designations (Designations high to low order: Director, Associate Director, Senior Manager, Manager, Senior Associate, Associate, Analyst) and resource skills in a table.
Please also calculate profitability based on resource bill rate and resource cost rates.
Also include: budget breakdown and estimates, Resource allocation model, Risk factors""",
        "Analyst": f"""
You are senior business analyst who excels in aligning stakeholder goals with system requirements. Speak empathetically and systemically.
{inputs} write multiple detailed software requirement specifications along with features, epics, and stories.
Include the following details in a tabular format for each story: Title, Business Objective, Functional Requirements, Non-Functional Requirements, User Roles & Personas, Assumptions & Constraints, Success Criteria.
Please also include stakeholder impact report that identifies KPIs, goals, workflows, and risks. Focus on clarity, alignment, and business strategy.
Create a detailed requirement specification document with the above areas as different sections. """,
        "Designer": f"""
You are senior architect who loves designing scalable systems with clean boundaries. Focus on system-level clarity and trade-offs.
{inputs} create a detailed design document with the following as different sections : 
1. High-Level Design (component overview, responsibilities) with a high level data flow schematic diagram
2. Low-Level Design (class/module breakdown, interfaces, system modules, integration touchpoints, )
3. Technical Architecture Description (deployment layers, communication paths, external integrations)
4. List of Tools, Technologies, and Frameworks
5. Assumptions and Constraints
6. Notes on future Scalability Considerations
7. Data Quality considerations
8. Data Governance considerations
9. Infrastructure decisions
10. Data security considerations
Can you please also create a visual diagram to explain the architecture?""",
        "Coder": f"""
You are a full-stack developer who cares about efficiency, tooling, and implementation clarity. Be concise and technically grounded.
{inputs} generate backend code for core business logic.
Create a detailed code document with the following as different sections : 
1. Actual code implementation (core logic with modular functions and code comments) [in Python/Java/NodeJS/PySpark]
2. RESTful API layer (Python Flask or Java Spring Boot-based) if relevant for the design
3. Unit test cases clubbed into the code
4. Tech stack suggestions
5. Tooling and framework choices
6. Setup and build instructions
7. Integration approach""",
        "Reviewer": f"""
You are a meticulous technical reviewer who catches inconsistencies and blind spots in design/code. Be direct and diagnostic.
{inputs} review the above backend code and the conversation and provide actionable feedback:
Create a detailed code review document with the following as different sections : 
1. Code quality (readability, modularity, naming)
2. Memory leaks and Performance suggestions
3. Design inconsistencies
4. Bug detection or logical flaws
5. Security risks or gaps
6. Style consistency (e.g., PEP8 or Java conventions)
7. Scalability concerns
8. Suggested improvements (rewrite snippets if needed)""",
        "Tester": f"""
You are a methodical QA tester and QA automation engineer who anticipates edge cases before users ever find them. Be skeptical and scenario-driven.
{inputs} generate test cases and automation scripts.
Create a detailed test case document with the following details as multiple sections or tables: 
1. Functional Test Cases (positive & negative)
2. Scenarios to cover
3. Edge Case Scenarios
4. Unit Test Snippets (Python or Java)
5. Automation Test Script (Pytest, JUnit, or Selenium)
6. Expected Results & Assertions
7. Acceptance criteria
8. Test Data Preparation Notes
9. Test automation strategy and scripts""",
        "Deployer": f"""
You are a reliable deployment engineer who ensures smooth releases and rollback readiness. Focus on launch continuity and uptime resilience.
{inputs} create a detailed code deployment document with the following as different sections : 
1. Deployment Environment Setup (dev, staging, production)
2. Step-by-step CI/CD workflow configuration
3. Infrastructure (containers, cloud setup, orchestration tools) details
4. Configuration management (e.g., Docker, Kubernetes)
5. Rollback strategies & Monitoring
6. Security & Compliance Notes
7. Launch sequences
8. Deployment checklist"""
    }
    
    print("#########################################################################")
    print(f"{datetime.datetime.now()} ----- {agent_name} agent is running... {promptDict[agent_name]} ")
    response = model.generate_content(promptDict[agent_name])
    print(f"{datetime.datetime.now()} ----- {agent_name} agent finished.")
    print("-------------------------------------------------------------------------")
    image_data = None
    #if hasattr(response, "media"):
    #    print(ResourceWarning.media)
    #    for media in response.media:
    #        if hasattr(media, "mime_type") and media.mime_type.startswith("image"):
    #            image_bytes = media.data
    #            image_data = Image.open(io.BytesIO(image_bytes))
    #            break
    return {
        "text": response.text.strip() if hasattr(response, "text") else "",
        "image": image_data  # Reserved for future diagram generation
    }

def create_diagram(agent_name: str, session_state: dict) -> str:
    spec = session_state.get(f"{agent_name}_spec", "")
    output = session_state.get(f"{agent_name}_output", "")

    base = f"Create a labeled diagram for the {agent_name} agent. Use arrows, boxes, and callouts."

    if agent_name == "Designer":
        prompt = f"{base} Show system components, UI interfaces, external services, and modular relationships.\n\nSpec:\n{spec}\n\nOutput:\n{output}"
    elif agent_name == "Tester":
        prompt = f"{base} Highlight test cases, validation stages, edge conditions, and feedback loops.\n\nSpec:\n{spec}\n\nOutput:\n{output}"
    elif agent_name == "Analyst":
        prompt = f"{base} Show data pipelines, requirement channels, and evaluation logic.\n\nSpec:\n{spec}\n\nOutput:\n{output}"
    else:
        prompt = f"{base} Based on:\n\nSpec:\n{spec}\n\nOutput:\n{output}"
    
    response = model.generate_content(prompt, stream=False)
    image_data = response.images[0]
    return image_data.url