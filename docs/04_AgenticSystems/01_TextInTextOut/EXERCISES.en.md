# Exercises · Chapter 1

Three exercises. Each forces you to vary the miniature — and that is the only way to actually understand the point.

---

## Exercise 1 · How small is "small"?

`01_hello_llm.py` is about 25 lines — most of them bootstrap (import path, dotenv). The actual useful code is a single call.

**Task:** Build a *single* script `hello_smallest.py` that makes an LLM call and prints the answer in **at most ten lines** (blank lines and comments do not count). If you use `common/llm.py`, this is easy. If you go directly against the SAP GenAI Hub API, this is *hard* — you will have to implement OAuth, deployment lookup, and JSON parsing yourself.

**What you learn:** how much infrastructure sits under the `chat()` one-liner.

**Bonus:** Try to do the whole thing in **a single line of Python**. (Hint: with `requests.post(...).json()["choices"][0]["message"]["content"]` and a valid bearer token in `AUTHORIZATION` as an environment variable it works. But the token has to be fetched beforehand — that is the trick.)

---

## Exercise 2 · How often is the model wrong?

`02_math_breaks.py` makes a single call. But the model answers slightly differently on every call — we don't see that because we only show one run.

**Task:** Modify `02_math_breaks.py` so that it asks the same question **20 times** (with `temperature=0.7` instead of the default) and then prints a distribution:

- How many answers were *exactly* right?
- How many had the right number of digits but wrong digits?
- How many had the wrong number of digits?
- What was the maximum absolute error? The minimum?

**What you learn:** the *distribution* of the model's answers, not just one instance. That is the perspective from which Chapter 6 talks about determinism.

**Bonus:** Draw an ASCII histogram of the error magnitudes. Where is the median? What is the mode?

---

## Exercise 3 · Where does the "text-in / text-out" rule break?

We claimed: an LLM only knows text-in and text-out. But modern models accept images as input, and the multimodal extensions from OpenAI and Anthropic accept `{"type": "image", "source": {...}}` in the same `messages` structure.

**Task:** Look up in the Anthropic or OpenAI API docs how an image is encoded in a `messages` array. Write into a new file `notes/multimodal.md`:

1. In what format does the image go into the request? (Base64? URL? Bytes?)
2. What does the model do with the image on the server side? (Hint: vision models project image patches through a vision encoder into the same vector space as text tokens.)
3. **Argument question:** does multimodality really violate the "text-in / text-out" principle? Or is it just an extension — "bytes-in / text-out"?

**What you learn:** that "text-in / text-out" is not to be taken literally. The principle actually means *"structured token sequence in / structured token sequence out"*. Text is just the most common instantiation. The output almost always remains text.

**Bonus:** Where does the principle really end? Look up "audio LLM" (e.g., Whisper + GPT-4o) or "action LLM" (e.g., robotics models like RT-2). What breaks there?

---

## How you know you have understood this chapter

If you can explain to a non-technical colleague in **one sentence** why ChatGPT is wrong on `43,177 × 14,694` — and in **a second sentence** what one does about it — you're done with Chapter 1.

The second sentence is Chapter 2.