# Guide 2 (STRETCH S1) — Containerize Your Agent

> **Optional and ungraded.** Finish the runnable agent first. This guide is here for students who want extra hands-on practice. Doing it gives no grading advantage; skipping it has no penalty.

Goal: your agent runs the same on any machine, and its results survive the container being deleted. This is the same incremental Docker build you saw in Day 3's `NEXT_STEPS_DOCKER.md` — reread that if any line is unfamiliar. Build the Dockerfile up one layer at a time; don't paste a finished one.

> **This is a LOCAL exercise.** On the shared class server you deploy with a **Python venv**, not Docker (Guide 3) — putting 35 people in the `docker` group on one box is effectively giving them all root. Learn Docker here on your own machine; deploy the agent to the server with venv. If you ever containerize on a shared host anyway, bind loopback only (`-p 127.0.0.1:$MY_PORT:8000`) and prefer rootless Podman.

Prereq: Docker installed on your own laptop. `docker --version`.

---

## Step 1 — A first (bad) image (10 min)

Add a FastAPI entrypoint to your agent if you haven't (a `serve` command running `uvicorn` on port 8000). Then the minimal Dockerfile:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "agent.py", "serve"]
```

```bash
docker build -t myagent .
docker run --rm -e MOCK=1 -p 8000:8000 myagent
curl localhost:8000/health
```

**Ask yourself:** change one line of code and rebuild. Why did it reinstall every package? (Layer caching — fix next.)

---

## Step 2 — Cache dependencies (10 min)

Copy `requirements.txt` and install *before* copying your code, so edits don't bust the pip layer:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "agent.py", "serve"]
```

Rebuild twice with a code edit in between — the second build should skip the install. Add a `.dockerignore` (`__pycache__/`, `.env`, `*.pyc`, `.git`) so junk and secrets never enter the image.

---

## Step 3 — Secrets at run time, never baked in (10 min)

Your key comes from `--env-file`, not `COPY .env`. Prove it:

```bash
docker run --rm --env-file .env -p 8000:8000 myagent
docker image history myagent | grep -i key      # -> nothing. Good.
```

If your key shows up in `image history`, you baked it in — fix your `.dockerignore` and rebuild.

---

## Step 4 — Persist results in a VOLUME (15 min) ← the real lesson

Make your agent write its results/audit trail to a directory read from an env var (e.g. `AUDIT_DIR=/data/audit`), then declare and mount it:

```dockerfile
ENV AUDIT_DIR=/data/audit
VOLUME ["/data/audit"]
```

```bash
docker run --rm -e MOCK=1 -v myagent_data:/data/audit myagent python agent.py run "test task"
docker run --rm -v myagent_data:/data/audit myagent cat /data/audit/audit.jsonl
```

Run the agent, delete the container, then read the file from a **fresh** container — your records are still there. That's the difference between a demo and a system that remembers.

---

## Step 5 — Harden a little (10 min)

- Run as non-root:
  ```dockerfile
  RUN useradd -m appuser && mkdir -p /data/audit && chown -R appuser /data/audit
  USER appuser
  ```
- Add a `HEALTHCHECK` hitting `/health` so Docker knows when the container is actually ready.

✅ *S1 done:* image builds, runs on `MOCK=1` with no key, writes to a named volume that survives `docker rm`, and no secret is baked in. Next: get it onto your VM → `03_STRETCH_deploy_vps.md`.

## Debug order

1. `curl` refused → is it `-p 8000:8000` and is the app binding `0.0.0.0` (not `127.0.0.1`)?
2. Build reinstalls every time → Step 2 layer order.
3. `.env` not found → you `.dockerignore`'d it (correct) but forgot `--env-file .env` at run time.
4. Volume empty on reread → your code isn't writing to `AUDIT_DIR`, or you used a different volume name.
