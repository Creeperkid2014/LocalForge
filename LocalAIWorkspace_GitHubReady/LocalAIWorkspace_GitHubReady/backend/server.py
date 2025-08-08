import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio, subprocess, shlex, json
from pathlib import Path
from .ai_engine import generate_code

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR.parent / 'workspace'
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title='Local AI Workspace Backend')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# serve static terminal HTML and xterm assets (we use CDN for xterm)
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')

# simple in-memory mapping of websocket sessions to subprocesses / clients
TERMINAL_SESSIONS = {}  # session_id -> {'proc': Popen, 'clients': set(WebSocket)}

@app.get('/')
async def root():
    return {'status': 'Local AI Workspace backend running'}

# File APIs
@app.get('/api/files/list')
async def list_dir(path: str = ''):
    base = (WORKSPACE_DIR / path).resolve()
    if not str(base).startswith(str(WORKSPACE_DIR.resolve())):
        raise HTTPException(400, 'Invalid path')
    if not base.exists():
        return []
    items = []
    for p in base.iterdir():
        items.append({'name': p.name, 'is_dir': p.is_dir(), 'size': p.stat().st_size})
    return items

@app.get('/api/files/read')
async def read_file(path: str):
    base = (WORKSPACE_DIR / path).resolve()
    if not str(base).startswith(str(WORKSPACE_DIR.resolve())):
        raise HTTPException(400, 'Invalid path')
    if not base.exists() or not base.is_file():
        raise HTTPException(404, 'Not found')
    return {'content': base.read_text(encoding='utf-8', errors='ignore')}

@app.post('/api/files/write')
async def write_file(request: Request):
    body = await request.json()
    path = body.get('path')
    content = body.get('content', '')
    base = (WORKSPACE_DIR / path).resolve()
    if not str(base).startswith(str(WORKSPACE_DIR.resolve())):
        raise HTTPException(400, 'Invalid path')
    base.parent.mkdir(parents=True, exist_ok=True)
    base.write_text(content, encoding='utf-8')
    return {'ok': True}

# AI endpoint (pluggable local model)
@app.post('/api/ai/generate')
async def ai_generate(request: Request):
    body = await request.json()
    prompt = body.get('prompt', '')
    language = body.get('language', 'python')
    if not prompt:
        raise HTTPException(400, 'Empty prompt')
    result = generate_code(prompt, language=language)
    return JSONResponse(result)

# Websocket terminal endpoint
@app.websocket('/ws/term/{session_id}')
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = TERMINAL_SESSIONS.get(session_id)
    if session is None:
        # spawn a shell subprocess for this session
        # cross-platform: use bash on Unix, cmd on Windows
        if os.name == 'nt':
            cmd = ['cmd.exe']
        else:
            cmd = ['bash', '-l']
        proc = await asyncio.create_subprocess_exec(*cmd,
                                                    stdin=asyncio.subprocess.PIPE,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.STDOUT)
        session = {'proc': proc, 'clients': set()}
        TERMINAL_SESSIONS[session_id] = session

        # background task: read from proc stdout and broadcast to clients
        async def reader():
            try:
                while True:
                    data = await proc.stdout.readline()
                    if not data:
                        break
                    text = data.decode(errors='ignore')
                    # broadcast to clients
                    for ws in list(session['clients']):
                        try:
                            await ws.send_text(text)
                        except:
                            pass
            except Exception:
                pass
        asyncio.create_task(reader())

    session['clients'].add(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            # when a client sends data, write to subprocess stdin
            proc = session['proc']
            if proc and proc.stdin:
                try:
                    proc.stdin.write(msg.encode() + b'\n')
                    await proc.stdin.drain()
                except Exception:
                    pass
    except WebSocketDisconnect:
        session['clients'].discard(websocket)
    except Exception:
        session['clients'].discard(websocket)

# Serve the terminal HTML (simple)
@app.get('/terminal')
async def terminal_ui(session_id: str = 'demo'):
    html_path = BASE_DIR / 'static' / 'terminal.html'
    return HTMLResponse(html_path.read_text())
