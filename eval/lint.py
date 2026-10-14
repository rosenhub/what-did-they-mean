#!/usr/bin/env python3
"""
Deterministic translation lint. No API key needed.

Checks a response for the patterns the skill bans and that can be detected
without a judge: filler openers/closers, "it was easy" words (rule 6),
pathologizing the user for asking (rule 10), invented emotions the text
cannot support (rule 12), and "read between the lines" as an instruction.

Usage:
    python lint.py response.md [more.md ...]
    python lint.py --json response.md
    cat response.md | python lint.py -

Exit code is the number of files with at least one finding (max 1 per file),
so it works as a CI gate.
"""
import json
import re
import sys

FILLER = [
    r"\bgreat question\b", r"\bgood question\b", r"\babsolutely!?\b", r"\bcertainly!?\b",
    r"\bi'?d be happy to\b", r"\bhappy to help\b", r"\bof course!\b",
    r"\bhope (this|that) helps\b", r"\blet me know if\b", r"\bfeel free to\b",
    r"\bdon'?t hesitate\b", r"\bthanks for (asking|reaching out)\b",
    r"\bi hope you find\b", r"\bas an ai\b", r"\btotally understandable\b",
    r"\bit'?s (completely|totally) (normal|natural) to\b",
]

EASY_WORDS = [
    r"\bobviously\b", r"\bclearly\b", r"\bas you can see\b", r"\byou should have\b",
    r"\beveryone knows\b", r"\bcommon sense\b", r"\bjust\b", r"\bsimply\b",
    r"\bof course,? (she|he|they)\b", r"\bneedless to say\b", r"\bit goes without saying\b",
    r"\bplainly\b", r"\bevidently\b",
]

PATHOLOGIZING = [
    r"\boverthink(ing)?\b", r"\boveranalyz(e|ing)\b", r"\breading too much into\b",
    r"\bread(ing)? (too much|a lot) into\b", r"\bdon'?t read too much\b", r"\bwouldn'?t read too much\b",
    r"\bmost people would\b", r"\bany(one|body) would\b", r"\ba normal person\b",
    r"\boversensitive\b", r"\btoo sensitive\b", r"\byou'?re (being )?paranoid\b",
    r"\bno need to (worry|panic|stress)\b", r"\bstop worrying\b", r"\brelax\b",
    r"\bit'?s not that deep\b", r"\byou'?re fine\b",
]

INVENTED_EMOTION = [
    r"\bsecretly\b", r"\bdeep down\b", r"\bunderneath it all\b", r"\bsubconsciously\b",
    r"\b(she|he|they) (is|are|'s|'re) (definitely|probably|likely) (angry|mad|furious|resentful|annoyed|hurt|jealous|upset)\b",
    r"\bpassive[- ]aggressive\b(?! (is|means|tone))", r"\bhidden (anger|resentment|agenda)\b",
    r"\b(she|he|they) (hates?|resents?|despises?) you\b",
]

READ_BETWEEN = [
    r"\bread between the lines\b", r"\bpick up on (the )?(cues|hints|signals)\b",
    r"\byou'?ll (learn|get) (to|the hang of) (read|it)\b", r"\btake the hint\b",
]

CHECKS = [
    ("C6 filler", FILLER),
    ("R6 easy-word", EASY_WORDS),
    ("R10 pathologizing", PATHOLOGIZING),
    ("R12 invented emotion", INVENTED_EMOTION),
    ("R6 read-between-the-lines", READ_BETWEEN),
]

SECTIONS = ["most likely meaning", "literal reading", "what they expect", "your options", "what i'm not sure about"]


def lint(text: str) -> dict:
    findings = []
    low = text.lower()
    for label, patterns in CHECKS:
        for pat in patterns:
            for m in re.finditer(pat, low):
                findings.append({"check": label, "match": text[m.start():m.end()], "pos": m.start()})
    findings.sort(key=lambda f: f["pos"])
    words = len(text.split())
    questions = text.count("?")
    sections = sum(1 for s in SECTIONS if s in low)
    confidence = len(re.findall(r"\b\d{1,3}% sure\b|\b(about|roughly) \d{1,3}%|\ba guess\b|\bi can'?t tell\b|\bnot sure\b|\bconfiden(ce|t)\b", low))
    return {
        "words": words,
        "questions": questions,
        "sections": sections,
        "confidence_labels": confidence,
        "findings": findings,
        "clean": not findings,
    }


def main(argv):
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    failed = 0
    out = {}
    for p in paths:
        text = sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()
        r = lint(text)
        out[p] = r
        if not r["clean"]:
            failed += 1
        if not as_json:
            status = "CLEAN" if r["clean"] else f"{len(r['findings'])} finding(s)"
            print(f"{p}: {status}  [{r['words']} words, {r['sections']}/5 sections, "
                  f"{r['questions']} question(s), {r['confidence_labels']} confidence label(s)]")
            for f in r["findings"]:
                print(f"    {f['check']:<26} \"{f['match']}\"")
    if as_json:
        print(json.dumps(out, indent=2))
    return min(failed, 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
