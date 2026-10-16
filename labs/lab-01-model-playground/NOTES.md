# Lab 1: Model Behaviour Playground — Notes

## 1.1 Build a Token and Context Window Inspector

**Question this answered:** What does the model actually see when it reads text — and why does that make letter-counting unreliable?

**What I built**
- [`token_inspector.py`](experiments/token_inspector.py) — takes a text file, reports word count, token count (via `client.messages.count_tokens`), tokens-per-word ratio, and an input-cost estimate at Sonnet 5.5 pricing. An optional `--find-outlier` flag finds the single word with the highest token count, at the cost of one extra `count_tokens` call per unique word.
- Two sample inputs pulled from `data/reviews.csv`: [`results/sample_review.txt`](results/sample_review.txt) (one review) and [`results/all_reviews.txt`](results/all_reviews.txt) (all 500, concatenated).
- A break-test input, [`results/break_test_5000words.txt`](results/break_test_5000words.txt): 5,000 words from the review corpus with one target word inserted in the middle, used for the Destructive Testing step below.

**How it works**
- **Token counting:** `client.messages.count_tokens` runs the tokenizer step only — no model inference, so it's free. This is distinct from `messages.create`, which does full inference and bills for both input and output tokens.
- **Why tokens ≠ words:** the tokenizer was trained with byte-pair encoding (BPE) on a corpus dominated by English. BPE repeatedly merges the most frequent adjacent character/byte pairs into single tokens, so common English words and fragments ("the", "-ing", "-tion") were merged all the way up into one token each. Text the tokenizer saw rarely — romanized Hindi, unusual punctuation glued to a word — never earned those merges, so it falls back to small subword or near-character fragments. More fragments per word = higher cost and more context-window usage for the same information.
- **Cost accounting:** cost is `tokens × price-per-token`. Using `count_tokens` lets you estimate spend before ever calling `messages.create`.
- **How the model finds one target word in 5,000 words (attention, not search):** the model doesn't scan the input left-to-right looking for a match. The whole input is processed in one pass. For every output position it's about to generate, each input position holds a "key" (what this token is) and a "value" (its content); the position about to generate holds a "query" (what it's looking for right now). The query gets compared against every key simultaneously, producing a relevance score per input position; those scores are turned into weights (summing to 100%, via softmax), and the output is built from a weighted blend of every input position's value, weighted by those scores. "Looking back at every input position" means exactly that — nothing is skipped, and position in the sequence (start, middle, end) doesn't matter the way it would in a left-to-right scan. In this test, the query built from the question ("what word is being asked about?") scores highest against the input position holding the target word, among the other 5,000, so that position dominates the blend feeding the answer — which looks like "finding" the word but is really one large weighted comparison done via matrix multiplication, not a loop.

**Results**
| Input | Words | Tokens | Tokens/word | Est. input cost (Sonnet 5.5) |
|---|---|---|---|---|
| [One review, code-mixed English/Hindi](results/sample_review.txt) | 57 | 150 | 2.63 | $0.000300 |
| [All 500 reviews](results/all_reviews.txt) | 25,806 | 47,866 | 1.85 | $0.095732 |

- Highest-token word found in the single-review run (`--find-outlier`): `'dikhaya.'` → **14 tokens** for one word. It's a romanized Hindi word with punctuation stuck to it, so the tokenizer had no learned merge for it and fell back to small fragments.
- The all-corpus ratio (1.85) is lower than the single review's (2.63) because most of the 500 reviews are plain English, where tokens run close to ~0.75–1 per word; the one code-mixed review was an outlier dragging its own ratio up.

**Predicted vs. actual**
- **Predicted** (2026-10-17, before running): I am not sure but model does not read the text 'r' but rather reads the tokens so it may be need to reverse the token to convert it to letter r for it to answer it
- **Actual:** Mixed, in an informative way. Four variants of the break test, all on [`results/break_test_5000words.txt`](results/break_test_5000words.txt) (5,000 words with a target word inserted):
  1. **"strawberry", free-form answer:** correct (3 r's). The model visibly spelled the word out (`s-t-r-a-w-b-e-r-r-y`) before counting.
  2. **"strawberry", forced to a single digit, no spelling allowed, tiny `max_tokens`:** still correct, with zero spelling and zero visible reasoning (`thinking_tokens: 0`). This is a confound, not a counterexample — see Gotchas.
  3. **"entrepreneurial" (not an internet-famous example), forced to a single digit, `max_tokens=5`:** broke. Output was cut off mid-spelling (`e-n-t`), because the model disobeyed the "no spelling" instruction and tried to spell the word anyway, but ran out of token budget before finishing.
  4. **Same word and instruction, `max_tokens=60`:** the model again ignored "no spelling," spelled `e-n-t-r-e-p-r-e-n-e-u-r-i-a-l` in full, marked the r positions, and answered correctly (3).
- **Why:** The prediction's mechanism was right — the model never reads individual letters, only opaque token IDs — but the first break-test attempt didn't actually prove it, because "strawberry" has become so internet-famous as a letter-counting trap that the fact "strawberry has 3 r's" is very likely memorized directly from training data discussing that meme, independent of any token reasoning. Swapping to a non-meme word ("entrepreneurial") and constraining output length is what actually exposed the real mechanism: the model's only reliable way to count letters is to regenerate the word as new output text, split onto individual characters (e.g. via hyphens), because that regenerated form happens to tokenize at roughly one-token-per-letter — unlike the original word, which is one or two opaque multi-letter tokens. Cut off the room for that regeneration, and the answer breaks, not by guessing wrong but by being truncated mid-recovery.

**Gotchas**
- "Strawberry" is a bad test word for this exercise now — it's too famous as an AI-can't-count meme, so a correct answer under a no-reasoning constraint doesn't prove the model computed anything; it may have memorized the specific fact. Use an uncommon real word with repeated letters instead (we used "entrepreneurial") to separate memorization from actual counting behavior.
- `thinking: {"type": "between_tools"}` suppresses visible reasoning but does not stop the model from "thinking out loud" directly in its answer text (spelling the word out) when it needs to — it just means that spelling happens in the visible output, consuming regular output tokens, instead of in a separate thinking block.
- A tiny `max_tokens` doesn't make a model answer more concisely — it can truncate a reasoning strategy mid-way and produce a broken, partial answer instead of a wrong-but-complete one.

**Remember**
- `count_tokens` is free (no inference) and billed separately from `messages.create` (full inference, bills input + output). Use it to estimate cost before spending anything.
- Tokens-per-word for plain English runs under 1; code-mixed or unusual text can run 2–3× higher per word, inflating cost and context-window usage for the same content.
- A model cannot inspect the letters "inside" one of its own tokens — a token is an opaque ID to it. Its only reliable strategy for letter-level tasks is to regenerate the word as new text that happens to tokenize closer to one-letter-per-token (e.g. by spelling it with separators), then count over that new sequence.
- A model will override an explicit "don't show your reasoning" instruction when the task genuinely requires that reasoning to succeed (here: spelling before counting) — unless you also remove its room to do so, in which case it fails visibly rather than silently.
- Famous "gotcha" examples (like "strawberry") make bad break tests on current models, because the "failure" may have been patched by memorizing the specific fact rather than by the model getting better at the underlying mechanism.

**Commands**
```bash
# run the inspector on any text file
uv run python labs/lab-01-model-playground/experiments/token_inspector.py <path-to-file.txt>

# also find the single highest-token word (one extra API call per unique word — small inputs only)
uv run python labs/lab-01-model-playground/experiments/token_inspector.py <path-to-file.txt> --find-outlier
```
