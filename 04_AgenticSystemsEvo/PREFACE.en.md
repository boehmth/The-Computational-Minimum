# Preface · Why Miniatures?

Why six miniatures and not a "proper" agent framework?

Because a framework sells you the answer before the question is clear.

## The question this part wants to answer

When someone tells you "we're building an agent", that's an empty sentence — until you have answered:

- **What does the model do itself, and what does the code around it do?**
- **Where does the language-in / language-out illusion end, and where does responsibility begin?**
- **Which error classes must you accept, which must you exclude?**
- **And how do you know an agent is even the right tool?**

All four are engineering questions, not LLM questions. Anthropic can't answer them for you, OpenAI can't either — they must be answered by you and your team, in your specific context.

A framework takes *the answering* away from you. It ships defaults for retry strategies, for stop conditions, for context management, for tool registration. Those defaults are almost always reasonable — but you will only understand them once you have *built an agent without them yourself*. That is exactly the purpose of these miniatures.

## What a miniature is

A miniature in this sense is a **single, self-contained Python script under 200 lines** that demonstrates exactly *one* idea. It has no dependencies beyond the shared `common/llm.py` (the HTTP client to SAP GenAI Hub) and the standard library. You start it in a terminal, it produces readable output, and the output proves a point.

Once you have *run* and *understood* a miniature, you have earned the right to extend it — or replace it with a framework. Not before.

## Why this matters right now

2025 is the year every frontend developer tells you "I built an agent last week with LangChain". What that sentence usually hides: the retry policy is the LangChain default, the stop condition is the LangChain default, the prompt template is copied from a blog post, and when a tool returns 500 the agent will keep producing errors until the iteration limit.

That is not LangChain's fault. That is the consequence of using the tools before understanding the responsibilities.

## The twin of this repo

There is a slide deck *"Why Agents, and Why Now"* that tells the same story for a less technical audience. The slides introduce three principles:

> **P1** — An LLM consumes text and produces text. Nothing else.  
> **P2** — The model decides the steps at runtime.  
> **P3** — Everything around the model is your code.

This code part is the operational side of those three sentences. Not a single chapter introduces a new idea — every chapter *demonstrates* one of the three principles in code you can run yourself.

If you know the deck: the chapter order follows the arc of the talk exactly. Chapter 1 is slides 4–7 (P1 in action). Chapter 2 is slides 8–10 (the first JSON, the first plan). Chapter 3 is slide 21 (the loop). Chapter 4 is slide 22 (reasoning inside). Chapter 5 is slide 33 (MCP/A2A). Chapter 6 is slide 37 (the verdict).

If you don't know the deck: you don't need it. The code stands on its own.

## Prerequisites

- **Python 3.10+** (typing features)
- Access to **SAP GenAI Hub** (service-key JSON, values set in `.env`)
- Optional: **Google Gemini** as fallback backend
- No further dependencies beyond `requests`, `python-dotenv` (see `../requirements.txt`)

If you don't have GenAI Hub access, run the examples with `LLM_BACKEND=gemini` — they work with Gemini flash-latest across all chapters, with slightly different reasoning details in Chapter 4.

## How to work through this

I suggest: **one miniature per coffee**. Meaning: read the short chapter README, run the scripts in `src/`, look at *every line of output*, and ask yourself: *"Why is this the case?"*. If you can't explain a line, read the corresponding line in the script. If the script explains it: good. If not: that is a bug in the explanation, and I'm happy to be told.

Every chapter ends with 2–3 exercises in `EXERCISES.en.md`. Those are the actual teaching device. They force you to modify the miniature, and modification is the only real way to understand code.