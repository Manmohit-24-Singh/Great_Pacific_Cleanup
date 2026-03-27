import sys
import json
import asyncio

async def fetch_json(url, method="GET", headers=None, body=None):
    if sys.platform == "emscripten":
        # Pygbag/WebAssembly environment
        import js
        import json as python_json
        
        js_opts = js.JSON.parse(python_json.dumps({
            "method": method,
            "headers": headers or {},
            **({"body": python_json.dumps(body)} if body else {})
        }))
        
        # In Pygbag/Pyodide, JS promises can be awaited natively
        response = await js.window.fetch(url, js_opts)
        text = await response.text()
        
        try:
            res_json = python_json.loads(text)
        except Exception:
            res_json = {"text": text}
            
        return response.status, res_json
    else:
        # Standard desktop fallback (for testing locally)
        import requests
        if method == "GET":
            res = requests.get(url, headers=headers)
        elif method == "POST":
            res = requests.post(url, headers=headers, json=body)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        try:
            res_json = res.json()
        except:
            res_json = {"text": res.text}
            
        return res.status_code, res_json
