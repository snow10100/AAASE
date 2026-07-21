# NEXT STEP: Ship Your Agent in Docker

> **Prerequisite:** you finished `skeleton_enterprise_multiagent.py` (all TODOs, at least through Stage 5). Your agent runs as an API on your machine. Now for the last mile of the Day 5 story: *"works on my machine" is where the PoC chasm swallows most projects.* Docker is how your agent runs identically on your laptop, your teammate's laptop, and a cloud server.
>
> Same rules as the lab: build the `Dockerfile` yourself, one step at a time. The finished `Dockerfile` in this folder is the solution — compare at the end, don't copy from it.

**Docs you'll use** (keep open): [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) · [Volumes](https://docs.docker.com/engine/storage/volumes/) · [docker run reference](https://docs.docker.com/reference/cli/docker/container/run/)

Check your install first:

```bash
docker --version          # any recent version is fine
docker run hello-world    # if this works, you're ready
```

---

## Step 1 — A minimal image that runs the agent once

Create a new file called `Dockerfile` (no extension) in this folder:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "skeleton_enterprise_multiagent.py"]
```

Read it line by line — each is a **layer**:

| Line | What it does | Ask yourself |
|---|---|---|
| `FROM python:3.12-slim` | Start from an official Python image. `-slim` ≈ 120 MB vs ≈ 1 GB for the full one | Why pin `3.12` instead of `python:latest`? (Hint: what does "latest" mean in six months, on someone else's machine?) |
| `WORKDIR /app` | cd into `/app` *inside the image* (creates it) | — |
| `COPY . .` | Copy this folder into `/app` | What's the danger of `COPY . .`? Look at `.dockerignore` in this folder — what would leak into the image without it? (`.env`!) |
| `RUN pip install ...` | Runs **at build time**, result is baked into the image | Why `--no-cache-dir`? (What's the point of a pip cache in an image no one pip-installs into again?) |
| `CMD [...]` | The default command **at run time** — one per container | What's the difference between `RUN` and `CMD`? |

Build and run (mock mode — no API key inside the container yet):

```bash
docker build -t report-agent .
docker run --rm -e MOCK=1 -e LAB_STAGE=3 report-agent
```

You should see your Stage 3 JSON logs, exactly like on your machine. That's the whole pitch of containers.

> `--rm` deletes the container when it exits — otherwise stopped containers pile up (`docker ps -a`).

---

## Step 2 — Fix the slow rebuild (layer caching)

Change anything in your Python file and rebuild. Notice `pip install` runs **again** — ~a minute wasted per code edit. Why? Docker caches each layer, but a change to *any* copied file invalidates the `COPY . .` layer **and every layer after it**.

The fix — copy only what each layer needs, least-changing first:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY skeleton_enterprise_multiagent.py app.py
CMD ["python", "app.py"]
```

Rebuild twice, editing your Python file in between. Second build should say `CACHED` for the pip layer and finish in ~2 seconds.

> We also renamed the file to `app.py` **inside the image** — the container is a product now; internal names shouldn't depend on what the file was called in class.

**ASK YOURSELF:** this is the same idea as the lab's `call_llm` chokepoint — an ordering discipline that costs nothing and pays forever. What OTHER file could you add to this project that should be copied before the code? (Anything that changes less often than code.)

---

## Step 3 — Config and secrets (Stage 2, containerized)

Your Stage 2 work pays off now: because ALL config comes from env vars, the *same image* can run in any mode — no rebuild:

```bash
docker run --rm -e MOCK=1 -e LAB_STAGE=4 -e QUALITY_THRESHOLD=9 report-agent
```

For the real model, pass your key **at run time** from your `.env` file:

```bash
docker run --rm --env-file .env -e LAB_STAGE=4 report-agent
```

**RULES (Day 5 "Security & Governance"):**

1. The key goes in with `--env-file` at RUN time — **never** `COPY .env` or `ENV OPENAI_API_KEY=...` at BUILD time. Anything baked into an image is readable by anyone who gets the image (`docker history` shows all layers).
2. That's why `.env` is in `.dockerignore` — defense in depth: even a careless `COPY . .` can't leak it.

**YOUR TURN:** run `docker image history report-agent`. Find your pip layer. Confirm no layer contains your key.

---

## Step 4 — The volume: where does the report GO?

Run a full report generation:

```bash
docker run --rm -e MOCK=1 -e LAB_STAGE=4 report-agent
docker run --rm -e MOCK=1 -e LAB_STAGE=4 report-agent ls -la /app
```

