import sys
import json
import asyncio

async def fetch_json(url, method="GET", headers=None, body=None):
    if sys.platform == "emscripten":
        # Pygbag/WebAssembly environment
        import js
        import json as python_json
        
        js_headers = js.Object.fromEntries(js.Object.entries(js.JSON.parse(python_json.dumps(headers or {}))))
        
        fetch_opts = {
            "method": method,
            "headers": js_headers,
        }
        if body:
            fetch_opts["body"] = python_json.dumps(body)
            
        # Call JS fetch
        promise = js.window.fetch(url, js.Object.fromEntries(js.Object.entries(js.JSON.parse(python_json.dumps(fetch_opts)))))
        response = await asyncio.wrap_future(promise)
        
        # Read text
        text_promise = response.text()
        text = await asyncio.wrap_future(text_promise)
        
        return response.status, python_json.loads(text)
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
