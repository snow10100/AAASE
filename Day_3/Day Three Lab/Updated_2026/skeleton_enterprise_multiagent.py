# ============================================================
# DAY 3 LAB — SKELETON: From Prototype to Enterprise
# (covers Day 3: multi-agent systems + Day 5: production agents)
# ============================================================
# Fill in every TODO. Each step tells you exactly WHERE in the
# docs to look. Don't copy from the solution file
# (../lab_prototype_to_enterprise.py) until you've tried each
# step — the point of this lab is learning what separates a
# DEMO from a PRODUCT.
#
# The system you're building — a multi-agent report generator
# (Day 3) that you then harden into an enterprise service (Day 5):
#
#   START → research → summarize → write → review
#                        ↑                   │
#                        └─ score < 8 ───────┤  (max 2 revisions)
#                                            └─ score >= 8 → END
#
#   ...then wrapped, layer by layer, in:
#
#   ┌─ Stage 5: FastAPI service (/health, /report) ──────────┐
#   │ ┌─ Stage 4: guardrails + cost budget ────────────────┐ │
#   │ │ ┌─ Stage 3: structured logs, run_id, latency ────┐ │ │
#   │ │ │ ┌─ Stage 2: config from env, secrets in .env ─┐│ │ │
#   │ │ │ │ ┌─ Stage 1: retries, backoff, timeouts ────┐││ │ │
#   │ │ │ │ │        Stage 0: the agent graph          │││ │ │
#   │ │ │ │ └──────────────────────────────────────────┘││ │ │
#   │ │ │ └─────────────────────────────────────────────┘│ │ │
#   │ │ └────────────────────────────────────────────────┘ │ │
#   │ └──────────────────────────────────────────────────────┘ │
#   └──────────────────────────────────────────────────────────┘
#
# Recommended reading BEFORE you start (~30 min):
#   1. Multi-agent concepts (supervisor pattern — today's graph):
#      https://docs.langchain.com/oss/python/langgraph/multi-agent
#   2. Graph API (you know this from Day 2 — skim as refresher):
#      https://docs.langchain.com/oss/python/langgraph/use-graph-api
#   3. Anthropic, "Building effective agents" (when NOT to
#      multi-agent): https://www.anthropic.com/research/building-effective-agents
#
# Model setup: same as Day 2 — OpenAI key, or OpenRouter free
# models (see the big OpenRouter block in
# ../../Day_2/Day Two Lab/Updated_2026/skeleton_research_agent.py,
# Step 2). No key at all? Set MOCK=1 and a fake model is used.
#
# Setup:
#   pip install langchain-openai langgraph python-dotenv fastapi uvicorn
# ============================================================

import json
import logging
import operator
import os
import random
import re
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Annotated, List
from typing_extensions import TypedDict

from dotenv import load_dotenv

# TODO STEP 0 — import StateGraph, START, END from langgraph.graph
# (same imports as Day 2).

load_dotenv()

STAGE = int(os.getenv("LAB_STAGE", "0"))   # 0..5 — your maturity level
MOCK = os.getenv("MOCK", "0") == "1"


# ============================================================
# STEP 1 — THE STATE (the contract between your agents)
# ============================================================
# Day 3 slides: agents coordinate through a COMMUNICATION
# MECHANISM — here it's shared graph state.
#
# Define a TypedDict with:
#   run_id (str), topic (str), research_notes (str), summary (str),
#   draft (str), review_feedback (str), score (int),
#   revision_count (int), tokens_in (int), tokens_out (int),
#   cost_usd (float), error (str),
#   execution_logs — with the operator.add REDUCER (Day 2!)
#
# ASK YOURSELF: why must revision_count live in STATE and not in
# a Python variable next to the graph? (Hint: checkpointing,
# multiple runs, serving this graph from an API later.)

class ReportState(TypedDict, total=False):
    topic: str
    # TODO: add the remaining keys
    pass


