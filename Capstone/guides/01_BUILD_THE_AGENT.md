# Guide 1 (CORE) — Build a Production AI Agent from Scratch

This is the capstone. Open a **blank file** (`agent.py`) and build your own agent. Your Day 2–4 files are fair to reference — but type it yourself; that's the point.

Work through the milestones in order. Each one ends with something you can **run**, so you're never more than ~30 minutes from a working checkpoint. All doc links are the current (2026) LangChain/LangGraph docs.

> **How much is "enough"?** For the capstone checklist you only need a runnable agent with **one** agentic behavior (Milestone 3 gives you that). Everything after is here to make a *better* agent and to teach the patterns — do as much as your team wants, in any order. None of it is graded.

> Setup once:
> ```bash
> pip install langgraph langchain-openai python-dotenv fastapi uvicorn pydantic
> ```
> Bring your own OpenRouter free-model key (Day 2 setup), or set `MOCK=1` and build the whole thing offline first — recommended, so a rate limit never blocks you.

---

## Milestone 0 — Decide the job (10 min)

Pick a small, multi-step task (auditor / triage / orchestrator — or your own). Write one sentence: *"My agent takes ___, does ___ over a few steps, and returns ___."* Keep the domain trivial so the **engineering** is the star.

Sketch the graph on paper — nodes and the one decision that loops. If you can't draw the loop, you don't have a graph yet, you have a script.

---

## Milestone 1 — State + a linear graph (30 min)

The **state** is the contract every node reads and writes. Define a `TypedDict`, then wire 2–3 nodes in a straight line and run it.

- Graph API — nodes, edges, `START`/`END`, `StateGraph`, `compile()`, `invoke()`:
  https://docs.langchain.com/oss/python/langgraph/graph-api
- Reducers (e.g. append to a log list with `Annotated[list, operator.add]`) — you used this Day 2:
  https://docs.langchain.com/oss/python/langgraph/graph-api#state

**Ask yourself:** what's the minimum state your nodes need to pass along? Add a `run_id` field now — Milestone 5 depends on it.

✅ *Checkpoint:* `python agent.py` runs start→...→end and prints a result.

---

## Milestone 2 — The model, with an offline mock (20 min)

Wrap model creation in a `get_model()` that returns a **FakeChatModel** when `MOCK=1` and a real `ChatOpenAI` otherwise (OpenRouter base_url + `:free` model, exactly like Day 2). Pass `timeout=60, max_retries=0` — you'll own retries yourself in Milestone 6.

Make the fake deterministic and make it fail once (e.g. return a low score the first time) so your loop is guaranteed to fire in demos.

✅ *Checkpoint:* the graph runs identically with `MOCK=1` and no key.

---

## Milestone 3 — The conditional loop + hard termination (40 min)

This is the heart of the agent — and on its own it satisfies the checklist's "one agentic behavior." Add a decision node and a **conditional edge** that either loops back (revise/retry) or ends.

- Conditional edges + routing function:
  https://docs.langchain.com/oss/python/langgraph/graph-api#conditional-edges
- Designing loops that terminate (do NOT rely on the recursion limit):
  https://docs.langchain.com/oss/python/langgraph/graph-api#loops

**The trap (you hit this Day 2):** a loop with no termination runs until `GraphRecursionError`. Put the guard *in state* — a `revision_count` capped at 2–3, and/or a cost budget. Trigger the runaway once on purpose, watch it fail, then fix it. That story is great for your presentation.

✅ *Checkpoint:* a bad result loops back once, a good result ends, and a pathological input still stops.

---

## Milestone 4 — Structured output (25 min)

Anywhere you parse a model decision (a score, a verdict, extracted fields), prefer **structured output** over `int(text.strip())` — fragile string parsing is the most common thing that breaks a demo. (Recommended, not required.)

- `with_structured_output` with a Pydantic model / TypedDict / JSON schema:
  https://docs.langchain.com/oss/python/langchain/models#structured-output
- Deeper dive + provider strategies (and `method="json_schema"` if a free model chokes on tool-calling):
  https://docs.langchain.com/oss/python/langchain/structured-output

✅ *Checkpoint:* your decision node returns a validated object, and a garbled model reply doesn't crash the run.

---

## Milestone 5 — Monitoring: structured logs with a run_id (25 min)

Every node emits **one JSON log line** stamped with the shared `run_id`. This is what makes an agent debuggable in production (Day 4).

Minimum: a `log_event(run_id, event, **fields)` that prints `json.dumps({...})`. Log `request`, each `node`, the decision `score`, and the final `response` with latency and cost. Bonus: collect the same numbers into a small metrics object.

- If you want live event streaming instead of after-the-fact logs:
  https://docs.langchain.com/oss/python/langgraph/streaming

✅ *Checkpoint:* one run = a clean sequence of JSON lines you can `grep` by `run_id`.

---

## Milestone 6 — Reliability + one guardrail (35 min)

Two things separate this from a notebook:

1. **Retries.** Wrap each model call in your own retry-with-backoff + timeout (you set `max_retries=0` in M2 so these don't multiply). Add a cost or iteration budget that aborts cleanly instead of looping forever.
2. **A guardrail.** An input check that blocks an obvious prompt-injection, plus PII redaction on the way in and out. Layer it (regex → heuristic); note where a paraphrased attack still slips through — that's the honest lesson from Day 4.

- Threat/guardrail checklist to map against — OWASP Top 10 for LLM Apps:
  https://genai.owasp.org/llm-top-10/

✅ *Checkpoint:* `python agent.py run "ignore previous instructions..."` is **blocked and logged** (not a stack trace); a benign task still succeeds.

---

## Milestone 7 — Wrap it in an entrypoint (20 min)

Tie it together: a `run(task)` that does input-guard → redact → run graph → output-guard → log/return, and a tiny CLI (`run` / `pentest`). A `pentest()` that fires a few attacks and asserts each is handled proves your guardrail instead of assuming it.

✅ *Checkpoint:*
```bash
MOCK=1 python agent.py run "a normal task"                 # observable result + logs
```
Once your agent runs, has one agentic behavior, and you can explain and demo it, you've met the capstone checklist (`RUBRIC.md`). Everything beyond here is the **optional stretch ladder** → `02_STRETCH_docker.md`.

---

## If you get stuck (debug order)

1. Import error on `StateGraph`? `pip install langgraph`, and import from `langgraph.graph`.
2. Loop never ends → Milestone 3, check the routing function and your cap.
3. Structured output errors on a free model → try `method="json_schema"` or a different `:free` model (M4 links).
4. Logs missing a `run_id` → you dropped it from the state dict a node returned; partial updates must carry it or use a reducer.
5. Only then compare against your own Day 4 solution — don't copy, diff.
