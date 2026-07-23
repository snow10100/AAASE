# Guide 3 (STRETCH S2) — Deploy to the Class Server

> **Optional and ungraded.** Finish the runnable agent first. This guide is here for students who want extra hands-on practice. Doing it gives no grading advantage; skipping it has no penalty.

Goal: your agent runs on the shared class VM and anyone can reach it at your own **HTTPS URL** — `https://studentNN.apps.ibrahimalshehri.sa`. You already have an account there; login is your **GitHub SSH key** (nothing to download).

**The one rule for this server:** your whole project — API and UI — must be reachable through **one process, on your one `$MY_PORT`, bound to `127.0.0.1`**. Caddy turns that loopback port into your public HTTPS subdomain. You never open a raw port to the internet, and you never run Docker here (that's a local exercise — Guide 2).

---

## Step 1 — Log in (2 min)

Your handout has the exact line. It uses the SSH key already on your GitHub account:

```bash
ssh studentNN@ssh.apps.ibrahimalshehri.sa
```

No password, no key file. If it refuses: check `https://github.com/YOUR_USERNAME.keys` actually shows a key, and that you're on the laptop with the matching private key. Your port and URL are already set:

```bash
echo $MY_PORT      # e.g. 8107
echo $MY_HOST      # e.g. student07.apps.ibrahimalshehri.sa
```

---

## Step 2 — Get your code + a venv (10 min)

`git clone` your repo into `~/app` (or `scp` it up). Then a virtual environment — **no Docker on this box**:

```bash
cd ~/app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Put your key in a local `.env` (never commit it):

```bash
cat > .env <<'ENV'
OPENAI_API_KEY=sk-or-YOUR-KEY
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=nvidia/nemotron-3-super-120b-a12b:free
ENV
```

---

## Step 3 — Run on YOUR port, on loopback (5 min)

```bash
uvicorn agent:api --host 127.0.0.1 --port $MY_PORT
```

`--host 127.0.0.1` is the whole trick: your app is private to the VM, and **Caddy** is the only thing allowed to reach it and publish it over HTTPS. (Binding `0.0.0.0` here would do nothing useful — the firewall only allows 22/80/443.)

On the VM, in a second SSH tab, confirm it's alive:
```bash
curl -s localhost:$MY_PORT/health
```

---

## Step 4 — See it live from anywhere (2 min)

From any browser:
```
https://studentNN.apps.ibrahimalshehri.sa/health
https://studentNN.apps.ibrahimalshehri.sa/docs      # FastAPI's auto UI — great to demo
```

HTTPS is automatic (Caddy issues the certificate on first hit). **Before your app is running, the URL shows a Caddy 502 — that's normal**, not a bug; it means "nothing is listening on your port yet."

---

## Step 5 — Keep it running after you log off (5 min)

A bare `uvicorn` dies when you close the SSH session, and your URL goes 502. Pick one:

- **tmux (simplest):**
  ```bash
  tmux new -s agent          # run uvicorn inside
  # detach: Ctrl-b then d   |   reattach later: tmux attach -t agent
  ```
- **systemd --user (survives logout cleanly):** see `SINGLE_VM_SETUP.md` §6 for the ready-made unit.

✅ *S2 done:* a teammate on another laptop opens `https://studentNN.apps.ibrahimalshehri.sa/docs` and calls your agent. Screenshot it for your README.

---

## Cost + courtesy

The VM bills while it runs and everyone shares it. Don't leave an agent looping on paid API calls when you step away — stop your process (`Ctrl-c`, or `systemctl --user stop agent`). The instructor stops the whole VM outside class hours; because it has a static IP, your URL is the same when it comes back — no reconnect dance.

## Debug order

1. `ssh` refused → no key at `github.com/USER.keys`, or wrong laptop/username.
2. URL shows 502 → your app isn't listening on `$MY_PORT` (start it), or it bound the wrong port.
3. App runs but `/run` errors → read your logs: `journalctl --user -u agent -f` (systemd) or scroll your tmux pane. Your Milestone-5 JSON logs pay off here.
4. Works over SSH `curl localhost` but not the URL → you bound `127.0.0.1` (correct) but used a port that isn't yours; `echo $MY_PORT` and match it.
