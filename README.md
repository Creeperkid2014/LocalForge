# Local AI Workspace — GitHub Ready (FOSS)

Self-hosted developer workspace combining:
- Code editor (Monaco via streamlit-ace)
- File explorer
- Terminal collaboration (websocket + xterm.js)
- AI code generation (pluggable local LLM / mock)

## Quick start (Windows / macOS / Linux)

1. Install Python 3.9+
2. Unzip this folder and open a terminal in it
3. Run:
   ```bash
   py -3 run.py    # Windows (or use `python run.py` / `python3 run.py`)
   ```
4. The backend will be at: http://127.0.0.1:8000
   The frontend will open Streamlit in your browser.

## Features
- Edit files from `workspace/` using an embedded code editor
- Open a collaborative terminal (share the session id with others on your LAN)
- Generate code suggestions via local Ollama (if installed) or the included mock engine

## Notes
- This is intended as a developer-friendly, open-source starter — customize and push to GitHub!
- For production-hardening, add auth, HTTPS, containerized sandboxes for terminals, and strict path ACLs.
-There are some bugs in the terminal, later we will upgrade this project to v.1.1
##Devs
-AgentArk5/Creeperkid2014, The co CEO of thundered studios: https://discord.gg/4fNnMamM. And The Founder of LocalForge.
