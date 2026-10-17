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

## 1.2 Run a Temperature and Non-Determinism Experiment

**Question this answered:** Does `temperature=0` guarantee identical output, and what does raising it to `1.0` actually change?

**What I built**
- [`temperature_experiment.py`](experiments/temperature_experiment.py) — classifies one review into the fixed 8-theme list (`data/SPEC.md` §6) at a given temperature, `n` times, and reports distinct outputs and agreement rate. A `--reasoning` flag lets the model write a short explanation before its final answer (parsed by taking the last theme id it mentions), which gives per-token sampling noise more steps to compound into a different final answer.

**How it works**
- **`temperature` is gone from the SDK's typed interface on current-generation thinking-by-default models** — confirmed directly: `client.messages.create(..., temperature=...)` raised `TypeError: unexpected keyword argument 'temperature'` on `anthropic` 1.13.0, for every model, not just Sonnet. Sonnet 5.5 / Opus 5.5 / Fable 5.1 / Haiku 5.5 run adaptive thinking by default and reject a non-default `temperature` (400) while thinking is active — "effort" replaced manual sampling control as the main dial on those models. **This is not true everywhere** — it's specific to models with thinking on by default. **Claude Haiku 4.5** has no thinking by default and still accepts `temperature` normally, so that's the model this whole experiment runs on (see the comment above `MODEL` in the script). Passed via `extra_body={"temperature": ...}` since the typed parameter doesn't exist even for Haiku 4.5 in this SDK version — the server still accepts it as a raw field.
- **Why this matters going forward:** temperature isn't "retired" as a concept — a future lab or production system that deliberately wants direct sampling control (not thinking-mediated behavior) needs to pick a model where it's still live, like Haiku 4.5, or an older Sonnet/Opus generation. Don't carry forward an assumption that temperature is universally unavailable; it's model-specific.
- **Temperature controls how broadly the model samples from its own probability distribution over the next token** — `0` effectively always takes the single most likely token (greedy decoding); `1.0` samples more broadly, letting lower-probability tokens through sometimes. It doesn't invent uncertainty that isn't there: if the model's own distribution is extremely peaked (one token at ~99.99%), raising temperature barely changes behavior in practice, because that token still gets sampled almost every time.
- **Short categorical answers hide temperature's effect.** With the prompt instructing "answer with only the theme id, nothing else," the output collapses to a handful of tokens, and instruction-tuned models tend to be very decisive on short classification answers regardless of nominal temperature. Confirmed directly: raw output text varied in wording across 5 runs at `temperature=1.0` (proving sampling was genuinely active), but the final theme was identical every time for several prompts we tried. Allowing the model to reason first (`--reasoning`) gives sampling noise more tokens to compound over, which is what eventually surfaced real disagreement.

