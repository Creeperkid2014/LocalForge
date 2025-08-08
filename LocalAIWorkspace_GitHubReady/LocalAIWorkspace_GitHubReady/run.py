import subprocess, sys, os, time

ROOT = os.path.dirname(__file__)
os.chdir(ROOT)

print('[*] Installing dependencies (if missing)...')
subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

# Start backend (uvicorn) and frontend (streamlit)
print('[*] Starting backend (uvicorn) on http://127.0.0.1:8000 ...')
backend_proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.server:app', '--host', '127.0.0.1', '--port', '8000'])

# Wait a moment for backend to be ready
time.sleep(1)

print('[*] Starting frontend (streamlit)...')
frontend_proc = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'frontend/app.py'])

print('\n[✅] Local AI Workspace is running!')
print(' - Backend: http://127.0.0.1:8000')
print(' - Streamlit will open in your browser (or visit http://localhost:8501)')
print('\n[CTRL+C to stop]')

try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print('\n[*] Shutting down...')
    backend_proc.terminate()
    frontend_proc.terminate()