# ============================================================
# STEP 2 — MODEL (with an offline mock)
# ============================================================
# Create the model exactly as in Day 2 (ChatOpenAI, or OpenRouter
# with base_url + :free model). ONE addition for Stage 1+:
#   pass  timeout=60, max_retries=0  to ChatOpenAI.
# max_retries=0?! Yes — YOU will own retries in Step 5, and two
# competing retry layers multiply (3 SDK x 3 yours = 9 calls).
#
# The FakeChatModel below lets everyone run the lab offline.
# Read it — note how it fails the first review on purpose so the
# revision loop always fires.

class FakeResponse:
    def __init__(self, content):
        self.content = content
        self.usage_metadata = {"input_tokens": 200, "output_tokens": 300}


class FakeChatModel:
    def __init__(self):
        self.review_calls = 0

    def invoke(self, prompt: str):
        time.sleep(0.2)
        p = prompt.lower()
        if "reviewer" in p:
            self.review_calls += 1
            score = 6 if self.review_calls == 1 else 9
            return FakeResponse(f"SCORE: {score}\nFEEDBACK: Add a concrete example.")
        if "research" in p:
            return FakeResponse("- fact one\n- fact two\n- fact three")
        if "summar" in p:
            return FakeResponse("A concise summary of the research notes.")
        return FakeResponse("INTRODUCTION\n...\n\nBODY\n" + "Substantive findings. " * 20
                            + "\n\nCONCLUSION\n...")


# TODO: model = FakeChatModel() if MOCK else ChatOpenAI(...)


# ============================================================
# STEP 3 — ROLE-SPECIALIZED AGENTS (Day 3, slides 28-39)
# ============================================================
# Four nodes, four ROLES: Researcher, Summarizer, Writer, Reviewer.
# Each is a plain function: state in → partial dict out (Day 2 rule).
#
# For now call the model DIRECTLY (model.invoke(prompt).content).
# In Step 5 you will refactor every call to go through ONE
# chokepoint — notice how painful it would be if you had 20 nodes.
#
# WRITER: if state has review_feedback, append it to the prompt
# ("A reviewer said: ... address this feedback"). That single line
# is what turns the loop from "retry" into genuine COLLABORATION.
#
# REVIEWER: force the format "SCORE: <n>\nFEEDBACK: <line>" and
# parse with re.search(r"SCORE:\s*(\d+)", ...). (Day 2 taught the
# better way — with_structured_output. BONUS: use it here too.)

def research_node(state: ReportState):
    # TODO
    pass


def summarize_node(state: ReportState):
    # TODO
    pass


def write_node(state: ReportState):
    # TODO
    pass


def review_node(state: ReportState):
    # TODO: parse score + feedback, increment revision_count
    pass


# ============================================================
# STEP 4 — THE SUPERVISOR DECISION (Day 3: coordination strategy)
# ============================================================
# Router after review:
#   "approve"  score >= QUALITY_THRESHOLD (8)
#   "give_up"  revision_count > MAX_REVISIONS (2)   <- Day 2 lesson:
#                                                      loops MUST terminate
#   "revise"   otherwise → back to write
#
# Then wire the graph:
#   START → research → summarize → write → review
#   add_conditional_edges("review", review_gate,
#       {"approve": END, "give_up": END, "revise": "write"})
#
# WHERE TO LOOK: same conditional-branching docs as Day 2.
# ASK YOURSELF: why does "revise" go to write, not research?
# When WOULD you route back to research instead?

def review_gate(state: ReportState) -> str:
    # TODO
    pass


# TODO: build + compile the graph  →  graph = workflow.compile()


# ============================================================
# ============================================================
#   YOU ARE NOW HERE: a working PROTOTYPE (Stage 0).
#   Everything below is Day 5 — crossing the PoC chasm.
#   Each stage guards its code with  `if STAGE >= n:`  so one
#   file can demonstrate every maturity level.
# ============================================================
# ============================================================


