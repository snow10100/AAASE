# Guide 5 (STRETCH S4) — Put a UI on Your Agent

> **Optional and ungraded.** Finish the runnable agent first. This guide is here for students who want extra hands-on practice. Doing it gives no grading advantage; skipping it has no penalty.

Goal: something a human can click, not just `curl`. It's a *demo* layer — don't let it eat the hours the agent deserves.

## The one hard rule on the class server

You get **one port** (`$MY_PORT`), which means **one process**, reachable at your one HTTPS URL. So on the server your UI and API must live in the **same process, same origin**:

```
https://studentNN.apps.ibrahimalshehri.sa/        → your UI
https://studentNN.apps.ibrahimalshehri.sa/run     → your API
https://studentNN.apps.ibrahimalshehri.sa/docs    → API docs
```

Same origin has a bonus: the browser makes same-origin calls, so you **don't need permissive CORS** (`allow_origins=["*"]`). Locally you can run two ports while developing; just collapse to one process before you deploy.

Two ways the UI reaches the agent:
- **Direct import** — the UI does `from agent import run`. Simplest; Gradio/Streamlit only.
- **HTTP** — the UI calls `POST /run`. Required for React; also how a mounted UI talks to your API.

---

## Option A — Gradio (recommended: fastest, Python)

**Local dev:**
```bash
pip install gradio
```
```python
# ui_gradio.py
import gradio as gr
from agent import run                       # your Milestone-7 entrypoint

def chat_fn(message, history):
    result = run(message)
    if result["status"] == "blocked":
        return f"🚫 Blocked: {result['reason']}"
    return result.get("report") or result.get("result", "")

demo = gr.ChatInterface(chat_fn, title="My Agent")

if __name__ == "__main__":
    demo.launch()                           # local only
```

> **Do NOT use `share=True`.** It opens an external tunnel that bypasses your domain, may be blocked by the classroom network, and hands you a second public endpoint you don't control. On the server you go through Caddy, not a tunnel.

**Deploy — pick one:**

*A1. Gradio IS your process* (UI + agent, no separate FastAPI):
```python
import os
demo.launch(server_name="127.0.0.1", server_port=int(os.environ["MY_PORT"]))
```

*A2. Mount Gradio inside your FastAPI* (keep `/run` and `/docs` too — nicest):
```python
# in your FastAPI file
import gradio as gr
from agent import run   # or call your own /run

def chat_fn(message, history):
    r = run(message)
    return r.get("result", "") if r["status"] == "ok" else f"Blocked: {r['reason']}"

demo = gr.ChatInterface(chat_fn)
api = gr.mount_gradio_app(api, demo, path="/ui")   # api is your FastAPI app
```
Then run the FastAPI app on `$MY_PORT` (Guide 3). UI at `/ui`, API at `/run`, docs at `/docs` — one process, one origin.

---

## Option B — Streamlit (best if you want a dashboard)

Nice when you want chat **plus** a metrics/logs view. Note: Streamlit runs as its own server, so if you deploy Streamlit it becomes your one process (you won't also expose `/docs` on that port — fine for a UI-first demo).

```bash
pip install streamlit
```
```python
# ui_streamlit.py
import streamlit as st
from agent import run

st.title("My Agent")
if prompt := st.chat_input("Give the agent a task..."):
    st.chat_message("user").write(prompt)
    result = run(prompt)
    with st.chat_message("assistant"):
        if result["status"] == "blocked":
            st.error(f"Blocked: {result['reason']}")
        else:
            st.write(result.get("result", ""))
            st.json({k: result[k] for k in ("score", "latency_ms", "cost_usd") if k in result})
```

Deploy on **your** port, loopback (not the default 8501):
```bash
streamlit run ui_streamlit.py \
  --server.address 127.0.0.1 --server.port "$MY_PORT" \
  --server.headless true
```
Caddy publishes it at your HTTPS URL.

---

## Option C — React + Vite (only if your team already knows React)

React can't import Python, so it always talks **HTTP** — and on the server it must be **built to static files and served by your FastAPI**, so it shares your one port and origin.

**Build & wire the API as a relative path** (no hardcoded host, so it works behind your subdomain):
```jsx
// src/App.jsx
import { useState } from "react";
const API = "";                              // relative → same origin as the page

export default function App() {
  const [task, setTask] = useState("");
  const [out, setOut] = useState("");
  async function run() {
    const r = await fetch(`${API}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task }),
    });
    const data = await r.json();
    setOut(r.status === 422 ? `Blocked: ${data.detail}` : data.result);
  }
  return (
    <div style={{ maxWidth: 640, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h1>My Agent</h1>
      <textarea rows={3} value={task} onChange={(e) => setTask(e.target.value)} style={{ width: "100%" }} />
      <button onClick={run}>Run</button>
      <pre style={{ whiteSpace: "pre-wrap" }}>{out}</pre>
    </div>
  );
}
```
```bash
npm create vite@latest agent-ui -- --template react
cd agent-ui && npm install && npm run build      # produces dist/
```

**Serve `dist/` from FastAPI** (mount LAST, after your API routes):
```python
from fastapi.staticfiles import StaticFiles
# ... define /run, /health first ...
api.mount("/", StaticFiles(directory="agent-ui/dist", html=True), name="ui")
```
Now `/` serves the React app and `/run` is the API — one process on `$MY_PORT`, one origin, no CORS needed.

*Local dev only:* `npm run dev` (port 5173) calling `http://localhost:8000` is fine — that's the one time you need CORS (below). Don't deploy the dev server.

---

## CORS — local dev only

Only needed when the browser page and the API are on **different origins** (i.e. `npm run dev` on :5173 → API on :8000). On the class server everything is one origin, so skip it. If you do need it locally:

```python
from fastapi.middleware.cors import CORSMiddleware
api.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])
```
Prefer naming the dev origin over `["*"]`.

---

✅ *S4 done:* someone opens your HTTPS URL, types a task, and watches the agent answer — and a hostile prompt shows a clean "Blocked" message, not a crash. Screenshot for your README.

## Debug order

1. UI loads but calls 404/blocked → the static mount is above your API routes; mount `StaticFiles` **last**.
2. CORS error in the browser console → you're cross-origin; either collapse to one process (deploy) or add the dev-origin CORS (local).
3. `/docs` gone after adding Streamlit → expected; Streamlit is its own server. Use Gradio-mounted-in-FastAPI (A2) if you want both.
4. Works locally, 502 on the URL → your one process isn't listening on `$MY_PORT`/`127.0.0.1` (Guide 3).