**Results**
| Review | Temp | Distinct outputs | Most common | Agreement | Source |
|---|---|---|---|---|---|
| Clear-cut (`delivery_delay`, review #29) | 0.0 | 1 | delivery_delay | 100% | [results/temp_experiment_clearcut.txt](results/temp_experiment_clearcut.txt) |
| Clear-cut (`delivery_delay`, review #29) | 1.0 | 1 | delivery_delay | 100% | [results/temp_experiment_clearcut.txt](results/temp_experiment_clearcut.txt) |
| "Ambiguous" (review #6, spans 3 themes) | 0.0 | 1 | damaged_on_arrival | 100% | [results/temp_experiment_ambiguous.txt](results/temp_experiment_ambiguous.txt) |
| "Ambiguous" (review #6, spans 3 themes) | 1.0 | 1 | damaged_on_arrival | 100% | [results/temp_experiment_ambiguous.txt](results/temp_experiment_ambiguous.txt) |
| Deliberately balanced (ease_of_use vs. value_for_money) | 0.0 / 1.0 | 1 / 1 | value_for_money | 100% / 100% | [results/temp_experiment_balanced.txt](results/temp_experiment_balanced.txt) |
| Parallel severity (delivery_delay vs. product_defect) | 0.0 / 1.0 | 1 / 1 | product_defect | 100% / 100% | [results/temp_experiment_parallel.txt](results/temp_experiment_parallel.txt) |
| No signal at all ("It's okay I guess.") | 0.0 / 1.0 | 1 / 1 | value_for_money | 100% / 100% | [results/temp_experiment_nosignal.txt](results/temp_experiment_nosignal.txt) |
| No signal + reasoning allowed | 0.0 / 1.0 | 1 / 1 | value_for_money | 100% / 100% | [results/temp_experiment_reasoning.txt](results/temp_experiment_reasoning.txt) |
| Explicit tie (delivery_delay vs. product_defect, stated "50/50", + reasoning), 30 trials | 0.0 | 1 | product_defect | 100% | [results/temp_experiment_tie.txt](results/temp_experiment_tie.txt) |
| Explicit tie (same review), 30 trials | **1.0** | **2** | product_defect | **70%** (21/30, vs. 9 delivery_delay) | [results/temp_experiment_tie.txt](results/temp_experiment_tie.txt) |
| Explicit tie (same review), 50 more trials, reasoning | 0.0 | 1 | product_defect | 100% (50/50) | conversation (ad hoc run, not saved to a results file) |

**Predicted vs. actual**
- **Predicted** (2026-10-17, before running): will have to deliberately write it
- **Actual:** Partly right. We did have to deliberately write an explicitly-tied review to get any instability at all — six other attempts (a clean case, a dataset-sourced "ambiguous" review, two hand-written balanced reviews, a no-signal review, and that same no-signal review with reasoning allowed) all stayed at 100% agreement at *both* temperatures. The one review that worked (explicitly stating "both were equally bad, genuinely 50/50") destabilized **only at `temperature=1.0`** (70% agreement, 2 distinct outputs across 30 trials). `temperature=0` never flipped, even on that same maximally-tied review, across 80 combined trials (30 + a further 50).
- **Why:** Temperature only has visible effect where the model's own probability distribution over the next token is genuinely spread out — it doesn't manufacture uncertainty that isn't there. Most reviews, even ones ambiguous *to a human*, turned out to have a dominant, confident answer in the model's own distribution, so sampling more broadly at `temperature=1.0` still almost always landed on the same token. True `temperature=0` instability, where it exists at all, comes from floating-point non-associativity in how GPUs batch and order parallel operations across requests — a hardware-level effect, not something a prompt can reliably trigger. Reaching it would likely take hundreds or thousands of trials, not a few dozen.

**Gotchas**
- `temperature` is not a parameter on `messages.create()` at all in `anthropic` 1.13.0's typed interface — on every model, not just the ones that reject it server-side. Confirmed with `inspect.signature()`. Use `extra_body={"temperature": ...}` to send it as a raw field.
- Sonnet 5.5 / Opus 5.5 / Fable 5.1 / Haiku 5.5 run adaptive thinking by default and return 400 on a non-default `temperature` while thinking is active — this is **model-specific**, not a general API removal. Haiku 4.5 (no thinking by default) still runs temperature normally. Pick a model deliberately when a lab or a production feature actually needs direct sampling control.
- A "distinct outputs" count of 1 can still hide real sampling activity — raw output *wording* varied across temperature=1.0 runs even when the final classification didn't. Don't conclude "temperature had no effect" just from the final label; check the raw text if you want to confirm sampling was actually active.
- An ambiguous-*to-a-human* review is not the same as an ambiguous-*to-the-model* one. Several reviews that plausibly span 2–3 themes still produced a single, confident, 100%-stable answer from the model at every temperature we tried.

**Remember**
- `temperature=0` is not mathematically guaranteed to be perfectly reproducible, but in everything we tested here — including a review deliberately written to be a 50/50 tie, across 80 trials — it held 100% stable. In practice, for short classification tasks, treat `temperature=0` as reliable, and don't expect prompt engineering alone to destabilize it.
- `temperature=1.0` can and did destabilize a genuinely tied case (70% agreement). If a production classification step needs to be auditable/reproducible, use `temperature=0` deliberately — don't assume the default is already low.
- If a categorization is unstable, check which lever actually caused it before rewriting the prompt: here, the fix for instability was lowering temperature back to 0, not rewording anything. Only reach for prompt rewrites once you've confirmed temperature isn't the driver.
- Current-generation thinking-by-default models (Sonnet 5.5, Opus 5.5, Fable 5.1, Haiku 5.5) don't expose temperature at all. If a future lab or feature wants direct sampling control, it needs an older or non-thinking model (e.g. Haiku 4.5) — this capability wasn't removed everywhere, just moved to a smaller set of models.

**Commands**
```bash
# clear-cut / ambiguous / balanced / parallel / no-signal cases (20 trials each by default)
uv run python labs/lab-01-model-playground/experiments/temperature_experiment.py \
  --label "<name>" --review "<review text>"

# allow the model to reason before answering, and set trial count explicitly
uv run python labs/lab-01-model-playground/experiments/temperature_experiment.py \
  --label "<name>" --review "<review text>" --n 30 --reasoning
```

## 1.3 Compare Models, Prompts, and Thinking Modes on One Task

**Question this answered:** On a deliberately unreliable support ticket, where does a more capable model's extra cost actually buy better output, and where does extra "thinking" effort just add cost without adding correctness?

**What I built**
- [`comparison_harness.py`](experiments/comparison_harness.py) — runs one summarization instruction against ticket 59 (the planted self-contradicting ticket, `data/SPEC.md` §5, case P6) across four configurations, timing each call and computing cost from `response.usage`. Each summary is saved to its own file in `results/`, and the comparison table is printed and saved to [`results/comparison_table.txt`](results/comparison_table.txt).
- Configurations run: Haiku 5.5 (fast) with the instruction in `system`; Opus 5.5 (capable) with the instruction in `system`; Opus 5.5 with the same instruction moved into the `messages` array instead; Opus 5.5 with `thinking: {"type": "adaptive"}` and `output_config: {"effort": "high"}` explicitly set.

**How it works**
- **Model selection trade-off:** Haiku 5.5 costs $0.10/$0.50 per 1M input/output tokens; Opus 5.5 costs $4/$20 — roughly 40× more expensive per token. The question this task is built to answer is whether that 40× buys anything on a specific task, not in the abstract.
- **System vs. messages placement:** the same instruction text can go in the dedicated `system` parameter or be prepended to the user's message in `messages`. Isolated this from the model/thinking variables by keeping the model fixed (Opus 5.5) across both placement runs, so any quality difference traces to placement alone, not a confound.
- **Extended thinking has no real "off" state on current models.** This echoes the finding in [1.2](#12-run-a-temperature-and-non-determinism-experiment): Opus 5.5 and Haiku 5.5 both run adaptive thinking **on by default**, and Opus 5.5's thinking can't be fully disabled (`{"type": "disabled"}` returns 400 on it). The `output_tokens_details.thinking_tokens` field confirms this directly — every single run here shows a nonzero thinking-token count, including the two runs that never set `thinking` at all. So the "extended thinking" config didn't toggle thinking on from an off state; it only raised `effort` from its default (`medium` on Opus 5.5) to `high`. The real variable tested was effort level, not thinking vs. no-thinking.
- **Cost accounting:** `cost = (input_tokens × input_price + output_tokens × output_price) / 1,000,000`, using each model's per-token price from the pricing table.

**Results**
| Configuration | Model | Latency(s) | Input tok | Output tok | Thinking tok | Cost ($) | Quality (1–5) |
|---|---|---|---|---|---|---|---|
| Fast model (Haiku 5.5) | claude-haiku-5-5 | 3.08 | 1,556 | 421 | 228 | 0.00037 | 2 |
| Capable model (Opus 5.5), instruction in `system` | claude-opus-5-5 | 6.56 | 1,556 | 532 | 196 | 0.01686 | 4 |
| Capable model, instruction in `messages` | claude-opus-5-5 | 8.27 | 1,562 | 650 | 280 | 0.01925 | 5 |
| Capable model, extended thinking (`effort: high`) | claude-opus-5-5 | 6.35 | 1,556 | 568 | 228 | 0.01758 | 4 |
| Capable model, instruction buried in the middle of the ticket (Destructive Testing) | claude-opus-5-5 | 7.38 | 1,550 | 647 | 225 | ~0.0183 | content: 5, format: broken |

Full table: [results/comparison_table.txt](results/comparison_table.txt). Saved summaries: [Haiku](results/summary_fast_model_%28haiku_5.5%29.txt), [Opus/system](results/summary_capable_model_%28opus_5.5%29.txt), [Opus/messages](results/summary_capable%2C_instruction_in_messages.txt), [Opus/thinking](results/summary_capable%2C_extended_thinking.txt), [Opus/buried mid-document](results/summary_instruction_buried_middle.txt).

**Quality ratings — who scored them:** the user found a bare 1–5 "quality" judgment too abstract to make blind, so together we turned it into a checklist against `data/SPEC.md`'s documented ground truth for ticket 59's three planted contradictions (condition on arrival, refund→replacement, Monday→Thursday delivery day), and I (Claude) applied that checklist and assigned the scores above, at the user's explicit request — a deviation from the usual split where the user rates quality themselves.

- **Haiku 5.5 (2/5):** got the final requested resolution right (replacement, not refund), but didn't explicitly flag any of the three contradictions, and actively **fabricated** a reconciliation for the delivery-day contradiction — reporting it as "late delivery (Thursday instead of the expected Monday)," an "expected vs. actual" framing the ticket never states. The ticket says it *arrived* Monday, then later says it *arrived* Thursday — a contradiction, not a delay.
- **Opus 5.5, system placement (4/5):** correctly resolved the final request and explicitly flagged the Monday→Thursday contradiction ("he first said Monday, then corrected himself"). Did not explicitly flag the refund→replacement reversal — stated only the final resolution.
- **Opus 5.5, messages placement (5/5):** the strongest of the four. Explicitly flagged *both* the Monday→Thursday contradiction and the refund→replacement reversal ("the ticket first demands a full refund... the customer changed their mind"), and added a genuinely useful operational note (no order number was included in the ticket).
- **Opus 5.5, extended thinking / effort=high (4/5):** same correctness profile as the system-placement run — flagged the delivery-day contradiction, not the refund reversal — despite costing more ($0.01758 vs. $0.01686) and generating more thinking tokens.

**Predicted vs. actual**
- **Predicted** (2026-10-17, before running): I beleive instructon in message would work better as we saw above
- **Actual:** Destructive Testing step: the same instruction, same model (Opus 5.5), moved from the top of the `messages` content into the exact middle of ticket 59's 852-word text (first half of the ticket, then the instruction, then the second half — [results/summary_instruction_buried_middle.txt](results/summary_instruction_buried_middle.txt)). Content accuracy held up, and arguably improved: this run explicitly flagged *both* remaining contradictions ("he first said Monday, then corrected it" and "explicitly changed his mind" on refund vs. replacement) — more explicit flagging than the system-placement or effort=high runs managed. But format instruction-following broke down: the ticket asked for "3-5 sentences," and this run produced 6 sentences under a `**Summary:**` header, then added an entirely unrequested `**Agent notes:**` section with 4 bullet points — structure nothing in the instruction called for.
- **Why:** Position mattered, but not for the reason either of us predicted. The semantic *content* instruction ("summarize this, capture the complaint, the resolution, key details") survived being buried, likely because the model's attention can still locate and weight it via content-matching regardless of its position in the sequence (the same mechanism from [1.1](#11-build-a-token-and-context-window-inspector)'s attention discussion). What didn't survive was the thin, low-redundancy *format* constraint ("3-5 sentences") — a single short phrase with nothing else in the text reinforcing it. Once it's buried mid-document instead of occupying the position models are trained to weight most heavily (start of message, or the dedicated `system` slot), that kind of thin signal is exactly what gets deprioritized relative to the richer content task competing for the same attention budget.

**Gotchas**
- "Extended thinking enabled" is not a real on/off toggle on Opus 5.5 or Haiku 5.5 — both run adaptive thinking by default, and Opus 5.5 rejects `{"type": "disabled"}` outright. Check `response.usage.output_tokens_details.thinking_tokens` before assuming a run had no thinking; it's very likely nonzero even when `thinking` was never set in the request.
- A fluent, confident-sounding summary (Haiku's) can still contain a factual fabrication. Rate against the planted ground truth, not against how natural the prose reads.
- Burying an instruction mid-document doesn't fail the way you'd expect. The *content* task (what to extract) can survive fine; the *format* constraint (length, structure) is what quietly breaks. Check both separately — a correct-looking answer can still violate the format you asked for.

**Remember**
- On a task built around deliberately unreliable source text, the capable model's ~40× cost premium bought real correctness: it caught contradictions the cheap model missed or misrepresented. On a task without that kind of planted ambiguity, the cheap model's output would likely be indistinguishable in practice — the cost premium only earns its keep when the task actually needs the extra care.
- Raising `effort` from its default to `high` cost more ($0.01758 vs. $0.01686, +4%) without any measurable quality gain here — in fact the cheaper "instruction in messages" variant scored higher than the explicit-high-effort run. Higher effort pays off on tasks that need genuine multi-step reasoning; this was reading comprehension and extraction, where it mainly adds tokens.
- Moving the same instruction from `system` into `messages` was, in this single test, not a downgrade — it scored *higher* (5 vs. 4), catching one more of the three planted contradictions. One run isn't enough to generalize "always put instructions in messages," but it's a reminder not to assume `system` is automatically the stronger placement without checking.
- Content instructions and format instructions don't degrade the same way under positional pressure. A semantic task ("summarize X, extract Y") can survive being buried mid-document because attention can still locate and weight it by content; a thin, low-redundancy constraint ("exactly 3-5 sentences, no extra sections") is what actually gets lost. If a format constraint matters in production, don't just trust that burying it alongside the content task is safe — verify the format held, separately from checking the content held.

**Commands**
```bash
uv run python labs/lab-01-model-playground/experiments/comparison_harness.py
```

## 1.4 Manage Conversation State and Send an Image

**Question this answered:** Where does a chatbot's "memory" actually live, how much does it cost as a conversation grows, and what happens when you send the model an image instead of text?

**What I built**
- [`cli_chat.py`](experiments/cli_chat.py) — an interactive command-line chat. A plain Python list (`history`) starts empty; each turn appends the user's message and the model's reply, and the *whole* list is resent on every `messages.create` call.
- [`token_growth.py`](experiments/token_growth.py) — the same pattern, scripted and unattended: 10 pre-written turns that deliberately reference earlier turns (a name, a product mentioned first), so recall can be checked automatically rather than typed live. Logs `input_tokens` per turn to [results/token_growth.csv](results/token_growth.csv) and prints a text bar chart (no plotting library in the project, and one text chart didn't justify adding `matplotlib` as a dependency).
- Two one-off image-description calls: [results/image_descriptions.txt](results/image_descriptions.txt) — one product photo (`KET-0001.jpg`) and one damaged-return photo (`return_10.jpg`, the kettle with the improvised wood-stick handle, from this task's own photo-finishing work — see `data/SPEC.md` section 4's status note and `data/answer_keys/damage_labels.csv`).

**How it works**
- **Conversation state is not server-side.** The API has no session or memory between calls — `messages.create` is stateless. "Memory" in any chatbot is entirely client-side bookkeeping: your own code keeps the growing list and resends it, in full, every single turn. Drop the list, and the model has no way to know the conversation ever happened — there is nowhere else the prior turns could be stored.
- **Cost grows with the conversation, not just the new message.** Every turn bills for the *entire* resent history as input tokens, not just the latest line. A 10-turn conversation's last turn costs far more in input tokens than its first turn, even though the user only typed one short sentence.
- **Images are tokenized too, and they're not cheap relative to text.** An ~800×589px product photo costs 673 input tokens — more than 4x a single customer review's ~150 tokens ([1.1](#11-build-a-token-and-context-window-inspector)) — for comparable "one item" cost accounting.
- **Large images get downscaled before tokenizing, not linearly charged.** Confirmed by comparison, not assumption: see the Destructive Testing result below.

**Results**

Token growth over the scripted 10-turn conversation ([results/token_growth.csv](results/token_growth.csv), [results/token_growth_run.txt](results/token_growth_run.txt)):

| Turn | Input tokens |
|---|---|
| 1 | 29 |
| 2 | 226 |
| 3 | 312 |
| 4 | 452 |
| 5 | 599 |
| 6 | 834 |
| 7 | 953 |
| 8 | 1,232 |
| 9 | 1,371 |
| 10 | 1,426 |

Recall was verified directly, not assumed: asked "What's my name again?" at turn 4, the model correctly answered "Priya" (stated at turn 1). Asked "what was the first product I mentioned?" at turn 9, it correctly answered "the Homiva kettle" over "Kitchora air fryer" (mentioned turn 5) — proving the resent history is actually doing the recall work, not the model guessing.

Image vs. text token cost ([results/image_descriptions.txt](results/image_descriptions.txt)):

| Item | Input tokens |
|---|---|
| One customer review (~57 words, [1.1](#11-build-a-token-and-context-window-inspector)) | 150 |
| One product photo, 800×589px (pipeline's resize cap) | 673 |

The damaged-photo description independently identified the exact same fault as our own ground-truth label: the model called out the burnt/peeling improvised handle as "the real problem" and a burn hazard, calling the body scratches merely cosmetic — matching `data/answer_keys/damage_labels.csv`'s `return_10.jpg,10,kettle,broken_part,moderate` exactly, with no prompting toward that answer.

**Predicted vs. actual**
- **Predicted** (2026-10-17, before running): model will not remember it as the memory (context window) has been cleared
- **Actual:** Destructive Testing, part 1 — ran 3 real turns (favorite color, city, dog's name), then cleared `history = []` in code and asked "What did I just tell you?" Result: `input_tokens=16` — the same as a fresh first message — and the reply states "This is the first message in our conversation, so you haven't told me anything yet... I also can't see any past conversations." Exact match to the prediction. Full transcript in the conversation; not separately saved to a results file (ad hoc run).

  Destructive Testing, part 2 — sent a huge image (upscaled the same `KET-0001.jpg` to 6000×4500px, 1.8MB) and compared its `count_tokens` result against the normal 800×589px version. Huge image: 27,000,000 pixels → **4,757 tokens**. Normal image: 471,200 pixels → **673 tokens**. That's 57x more pixels for only 7x more tokens — not remotely linear.
- **Why:** Part 1 confirms there is no hidden state anywhere except what's in the `messages` list your own code sends — the API genuinely has no memory of its own, so wiping the list is indistinguishable from a conversation that never happened. Part 2: the measured token counts are far below what linear pixel-to-token scaling would predict (671,200px → 673 tokens implies roughly 1 token per 700px; at that rate, 27,000,000px should cost ~38,500 tokens, not 4,757). The only explanation consistent with the data is that the API downscales an oversized image server-side before tokenizing it, capping the cost rather than letting it scale with raw resolution. A practical consequence: sending a much larger file than needed doesn't buy proportionally more "detail" to the model either, since what it actually sees is the downscaled version.

**Gotchas**
- A cleared/dropped history isn't a "degraded" memory — it's a complete, un-detectable-from-the-inside absence. The model doesn't know something is missing; it just starts fresh, same as turn 1 of any conversation.
- Image token cost doesn't scale with file size or resolution the way you'd naively expect — don't estimate image cost by eyeballing pixel count or file size; measure it with `count_tokens` instead, since there's a server-side downscale step you can't see from the client side.
- The thinking-eats-max_tokens issue from [1.1](#11-build-a-token-and-context-window-inspector) and [1.3](#13-compare-models-prompts-and-thinking-modes-on-one-task) showed up again here: the first damaged-photo description call (`max_tokens=300`) was cut off mid-sentence because 290 of those tokens went to thinking, leaving none for the visible answer. Raising `max_tokens` to 800 fixed it. Budget generously for any vision call where the model might need to reason before answering.

**Remember**
- There is no server-side conversation memory in the Claude API (or any stateless LLM API). Every byte of "context" the model has about prior turns exists only because your code resent it. This is the entire mechanism behind every chatbot's memory — there's no deeper magic to look for.
- Cost and context-window usage both grow with the *full* resent history every turn, not just the newest message. A 100-turn conversation's last few turns are dramatically more expensive than its first few, purely from carrying the accumulated history forward.
- An image at a modest 800px resize already costs more tokens (673) than a full customer review of text (150) — multimodal input is comparatively expensive per item, which matters when estimating cost for a feature that processes many images.
- Oversized images get downscaled, not linearly billed — 57x the pixels cost only 7x the tokens here. Don't assume "smaller file = cheaper" without measuring; the relationship isn't proportional once an image exceeds whatever internal cap the API applies.

**Commands**
```bash
# interactive chat with real conversation memory
uv run python labs/lab-01-model-playground/experiments/cli_chat.py

# scripted 10-turn conversation with token-growth logging
uv run python labs/lab-01-model-playground/experiments/token_growth.py
```
