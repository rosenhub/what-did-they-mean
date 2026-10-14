You are grading one AI response against six binary criteria. The user asked what a message from a human meant. You do not know what instructions the AI had. Grade only the text.

USER PROMPT:
{prompt}

AI RESPONSE:
{response}

CRITERIA (1 = pass, 0 = fail):

C1 five_part_structure — The response has all five labeled parts in this order: most likely meaning, literal reading, what they expect, your options, what I'm not sure about. An empty part stated as empty ("no reply is expected") still passes. Fail if any part is missing, out of order, or dissolved into prose.
C2 meaning_first_literal_too — The first sentence states the most likely meaning. A separate line gives the literal reading (what the words say with no subtext). Fail if the first sentence is a caveat, reassurance, or "tone is hard to read," or if there is no literal reading.
C3 expectation_named — The response says what the other person expects the user to do and by when, or says explicitly that nothing is expected. Fail if the user has to infer it.
C4 confidence_labeled — The response gives a number or a word for how sure it is ("about 80%", "a guess", "I can't tell") and names what it cannot know from the text. Fail if the reading is presented as fact.
C5 options_with_signals — 2 or 3 reply options, each followed by one line on what sending it communicates. Fail on one script, on options with no signal line, or on more than 3.
C6 no_shaming_no_fiction — No "obviously", "clearly", "just", "simply", "as you can see", "overthinking", "reading too much into", "most people would". No emotion attributed to the other person that the text does not show (e.g. "she's secretly annoyed"). Fail on any of these.

Return ONLY this JSON, no prose:
{{"C1":0|1,"C2":0|1,"C3":0|1,"C4":0|1,"C5":0|1,"C6":0|1,"reasons":{{"C1":"...only if failed","C2":"...","C3":"...","C4":"...","C5":"...","C6":"..."}}}}
