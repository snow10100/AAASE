# Guide 4 (STRETCH S3) — Real Observability with Langfuse

> **Optional and ungraded.** Finish the runnable agent first. This guide is here for students who want extra hands-on practice. Doing it gives no grading advantage; skipping it has no penalty.

Goal: see your agent's **thought trace** — which node ran, in what order, how long each took, tokens and cost — in a real dashboard, not just your JSON logs. This is the observability layer from the Day 4 deck (slide 59) made real.

Your structured logs (Milestone 5) answer *what happened*. A trace answers *why it happened and where the time went* across a multi-step run. Both matter; this adds the second.

---

## Step 1 — Get a Langfuse project (5 min)

Easiest is the free cloud tier: sign up at https://cloud.langfuse.com, create a project, and copy the **public** and **secret** keys. (If the instructor has a self-hosted Langfuse for the class, use that host + keys instead.)

```bash
pip install langfuse
```

Add to your `.env`:
```bash
TRACE=1
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Step 2 — Trace with a decorator, not a rewrite (15 min)

The whole point: tracing is *additive*. Wrap each graph node with the `@observe` decorator so every call becomes a span. Keep it a **no-op when `TRACE=0`** so keyless teammates and your offline `MOCK=1` runs are never blocked.

Pattern (build your own `trace` factory):
```python
def make_tracer():
    if os.getenv("TRACE", "0") != "1":
        return lambda name: (lambda f: f)      # no-op decorator
    from langfuse import observe
    return lambda name: observe(name=name)

trace = make_tracer()

@trace("research")
def research(state): ...
```

- Langfuse Python quickstart / `@observe`:
  https://langfuse.com/docs/observability/get-started
- Decorator reference:
  https://langfuse.com/docs/observability/sdk/python/decorators

---

## Step 3 — Run and look (10 min)

```bash
TRACE=1 python agent.py run "a normal task"     # needs a real key, not MOCK
```

Open your Langfuse project → Traces. You should see one trace per run, with a span per node, timing, and (if you attach usage) token counts. Trigger your revision loop and watch the extra spans appear — that visual is a great presentation moment.

**Ask yourself:** where did the time actually go? Traces routinely surprise people (one slow tool call dominates). That's the insight metrics alone hide.

---

## Optional — LiteLLM gateway (advanced)

If you route model calls through a LiteLLM proxy, it can emit traces to Langfuse *and* usage to a metering backend automatically, with zero per-call instrumentation. Overkill for the capstone, but it's the production pattern behind "every call is observed" — worth knowing it exists.

✅ *S3 done:* a screenshot of your trace (spans + timing) in the README, and you can point at the one span that surprised you.

## Debug order

1. Nothing in the dashboard → keys/host wrong, or you're running `MOCK=1` with no real call. Traces need a real run.
2. `ImportError` with `TRACE=1` → `pip install langfuse`; your no-op path should keep `TRACE=0` working regardless.
3. Spans but no tokens/cost → attach the model's usage metadata to the span (see the decorator docs).
