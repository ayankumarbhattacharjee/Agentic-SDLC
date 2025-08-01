import markdown
import os

custom_css = """ <style>
    #agent-output {font-family: "Segoe UI", sans-serif; color: #333; }

    #agent-output table {width: 100%; border-collapse: collapse; margin-top: 1rem;}
    #agent-output th, 
    #agent-output td {border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; border-left: none; border-right: none; padding: 10px; text-align: left;}
    #agent-output tr:nth-child(even) {background-color: #f9f9f9;}
    #agent-output tr:hover {background-color: #e6f7ff;  }
    #agent-output th {background-color: #111; color: white;}

    #agent-output h1, 
    #agent-output h2,
    #agent-output h3 { border-bottom: 2px solid #ddd; padding-bottom: 6px; margin-top: 1.5rem; color: #111; }
    #agent-output ul { padding-left: 1.5rem; margin-bottom: 1rem; list-style-type: disc;}
    #agent-output ul li { margin-bottom: 8px;  padding-left: 0.5rem; border-left: 3px;  background-color: #f7faff; border-radius: 4px; transition: background-color 0.3s ease; }
    #agent-output ul li:hover { background-color: #e6f2ff;}
    #agent-output ol {padding-left: 1.5rem; margin-bottom: 1rem; list-style-type: decimal; counter-reset: item;}
    #agent-output ol li {margin-bottom: 8px; padding-left: 0.5rem; position: relative; background-color: #fffdf7; border-left: 3px; border-radius: 4px; transition: background-color 0.3s ease;}
    #agent-output ol li:hover { background-color: #fff3e0; }
    #agent-output p { font-size: 1rem;  line-height: 1.7; margin-bottom: 1.2rem; padding: 0.5rem 0.75rem;  border-left: 4px;}
    #agent-output pre { background-color: #f4f4f4; padding: 10px; border-radius: 6px; overflow-x: auto; }
    </style> """

def to_markdown(title: str, content: str) -> str:
    """Wrap content with a title as Markdown."""
    return f"# {title} [AI agent] generated content:\n\n{content.strip()}"

def to_html(md_text: str) -> str:
    """Convert Markdown to HTML."""
    return markdown.markdown(md_text, extensions=["extra", "codehilite"])

def export_agent_output(name: str, content: str, folder: str="exports"):
    """Save content to .md and .html files."""
    os.makedirs(folder, exist_ok=True)

    base_name = name.lower().replace(" ", "_")
    md_path = os.path.join(folder, f"{base_name}_agent_out.md")
    html_path = os.path.join(folder, f"{base_name}_agent_out.html")

    md_text = to_markdown(name, content)
    html_body = to_html(md_text) 
    html_text = f"""{custom_css}\n<div id="agent-output">{html_body}</div>"""

    # Write MD file
    with open(md_path, "w", encoding="utf-8") as f_md:
        f_md.write(md_text)
    # Write HTML file
    with open(html_path, "w", encoding="utf-8") as f_html:
        f_html.write(html_text)

    return md_path, html_path

# 🧾 Collect Summary for Download
def build_summary(agents : dict):
    # Combine all Markdown sections
    full_md = "\n\n".join([to_markdown(f"{name} Agent Output", content)
                           for name, content in agents.items() if content])

    # Convert to HTML
    full_html_body = to_html(full_md)
    full_html = f"""<html>
        <head><title>Agentic SDLC Companion Report</title></head>
        <body><img src="https://www.cognizant.com/us/media_1808da395be9f77c0124de824530b0338915414a8.svg?width=2000&format=webply&optimize=medium" />
        <h1>🧠 Multi-Agent Assistant Summary</h1>{custom_css}\n<div id="agent-output">\n{full_html_body}</div></body>
        </html>"""
    return full_html

def render_messag(content: str, role: str, agent_name : str) -> str:
    align = "left" if role == "ai" else "right"
    bg = "#e6f7ff" if role == "ai" else "#fffbe6"

    # Handle blank or undefined content
    if not content or not content.strip():
        content = "<em>(No message provided)</em>"

    # Emoji per agent
    agent_emojis = {
        "Analyst": "🧠",
        "Designer": "🎨",
        "Estimator": "📊",
        "Coder": "💻",
        "Reviewer": "👓",
        "Tester": "🧪",
        "Deployer": "🚀"
    }
    emoji = agent_emojis.get(agent_name.lower(), "🤖") if role == "ai" else "🙋"

    return f"""<div style="text-align:{align}; margin: 0.75rem 0;">
        <div style="display:inline-block; background:{bg}; padding:0.75rem 1rem;
             border-radius:12px; max-width:70%; box-shadow:0 1px 3px rgba(0,0,0,0.1);
             font-family:'Segoe UI', sans-serif; font-size:0.95rem;">
             <div style="font-weight:bold; margin-bottom:6px;">{emoji} {agent_name if role == "ai" else role.title()}</div>
            {content} </div></div>"""

def export_agent_html(agent_name: str, session_state) -> str:
    history = session_state.get(f"{agent_name}_history", [])
    output = session_state.get(f"{agent_name}_output", "")
    spec = session_state.get(f"{agent_name}_spec", "")
    responses = session_state.get(f"{agent_name}_responses", {})
    feedback = session_state.get(f"{agent_name}_user_feedback", "")

    blocks = [f"<h2>{agent_name.title()} Agent</h2>",
              f"<h3>Spec:</h3><p>{spec}</p>",
              "<h3>Q&A:</h3><ul>"]

    for q, a in responses.items():
        blocks.append(f"<li><strong>{q}</strong><br>{a}</li>")
    blocks.append("</ul>")

    if feedback:
        blocks.append(f"<h3>Prompt Suggestions:</h3><p>{feedback}</p>")

    blocks.append("<h3>Final Output:</h3>")
    blocks.append(render_message(output, "agent"))

    return "\n".join(blocks)

def export_all_agents_html(agent_list: list, session_state: dict) -> str:
    html_parts = ["<html><head><style>"]
    html_parts.append("""
    body { font-family: 'Segoe UI', sans-serif; margin: 2rem; }
    .agent-block { margin-bottom: 3rem; padding-bottom: 2rem; border-bottom: 1px solid #ccc; }
    .role-user { text-align: right; background: #fff3e0; padding: 0.6rem; border-radius: 10px; margin: 0.4rem 0; }
    .role-agent { text-align: left; background: #e0f7fa; padding: 0.6rem; border-radius: 10px; margin: 0.4rem 0; }
    .agent-title { font-size: 1.4rem; font-weight: bold; margin-bottom: 1rem; color: #002B5B; }
    .final-output { padding: 1rem; margin-top: 1rem; border-radius: 12px; }
    </style>""")
    html_parts.append(f"""{custom_css}</head><body>""")

    for agent in agent_list:
        history_key = f"{agent}_history"
        output_key = f"{agent}_output"

        html_parts.append(f"<div class='agent-block'>")
        html_parts.append(f"<div class='agent-title'>Conversation with {agent.title()} Agent</div>")

        # Add chat history
        history = session_state.get(history_key, [])
        for msg in history:
            role_class = f"role-{msg['role']}"
            html_parts.append(f"<div class='{role_class}'>{msg['content']}</div>")

        # Add final output
        output = to_html(to_markdown(agent, session_state.get(output_key, "")))
        if output:
            html_parts.append(f"<div id='agent-output'><strong>Final Output:</strong><hr>{output}</div>")

        html_parts.append("</div>")

    html_parts.append("</body></html>")
    return "\n".join(html_parts)