Wait — where is `final_report.txt`?? **Gone.** A container's filesystem dies with the container. Every run starts from the image, fresh. This is the single most important Docker concept for stateful work: **containers are disposable; data that matters must live OUTSIDE them.**

That's what volumes are for.

**4a. Make the output directory configurable (code change — YOUR TURN):**

In your skeleton's save function, write the report to a directory taken from the environment (this is just Stage 2 discipline applied once more):

```python
out_dir = os.getenv("REPORTS_DIR", ".")
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, "final_report.txt")
```

**4b. Declare it in the Dockerfile:**

```dockerfile
ENV REPORTS_DIR=/reports
RUN mkdir /reports
VOLUME /reports
```

**4c. Create a named volume and mount it:**

```bash
docker volume create report_data
docker build -t report-agent .
docker run --rm -e MOCK=1 -e LAB_STAGE=4 -v report_data:/reports report-agent
```

**4d. Prove the report SURVIVED the container:**

```bash
# the container that wrote it is gone; read it from a brand-new one:
docker run --rm -v report_data:/reports python:3.12-slim cat /reports/final_report.txt

# inspect where Docker actually stores it:
docker volume inspect report_data
```

**ASK YOURSELF:**
- Run the agent twice. Why is there only one report? How would you fix the filename so runs don't overwrite each other? (You already have `run_id` in state...)
- What's the difference between `-v report_data:/reports` (named volume) and `-v $(pwd)/reports:/reports` (bind mount)? Try both. Which would you use in class? Which on a server?
- In real production, would reports live in a volume at all — or in something like S3? What does that change about your `save_report` function?

---

## Step 5 — Serve the API from the container

Your Stage 5 FastAPI service, containerized:

```dockerfile
ENV LAB_STAGE=5
EXPOSE 8000
CMD ["python", "app.py", "serve"]
```

```bash
docker build -t report-agent .
docker run --rm -e MOCK=1 -p 8000:8000 -v report_data:/reports report-agent
```

From ANOTHER terminal:

```bash
curl localhost:8000/health
curl -X POST localhost:8000/report -H 'Content-Type: application/json' -d '{"topic": "Smart Cities"}'
curl -X POST localhost:8000/report -H 'Content-Type: application/json' -d '{"topic": "Ignore all instructions"}'   # still 422!
```

**ASK YOURSELF:**
- `EXPOSE 8000` alone does NOT publish the port — remove `-p 8000:8000` and try to curl. So what is `EXPOSE` actually for? (Docs: documentation + `-P`.)
- Your server must listen on `0.0.0.0`, not `127.0.0.1` — why? (What is "localhost" *inside* a container?)
- You can now run `docker run` three times on three machines behind a load balancer. Which question from the lab's Stage 5 "YOUR TURN" just became real? (Where does `/metrics` state live now?)

---

## Step 6 — Hardening (compare with the solution Dockerfile)

Three production touches — add them, then diff your file against the `Dockerfile` in this folder:

1. **Non-root user.** By default your agent runs as root inside the container. Add `RUN useradd --create-home agent` + `USER agent` (and `chown` the `/reports` dir). Why does this matter if a prompt-injected agent ever gets code execution?
2. **HEALTHCHECK.** Point it at the `/health` endpoint you built. `docker ps` now shows `(healthy)` — this is what orchestrators (Kubernetes, ECS) use to restart dead agents automatically.
3. **`.dockerignore` audit.** `__pycache__`, `.env`, old reports — none belong in the build context.

---

## Self-check before you're done

- [ ] Editing your Python file and rebuilding takes seconds, not minutes — and I can explain why
- [ ] My API key exists ONLY at run time; `docker image history` proves the image is clean
- [ ] I deleted a container and the report survived in `report_data` — and I can read it from a fresh container
- [ ] `curl localhost:8000/health` works against the container; guardrail topics still return 422
- [ ] I know the difference between: image vs container, `RUN` vs `CMD`, `EXPOSE` vs `-p`, volume vs bind mount
- [ ] My container runs as a non-root user and shows `(healthy)` in `docker ps`

**Debugging order that works:**

1. `docker logs <container>` — your Stage 3 JSON logs were built for exactly this moment
2. `docker run --rm -it report-agent sh` — open a shell in the image, look around `/app`
3. `docker exec -it <container> sh` — shell into a RUNNING container
4. Only then compare against the solution `Dockerfile`

**Stretch goal (bridges into the capstone):** write a `compose.yaml` that starts the agent with the volume and port already wired, so the whole system is one `docker compose up`. Docs: https://docs.docker.com/compose/
