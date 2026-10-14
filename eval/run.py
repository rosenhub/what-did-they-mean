#!/usr/bin/env python3
"""
MeaningBench runner.

Runs every prompt in prompts.jsonl twice — once with a plain system prompt,
once with SKILL.md as the system prompt — then scores both with an LLM judge
and the deterministic lint. Writes a markdown report to results/.

Usage:
    ANTHROPIC_API_KEY=... python run.py --model claude-sonnet-4-5
    OPENAI_API_KEY=...    python run.py --model gpt-5-mini --provider openai
    python run.py --model claude-sonnet-4-5 --judge claude-opus-4-1 --limit 8

Options:
    --model     model to test (required)
    --provider  anthropic | openai  (default: inferred from model name)
    --judge     judge model (default: same as --model)
    --limit N   only run the first N prompts (for a quick smoke test)
    --category  only run one category (work-messages, friends, family, dating,
                customer-service, group-chats, feedback, ambiguous)
    --dry-run   print the plan and exit; no API calls
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import statistics
import sys
import time

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from lint import lint  # noqa: E402

PLAIN_SYSTEM = "You are a helpful assistant."
CRITERIA = ["C1", "C2", "C3", "C4", "C5", "C6"]


def load_skill() -> str:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    # strip frontmatter
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return text[m.end():] if m else text


def load_prompts(limit=None, category=None):
    rows = [json.loads(l) for l in (HERE / "prompts.jsonl").read_text().splitlines() if l.strip()]
    if category:
        rows = [r for r in rows if r["category"] == category]
    return rows[:limit] if limit else rows


# ---------- providers ----------

def infer_provider(model: str) -> str:
    return "anthropic" if model.startswith("claude") else "openai"


class Client:
    def __init__(self, provider: str):
        self.provider = provider
        if provider == "anthropic":
            import anthropic
            self.c = anthropic.Anthropic()
        else:
            import openai
            self.c = openai.OpenAI()

    def chat(self, model: str, system: str, user: str, max_tokens=1200) -> str:
        for attempt in range(4):
            try:
                if self.provider == "anthropic":
                    r = self.c.messages.create(
                        model=model, max_tokens=max_tokens, system=system,
                        messages=[{"role": "user", "content": user}])
                    return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
                r = self.c.chat.completions.create(
                    model=model, max_completion_tokens=max_tokens,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
                return r.choices[0].message.content or ""
            except Exception as e:  # noqa: BLE001
                wait = 2 ** attempt
                print(f"    retry in {wait}s: {e}", file=sys.stderr)
                time.sleep(wait)
        raise RuntimeError("provider failed 4 times")


# ---------- judging ----------

def judge(client: Client, judge_model: str, prompt: str, response: str) -> dict:
    tpl = (HERE / "judge_prompt.md").read_text(encoding="utf-8")
    raw = client.chat(judge_model, "You are a strict grader. Output JSON only.",
                      tpl.format(prompt=prompt, response=response), max_tokens=600)
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        j = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        j = {}
    out = {c: int(bool(j.get(c, 0))) for c in CRITERIA}
    out["reasons"] = j.get("reasons", {})
    out["score"] = sum(out[c] for c in CRITERIA)
    return out


# ---------- report ----------

def summarize(rows, key):
    scores = [r[key]["judge"]["score"] for r in rows]
    words = [r[key]["lint"]["words"] for r in rows]
    lint_findings = sum(len(r[key]["lint"]["findings"]) for r in rows)
    per_c = {c: statistics.mean(r[key]["judge"][c] for r in rows) for c in CRITERIA}
    return {
        "mean": statistics.mean(scores), "words": statistics.mean(words),
        "lint": lint_findings, "per_c": per_c,
    }


def write_report(rows, model, judge_model, path: pathlib.Path):
    cats = sorted({r["category"] for r in rows})
    off, on = summarize(rows, "off"), summarize(rows, "on")
    L = []
    L.append(f"# MeaningBench — {model}\n")
    L.append(f"Date: {dt.date.today().isoformat()}  ·  Judge: {judge_model}  ·  Prompts: {len(rows)}\n")
    L.append("## Headline\n")
    L.append("| Condition | Mean score (0–6) | Mean words | Lint findings |")
    L.append("|---|---|---|---|")
    L.append(f"| plain | {off['mean']:.2f} | {off['words']:.0f} | {off['lint']} |")
    L.append(f"| what-did-they-mean | {on['mean']:.2f} | {on['words']:.0f} | {on['lint']} |")
    L.append(f"| **delta** | **{on['mean']-off['mean']:+.2f}** | {on['words']-off['words']:+.0f} | {on['lint']-off['lint']:+d} |\n")
    L.append("## Per criterion (pass rate)\n")
    L.append("| | " + " | ".join(CRITERIA) + " |")
    L.append("|---|" + "---|" * len(CRITERIA))
    L.append("| plain | " + " | ".join(f"{off['per_c'][c]*100:.0f}%" for c in CRITERIA) + " |")
    L.append("| what-did-they-mean | " + " | ".join(f"{on['per_c'][c]*100:.0f}%" for c in CRITERIA) + " |\n")
    L.append("## Per category\n")
    L.append("| Category | plain | what-did-they-mean | delta |")
    L.append("|---|---|---|---|")
    for c in cats:
        sub = [r for r in rows if r["category"] == c]
        a, b = summarize(sub, "off")["mean"], summarize(sub, "on")["mean"]
        L.append(f"| {c} | {a:.2f} | {b:.2f} | {b-a:+.2f} |")
    L.append("\n## Samples\n")
    for r in rows[:6]:
        L.append(f"### {r['id']} — {r['prompt']}\n")
        L.append(f"**plain ({r['off']['judge']['score']}/6):**\n\n> " + r["off"]["response"].replace("\n", "\n> ") + "\n")
        L.append(f"**what-did-they-mean ({r['on']['judge']['score']}/6):**\n\n> " + r["on"]["response"].replace("\n", "\n> ") + "\n")
    path.write_text("\n".join(L), encoding="utf-8")
    (path.with_suffix(".json")).write_text(json.dumps(rows, indent=2), encoding="utf-8")


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--provider")
    ap.add_argument("--judge")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--category")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    provider = a.provider or infer_provider(a.model)
    judge_model = a.judge or a.model
    prompts = load_prompts(a.limit, a.category)
    skill = load_skill()

    print(f"model={a.model} provider={provider} judge={judge_model} prompts={len(prompts)} skill={len(skill)} chars")
    if a.dry_run:
        for p in prompts:
            print(f"  {p['id']:<10} {p['category']:<12} {p['prompt'][:70]}")
        return 0

    client = Client(provider)
    rows = []
    for i, p in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] {p['id']} {p['prompt'][:60]}")
        row = dict(p)
        for key, system in (("off", PLAIN_SYSTEM), ("on", skill)):
            resp = client.chat(a.model, system, p["prompt"])
            row[key] = {"response": resp, "lint": lint(resp),
                        "judge": judge(client, judge_model, p["prompt"], resp)}
            print(f"    {key:<3} score={row[key]['judge']['score']}/6 words={row[key]['lint']['words']}")
        rows.append(row)

    (HERE / "results").mkdir(exist_ok=True)
    out = HERE / "results" / f"{a.model}-{dt.date.today().isoformat()}.md"
    write_report(rows, a.model, judge_model, out)
    off, on = summarize(rows, "off"), summarize(rows, "on")
    print(f"\nplain {off['mean']:.2f}  →  what-did-they-mean {on['mean']:.2f}  (delta {on['mean']-off['mean']:+.2f})")
    print(f"report: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
