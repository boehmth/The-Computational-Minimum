# Chapter 1 · Text-in / Text-out

**What an LLM really is, from the API side — and what it is *not*.**

Two six-liners that together prove the first principle and at the same time show why we need Chapters 2 through 6.

---

## 📜 Historical context

**1950** — Alan Turing publishes *"Computing Machinery and Intelligence"* and formulates the question: *"Can machines think?"* He doesn't answer it directly, he replaces it with something more precise — the "Imitation Game", known today as the Turing test. The test operationalises intelligence as *linguistic behaviour*: a machine counts as thinking if its text behaviour is indistinguishable from human text behaviour.

That definition is exactly the one today's LLMs satisfy — not because they think (that would be the wrong question), but because their interface with the rest of the world is exactly one: **text in, text out**.

From the symbolic systems of the 1960s (SHRDLU, ELIZA) via the statistical NLP of the 1990s to the transformer models of the 2020s, the format has never changed. What has changed radically is the quality of what happens between input and output.

**2017** — Vaswani et al. publish *"Attention Is All You Need"* — the transformer. From here the line runs unbroken to today: GPT-1 (2018), GPT-2 (2019), GPT-3 (2020), ChatGPT (Nov 2022), GPT-4 / Claude / Gemini (2023–), all the way to the reasoning models of Chapter 4.

**The API contract has stayed the same from the first generation to today**: one prompt goes in, text comes back. Everything we build in the remaining five chapters is code that orchestrates precisely *this one operation* cleverly.

---

## 🔬 The two miniatures

### `src/01_hello_llm.py` — the smallest possible demonstration

A single `chat()` call. The prompt asks for the capital of France. The model answers. The output prints the model name, the token counts, and the answer — nothing more.

**Why this stands alone:** because it lays the foundation the rest of the repo uses. If this script runs for you, you have:
- a working SAP GenAI Hub configuration (or a Gemini fallback),
- the `common/llm.py` wrapper working,
- understood that from the code's point of view an LLM call is nothing more than an HTTP POST with a JSON body.

### `src/02_math_breaks.py` — the motivation for everything that follows

Same API contract, but now a task the model *cannot* solve: the product of two five-digit numbers (`43,177 × 14,694`).

The model answers with a plausible number. Python computes the truth alongside. The script shows both and the difference.

**What is happening here:** the model has learned to produce plausible sequences of digits — it predicts the *most likely next digit* character by character. It has not learned to multiply. The answer has roughly the right number of digits and often starts with the correct leading digits (the order of magnitude is right), but the middle and late digits are noise.

---

## 💡 Wow moment

The model produces numbers like `634,297,038` or `6,343,522,638` or `633,942,838`. The true value is `634,442,838`.

Sometimes the error is small (less than one percent). Sometimes it is large (a factor of 10, because one extra digit slipped in). Running the call repeatedly you see: every run gives a *different* wrong answer. There is no "correct" result stored in the model's weights — there is only a probability distribution over the next digit.

This is the pedagogical anchor for everything that follows: **if you need a deterministic computation, you need a deterministic compute engine — not the model.**

But the model *knows* it needs to multiply. It reads the prompt correctly. It identifies the operation. It just doesn't produce the correct result. Precisely this separation — *the model understands the task, but the execution belongs elsewhere* — is the central insight from which Chapter 2 grows.

---

## 🚀 Run it

Prerequisite: `.env` in the `RPT Agent` root is filled in (see `../../.env.example`).

```powershell
cd "C:\Users\<USERNAME>\Source\RPT Agent"
python "Agentic Systems/01_TextInTextOut/src/01_hello_llm.py"
python "Agentic Systems/01_TextInTextOut/src/02_math_breaks.py"
```

Expected output from `02_math_breaks.py` (your exact numbers will vary — that is the point):

```
┌── THE TASK ─────────────────────────────────────────────────────
│  Was ist 43,177 × 14,694?  Antworte NUR mit der Zahl.
└─────────────────────────────────────────────────────────────────

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ▸  THE MODEL guesses (predict-next-token)                     ┃
┃     6 tokens · gpt-4o                                          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  634,367.038                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ▸  PYTHON computes (deterministic)                            ┃
┃     0 tokens · Python multiplication                           ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  634,442,838                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌── DIFFERENCE ────────────────────────────────────────────────────
│  Model − Python   =   -75,800
│  Error percent    =   -0.0119 %
│
│  Interpretation: the order of magnitude is right, middle digits
│  are wrong. The model understood the task — it did not execute it.
└──────────────────────────────────────────────────────────────────
```

(Script labels themselves are in German; the frame here shows the pedagogical point in English.)

---

## 🧭 Bridge to the next chapter

If you have run these two scripts you have two things:

1. **Confidence** in the infrastructure (`common/llm.py` works for you).
2. **A question** which Chapter 2 answers: *how do we get from "the model knows what needs to be done" to "the correct result"?*

The answer: give the model a tool. Not so it computes — but so it *says* what should be computed, and the deterministic part outside the model does the actual computation.

That is Chapter 2.