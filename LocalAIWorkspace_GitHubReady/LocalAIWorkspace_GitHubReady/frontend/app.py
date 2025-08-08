import streamlit as st
import requests, os, urllib.parse
from streamlit_ace import st_ace

BACKEND = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

st.set_page_config(layout='wide', page_title='Local AI Workspace')
st.title('Local AI Workspace — GitHub Ready Demo')

# Sidebar: file explorer
st.sidebar.header('Workspace')
path = st.sidebar.text_input('Path (relative to workspace)', value='')
if st.sidebar.button('Refresh'):
    pass
try:
    res = requests.get(BACKEND + '/api/files/list', params={'path': path}, timeout=3).json()
except Exception as e:
    res = []
for item in res:
    if item['is_dir']:
        st.sidebar.write(f"📁 {item['name']}")
    else:
        if st.sidebar.button(f"Open {item['name']}", key=item['name']):
            # load file into editor
            file_path = os.path.join(path, item['name']) if path else item['name']
            r = requests.get(BACKEND + '/api/files/read', params={'path': file_path})
            st.session_state['current_file'] = file_path
            st.session_state['current_content'] = r.json().get('content', '')

# Editor pane
st.subheader('Code Editor')
current_file = st.session_state.get('current_file', 'untitled.py')
content = st.session_state.get('current_content', '# start coding...\n')
code = st_ace(value=content, language='python', theme='monokai', key='ace', height=400)

col1, col2 = st.columns([1,1])
with col1:
    if st.button('Save'):
        fp = st.session_state.get('current_file', 'untitled.py')
        payload = {'path': fp, 'content': code}
        requests.post(BACKEND + '/api/files/write', json=payload)
        st.success('Saved ' + fp)
    if st.button('New file'):
        name = st.text_input('New filename', value='newfile.py', key='nf')
        if name:
            st.session_state['current_file'] = name
            st.session_state['current_content'] = ''
with col2:
    st.subheader('AI code generation')
    prompt = st.text_area('Prompt for AI', value='Write a python function that calculates factorial.')
    if st.button('Generate'):
        r = requests.post(BACKEND + '/api/ai/generate', json={'prompt': prompt})
        out = r.json()
        if out.get('source') == 'mock':
            st.code(out.get('code',''), language=out.get('language','python'))
            if st.button('Apply to editor'):
                st.session_state['current_content'] = out.get('code','')
                st.experimental_rerun()
        else:
            st.text(str(out))

st.markdown('---')
st.subheader('Terminal (collaborative)')
session_id = st.text_input('Terminal session id', value='demo')
terminal_url = BACKEND + '/terminal?session_id=' + urllib.parse.quote(session_id)
st.markdown(f"Open the terminal in a new tab: [Terminal]({terminal_url})")
st.components.v1.iframe(terminal_url, height=400)
