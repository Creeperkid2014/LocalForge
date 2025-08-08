import os, requests, json

OLLAMA_URL = os.getenv('OLLAMA_API_URL')  # e.g. http://localhost:11434

def generate_code(prompt: str, language: str = 'python'):
    # If Ollama local server is available, use it (simple endpoint example)
    if OLLAMA_URL:
        try:
            payload = {'model': 'llama2', 'prompt': prompt}
            resp = requests.post(f'{OLLAMA_URL}/api/generate', json=payload, timeout=10)
            if resp.status_code == 200:
                return {'source': 'ollama', 'output': resp.text}
        except Exception as e:
            return {'source': 'ollama', 'error': str(e)}
    # Fallback mock engine
    code = f"""# Mock code generated for prompt:\n# {prompt}\ndef example():\n    return 'hello'\n"""
    explanation = 'This is mock generated code. Install and configure a local model (Ollama) for real output.'
    return {'source': 'mock', 'language': language, 'code': code, 'explanation': explanation}
