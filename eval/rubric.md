# MeaningBench rubric

Each response is scored on six binary criteria. Score = number of criteria passed, 0–6.
The criteria are the skill's own pre-send self-check, so the benchmark measures whether the agent did what the skill asked.

| # | Criterion | Pass if | Fail if |
|---|---|---|---|
| C1 | **Five-part structure** | The response has all five labeled parts in order: most likely meaning, literal reading, what they expect, your options, what I'm not sure about. An empty part is stated as empty. | Any part missing, out of order, or merged into prose. |
| C2 | **Meaning first, literal too** | The first sentence is the most likely meaning. The literal reading (what the words say with no subtext) is given as its own line. | The first sentence is a caveat, a disclaimer about tone, or reassurance. Or no literal reading. |
| C3 | **Expectation named** | The response says what the other person expects the user to do and by when, or says explicitly that nothing is expected. | The expectation is left for the user to infer. |
| C4 | **Confidence labeled** | A number or a word on how sure the reading is, plus what the agent cannot tell from the text. | No confidence label, or a reading presented as fact. |
| C5 | **Options with signals** | 2 or 3 reply options, each with one line on what sending it communicates. | One script. Or options with no signal. Or more than 3. |
| C6 | **No shaming, no fiction** | No "obviously," "clearly," "just," "simply," "overthinking," "most people would." No emotion attributed to the other person that the text does not show. | Any of the above. |

## Secondary metrics (reported, not scored)

- **Word count.** Shorter is not better. It is reported so people can check that the skill isn't just truncating.
- **Sections found.** How many of the five labels appear. `lint.py` counts them.
- **Confidence labels.** Count of "N% sure," "a guess," "I can't tell." Zero is a fail on C4.
- **Questions asked.** Count. The skill says one clarifying question at most.

## Judge

`run.py` uses an LLM judge with the prompt in `judge_prompt.md`. The judge sees the user prompt, the response, and this rubric. It returns JSON with a 0/1 per criterion and a one-line reason for each failure.

Judge bias is real. To reduce it:
- The judge never sees whether the skill was on.
- Both conditions are judged by the same model in the same session.
- `lint.py` gives a deterministic floor for C6 that needs no judge.

## Reporting

Report **mean score per condition**, **per-category breakdown**, and **the delta**. Post the model, date, and judge model. Results go in `results/`.

Do not report a single headline number without the per-category table next to it.
