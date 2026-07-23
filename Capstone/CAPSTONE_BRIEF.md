# Capstone — Build & Explain a Small AI Agent

**Teams of 3. ~5–6 hours, instructor in the room. You have everything you need from Days 2–4.**

## The deal

Build a small AI agent that **runs**, and be able to **explain and demo it.** That's the whole capstone. It's assessed **Complete / Needs Completion** — not scored (see `RUBRIC.md`).

You're not proving production-readiness in an afternoon. You're showing you can design, run, and talk about an agent you built.

## What "complete" means

Your project is complete when your team can show:

- a problem you picked for the agent,
- runnable agent code that takes an input and produces an observable result,
- **at least one agentic behavior** — a tool call, routing between steps, keeping state, multiple roles, a revise/evaluate step, or a multi-step workflow,
- a live/recorded run or saved output,
- a short explanation of your components, stack, and models,
- and (in a team) each member able to explain their part.

That's the bar. The **one** thing that doesn't count on its own is a plain single-prompt wrapper — you need one recognizable agentic element:

```
Input → model decides → tool or workflow step → result
```

It can be tiny (a model choosing between two functions; a graph routing between two nodes; one tool call; one revision loop; two roles handing off). We're checking understanding, not performance.

## Build it from scratch

You've built three agents this week (Days 2–4). Open a **blank `agent.py`** and build a fourth — your own, for a purpose you pick. Keep your Day 2–4 files open as reference, but type it yourself; that's how you prove you own the patterns. `guides/01_BUILD_THE_AGENT.md` walks it milestone by milestone with current doc links.

## Pick a purpose

Anything with a real multi-step job. Off-the-shelf ideas from the Day 5 deck:

1. **Document / contract auditor** — read a doc, extract terms, check a policy, give a verdict. *(Most self-contained.)*
2. **Log / threat triage** — scan fake logs, classify incidents, recommend an action.
3. **Onboarding / workflow orchestrator** — a small multi-agent pipeline.

Or invent your own. Keep the domain simple so building the agent is the focus.

## Everything else is optional (and ungraded)

Deployment, Docker/Podman, a frontend, HTTPS, tracing, guardrails, monitoring, databases — all genuinely useful, all **optional learning**, none of it adds or removes credit. The stretch guides are there if your team wants the hands-on practice, not because they're hidden requirements:

- `guides/02_STRETCH_docker.md` — containerize it (local).
- `guides/03_STRETCH_deploy_vps.md` — deploy to the class server at your own HTTPS URL.
- `guides/04_STRETCH_observability.md` — real tracing with Langfuse.
- `guides/05_STRETCH_frontend.md` — a clickable UI (Gradio / Streamlit / React).

Do as many, or as few, as you like. A small agent that runs and can be explained already meets the objective.

## Presentation (light, ~1–3 min, everyone speaks)

No slides required. Cover: the problem, what the agent does, the workflow, a demo or recorded run, your stack, and what you learned or found hard. You won't be compared against other teams. The goal is simply to stand up and talk about your agent.

## Team split (suggestion)

- **Graph** — state, nodes, the one agentic behavior.
- **Explainer** — can walk anyone through how it works; owns the demo.
- **Wildcard** — either strengthens the agent or explores a stretch guide.

Rotate whoever owns merging so the pieces come together before you present.

## Files in this folder

- `guides/01_BUILD_THE_AGENT.md` — **start here.** Build the agent, milestone by milestone.
- `guides/02–05_STRETCH_*.md` — optional, ungraded extras.
- `RUBRIC.md` — the Complete/Needs-Completion checklist.
- `SUBMISSION.md` — how to submit (GitHub repo `AAASE-CAPSTONE`, README + screenshots, no secrets).