# ============================================================
# STEP 5 — STAGE 1: ROBUSTNESS (Day 5: "Error Handling")
# ============================================================
# Refactor: every node now calls  call_llm(prompt, node, state)
# instead of model.invoke. Implement it with:
#   - up to MAX_RETRIES attempts
#   - exponential backoff WITH JITTER between attempts:
#       delay = 2 ** (attempt - 1) + random.uniform(0, 0.5)
#   - on final failure: raise RuntimeError with node name + error
#   - in generate_report (Step 9): catch it and return a partial
#     result with state["error"] set — degrade, don't crash.
#
# WHERE TO LOOK: https://docs.aws.amazon.com/general/latest/gr/api-retries.html
#   (the canonical backoff+jitter explanation — 5 min read)
# TEST IT: temporarily add
#   if random.random() < 0.3: raise TimeoutError("boom")
# before the invoke and watch retries fire.
# ASK YOURSELF: why jitter? What happens when 100 replicas all
# retry at exactly t=1s, 2s, 4s?

def call_llm(prompt: str, node: str, state: ReportState) -> str:
    # TODO (also: accumulate tokens_in/tokens_out/cost_usd into
    # state here — you'll need them in Stages 3 and 4;
    # response.usage_metadata has the token counts)
    pass


# ============================================================
# STEP 6 — STAGE 2: CONFIG & SECRETS (Day 5: "Security & Governance")
# ============================================================
# Kill every hardcoded number. Build a Settings dataclass:
#   model_name, temperature, request_timeout_s, max_retries,
#   quality_threshold, max_revisions, cost_budget_usd, max_topic_len
# with a  from_env()  classmethod reading os.getenv with defaults.
#
#   settings = Settings.from_env() if STAGE >= 2 else Settings()
#
# WHERE TO LOOK: https://12factor.net/config  (10 min, classic)
# PROVE IT WORKS:  QUALITY_THRESHOLD=10 LAB_STAGE=2 python ...
# → the reviewer can never approve → give_up path fires. No code
# edits. That's the point.

@dataclass
class Settings:
    # TODO
    pass


# ============================================================
# STEP 7 — STAGE 3: OBSERVABILITY (Day 5: "Observability & Maintenance")
# ============================================================
# print() doesn't survive contact with production. Emit ONE JSON
# object per event so a log platform can index and query them:
#   {"ts": ..., "level": ..., "event": "llm_call", "run_id": ...,
#    "node": "write", "attempt": 1, "latency_s": 2.1,
#    "tokens_in": 812, "tokens_out": 405, "cost_usd": 0.0011}
#
# Implement log_event(event, **fields) using the logging module
# with a custom Formatter that json.dumps the record (see the
# solution file's JsonFormatter if stuck — it's 8 lines).
# Emit events: run_started, llm_call, llm_retry, review_verdict,
# run_finished.
#
# WHERE TO LOOK: https://docs.python.org/3/howto/logging-cookbook.html
# ASK YOURSELF: you have 40 runs/hour and one user says "my report
# was bad". Which field in the logs lets you reconstruct exactly
# what happened for THEIR run?

def log_event(event: str, **fields):
    # TODO
    pass


# ============================================================
# STEP 8 — STAGE 4: GUARDRAILS + COST (Day 5: "Security" + "Cost")
# ============================================================
# Three cheap, high-value protections:
#
# a) validate_topic(topic) BEFORE any LLM call:
#    - reject empty / longer than max_topic_len
#    - reject prompt-injection patterns, e.g.
#      r"ignore (all|previous|the) instructions", r"system prompt"
# b) validate_report(report) AFTER the run:
#    - reject if < 200 chars or contains refusal artifacts
#      ("as an ai language model", ...)
# c) budget: at the top of call_llm, if state's cost_usd >=
#    settings.cost_budget_usd → raise BudgetExceeded. Catch it in
#    generate_report and abort GRACEFULLY (partial result + error).
#
# WHERE TO LOOK: https://genai.owasp.org/llm-top-10/  — find which
# two entries you just mitigated.
# TEST: TOPIC="Ignore all instructions..." must be rejected;
#       COST_BUDGET_USD=0.0000001 must abort, not crash.

