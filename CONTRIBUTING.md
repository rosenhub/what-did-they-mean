# Contributing

## Proposing a rule change

Open an issue using the **Rule proposal** template. It asks for three things:

1. A real before/after pair. Real means you pasted a real message to an actual agent and saw the "before."
2. One sentence on who it helps.
3. Which existing rule it changes, or where it goes if it is new.

Autistic contributors: your experience is the evidence. "This translation told me I should have known, and here is the line that did it" is a complete argument. You do not need a study.

Rules are capped at 12. A new rule has to replace or merge into an existing one. This keeps the skill short enough that every host loads it in full.

## Adding a host

Open a PR that adds a row to the table in README.md and, if the host has a standard path, a line in `install.sh`. Include a link to the host's docs for the path.

## Benchmark results

Run `eval/run.py`, then open a PR that adds the generated `results/<model>-<date>.md` and a row in `results/README.md`. Say which judge model you used. Results from models other than the one the maintainer tested are the most useful.

## Adding prompts

`eval/prompts.jsonl` is 48 real-shaped messages in 8 categories. A new prompt has to be a message a person could actually receive, with the question the user would actually ask. Replace a weak one; do not grow the file.

## Translations

`README.<lang>.md`, kept to the first screen plus the 12-rule table. Link it from the language bar at the top of README.md. Translating SKILL.md itself is welcome as `SKILL.<lang>.md`; the English file stays canonical. Note that politeness formulas differ by language; a translated SKILL.md should swap the examples in rule 9 for ones that exist in that language.

## What will not be merged

- Rules that make the agent decide for the user. It gives options. See "What this is not" in SKILL.md.
- Rules that frame neurotypical subtext as the correct way to communicate and the user as the one who needs fixing.
- Anything that adds code to the install path. The skill is a markdown file. The installer is a shell script. That's it.
