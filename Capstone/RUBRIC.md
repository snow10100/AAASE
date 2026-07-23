# Capstone Completion Checklist

Evaluated as **Complete / Needs Completion** — not a score.

This is a five-day learning course, not a production-readiness competition. The point of the capstone is to show that you can **design, run, and explain a small AI agent.** That's it.

## Complete when your team can demonstrate all of:

- You identified a problem or task for the agent.
- You produced runnable AI-agent code.
- The agent accepts an input and produces an observable result.
- The implementation includes **at least one agentic behavior** — one of:
  - calling a tool,
  - routing between steps,
  - maintaining state,
  - using multiple agent roles,
  - revising or evaluating an answer,
  - executing a multi-step workflow.
- You can explain the main components of your implementation.
- You show a **live run, recorded run, or saved execution output.**
- You briefly describe the architecture, libraries, and models used.
- If working in a team, **every member can explain their contribution.**

Meeting this checklist is sufficient. Nothing beyond it earns "extra."

## What "a runnable AI agent" means (the only boundary)

A plain one-shot prompt wrapper doesn't count on its own. You need **one recognizable agentic element**:

```
Input → model decides → tool or workflow step → result
```

That can be tiny. Any of these qualifies:

- a model chooses between two functions;
- a LangGraph workflow routes between two nodes;
- an agent calls one search or calculation tool;
- a reviewer step asks for one revision;
- two specialized roles pass a result between them.

We're checking **understanding, not performance.**

## Explicitly NOT graded (all optional learning)

None of these add credit, and their absence takes nothing away:

Docker / Podman · VPS or cloud deployment · frontend design · domain names or HTTPS · Langfuse or other tracing · structured logging & monitoring · performance, latency, or token cost · output quality or domain accuracy · reliability, retries, fallback models · security guardrails & red-teaming · databases, memory, or volumes · number of agents/tools/frameworks · visual polish · complexity of the idea.

A small agent that runs and can be explained meets the objective. A sophisticated deployment is welcome **only if your team wants to explore it.**

## Presentation (light, everyone speaks)

Briefly cover:

1. The problem you selected.
2. What the agent does.
3. The architecture or workflow.
4. A demonstration or recorded run.
5. The stack and libraries used.
6. What you learned or found difficult.

You will **not** be compared against other teams on output quality, speed, interface, or infrastructure.

## Instructor quick-check

```bash
MOCK=1 python agent.py run "a task"     # produces an observable result
# confirm ONE agentic behavior is present (a route, a tool call, a revision, state, roles)
# ask each member what they built
```