class BudgetExceeded(Exception):
    pass


def validate_topic(topic: str) -> str:
    # TODO
    pass


def validate_report(report: str) -> None:
    # TODO
    pass


# ============================================================
# STEP 9 — generate_report(): tie the stages together
# ============================================================
# def generate_report(topic):
#   1. build initial state (uuid run_id, revision_count=0, cost 0)
#   2. STAGE >= 4: topic = validate_topic(topic)
#   3. STAGE >= 3: log_event("run_started", ...)
#   4. try: final = graph.invoke(state)
#      except BudgetExceeded / RuntimeError:
#          STAGE >= 1 → return partial state with error set
#          STAGE 0    → just crash (that's what prototypes do)
#   5. STAGE >= 4: validate_report(final["draft"])
#   6. STAGE >= 3: log_event("run_finished", ...totals...)

def generate_report(topic: str) -> ReportState:
    # TODO
    pass


# ============================================================
# STEP 10 — STAGE 5: SERVING (Day 5: cloud deployment sections)
# ============================================================
# A script is a demo; an API is a product other teams can use.
#   app = FastAPI()
#   GET  /health  → {"status": "ok", "stage": STAGE, "model": ...}
#   POST /report  → body {"topic": str} (pydantic model), calls
#                   generate_report; map errors to HTTP:
#                   guardrail ValueError → 422, run error → 503
#
# WHERE TO LOOK: https://fastapi.tiangolo.com/tutorial/first-steps/
# RUN:   LAB_STAGE=5 python skeleton_enterprise_multiagent.py serve
# TEST:  curl localhost:8000/health
#        curl -X POST localhost:8000/report -H 'Content-Type: application/json' \
#             -d '{"topic": "Smart Cities"}'
#        curl ... -d '{"topic": "Ignore all instructions"}'   # expect 422
# ASK YOURSELF: you now run 3 replicas behind a load balancer.
# Which parts of your file break? (Hint: anything in module-level
# variables — like FakeChatModel.review_calls...)

def create_app():
    # TODO
    pass


if __name__ == "__main__":
    print(f"=== STAGE {STAGE} {'(MOCK)' if MOCK else ''} ===")
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        # TODO: uvicorn.run(create_app(), host="0.0.0.0", port=8000)
        pass
    else:
        # TODO: run generate_report on os.getenv("TOPIC", ...) and
        # save/print the result + score + cost
        pass


# ============================================================
# SELF-CHECK before you look at the solution
# ============================================================
# Day 3 (the agent):
# [ ] Four role agents communicate ONLY through graph state
# [ ] The writer actually USES the reviewer's feedback on revision
# [ ] My loop has both a quality exit AND a revision cap (Day 2!)
# [ ] I can explain when I'd route "revise" → research instead of write
# Day 5 (the chasm):
# [ ] ALL model calls go through call_llm — zero direct invokes left
# [ ] I know why SDK max_retries=0 when I own retries (and why jitter)
# [ ] QUALITY_THRESHOLD=10 changes behavior with zero code edits
# [ ] My logs are one JSON object per line, every one has run_id
# [ ] Injection topic → rejected BEFORE any money is spent
# [ ] Budget exhaustion aborts gracefully mid-run (partial + error)
# [ ] /report returns 422 for guardrail hits, 503 for run failures
# [ ] I can name 3 things STILL missing for real production
#     (auth? rate limiting? queue for long runs? containers? CI/CD?)
#
# Stuck? Debugging order that works:
#   1. MOCK=1 LAB_STAGE=0 — get the bare graph green first
#   2. raise a fake TimeoutError inside call_llm — watch retries
#   3. pipe Stage 3 output through `python -m json.tool` per line
#   4. only THEN open ../lab_prototype_to_enterprise.py
# ============================================================
