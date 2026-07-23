# AAASE Capstone — GitHub Submission Instructions

Submit your capstone as a **GitHub repository**. It's checked **Complete / Needs Completion** (see `RUBRIC.md`) — visual design, deployment, and performance are not graded. The goal is a runnable AI agent you can explain.

## Repository

- **Name it `AAASE-CAPSTONE`** (teams may add a suffix, e.g. `AAASE-CAPSTONE-TeamFalcon`).
- **Public**, or shared with the instructor's GitHub account.
- Contains **only your capstone** — do **not** commit the Day 1–4 labs. You may reuse ideas/code you understand, but include only files that are genuinely part of your final project.
- Teams: one repo under one member's account; add the others as **collaborators** and list everyone in the README.

> The instructor checks by GitHub username, so the exact repo name and the README member list are what make you findable. Pinning the repo to your profile helps.

## Required contents

- `README.md` (see below)
- your agent source code
- a dependency file (`requirements.txt` or `pyproject.toml`)
- run instructions
- screenshots or saved outputs showing it running
- `.env.example` and a `.gitignore`

Include only if you made them: `Dockerfile` / container config, frontend code, architecture diagram files, test/eval scripts, example input–output files, deployment screenshots.

## README must include

1. **Title & team** — project name; members with GitHub usernames; one line on each person's contribution.
2. **Problem statement** — what problem, who has it, why you chose it.
3. **How the agent solves it** — input → the steps it performs → the tools/decisions/roles/workflow it uses → the result. Make clear which part is the **agentic behavior** (a tool call, a route between steps, a revision loop, state, or multiple roles).
4. **Architecture** — a diagram (Mermaid, draw.io, Excalidraw, PowerPoint…) showing input, agent(s), model, tools, state/memory, external services, output.
5. **Tech stack** — language, model/provider, agent framework, libraries, APIs/tools, any storage/frontend/deployment — and a line on *why* you chose the main ones.
6. **How to run** — clear, copy-pasteable, e.g.:
   ```bash
   git clone <repo-url> && cd AAASE-CAPSTONE
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env        # then add your key
   python agent.py
   ```
7. **Demonstration evidence** — proof it ran: screenshots, terminal output, example in/out, tool-call output, logs/traces, or a short recording link. Put images in `docs/images/` and embed them in the README, e.g. `![run](docs/images/run.png)`.
8. **Limitations & future work** — what works, what's incomplete, what you'd improve. Honest limitations are fine.

## Deployment evidence (optional, and time-boxed)

Deploying to the class server is **optional and ungraded** — but if you do it, **capture evidence today.**

> **The class VPS is deleted at ~10:00 PM tonight.** After that, your live URL is gone; only your screenshots remain as proof, and that's completely sufficient.

Good screenshots: your FastAPI `/docs` or frontend, the public `https://studentNN.apps.ibrahimalshehri.sa` in the address bar, a successful `/health` or request, and the running process/container. Add a short "Deployment" section to your README with those images.

## Security — never commit secrets

Do **not** commit `.env`, API keys, tokens, passwords, SSH private keys, or cloud credentials.

`.env.example` (names only, no values):
```bash
OPENAI_API_KEY=
OPENAI_BASE_URL=
MODEL_NAME=
```

`.gitignore` (minimum):
```gitignore
.env
.venv/
__pycache__/
*.pyc
*.key
data/
```

If you accidentally push a real secret, deleting it in a later commit is **not** enough — **rotate/revoke the key immediately** (it stays in git history).

## Before you leave (by 3 PM)

Have the **working code already on GitHub** before the VPS cleanup window — you can polish the README and add deployment screenshots afterward, but don't risk losing the code. Confirm:

- [ ] repo contains only the capstone (no Day 1–4 labs)
- [ ] README has: problem, how it solves it, architecture diagram, stack, run steps
- [ ] source + dependency file pushed
- [ ] at least one screenshot / saved output of it running
- [ ] all members + GitHub usernames listed
- [ ] **no secrets or private keys committed** (`.env` ignored, `.env.example` present)
- [ ] latest work committed and pushed
- [ ] the repo is public or shared with the instructor

That's it — a small agent that runs and is clearly explained meets the objective.
