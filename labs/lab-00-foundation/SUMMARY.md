# Lab 0: Foundation & Dataset

> **In my own words:** _(you write this: one or two sentences, as you'd explain the lab to a colleague)_

**Concepts:** #54, #55, #56, #58 · also met: #59 (resumable jobs), #4 and #5 (temperature, non-determinism) · **Detail:** [NOTES.md](NOTES.md) · **Code:** [`src/shopai/`](../../src/shopai/), [`scripts/datagen/`](../../scripts/datagen/), [`tests/test_data_contract.py`](../../tests/test_data_contract.py)

## Key ideas
- **#54 A repeatable environment.** `pyproject.toml` says which versions you'll accept, `uv.lock` pins exactly what you get (with hashes, for every OS), and `.venv/` is the disposable result. The `src/` layout means tests exercise the installed package, as it will ship. ([0.1](NOTES.md#01-set-up-the-project-skeleton))
- **#55 Configuration and secrets.** Environment variable beats `.env` beats default; a required setting has no default, so the app fails at startup instead of an hour into a paid job. A key that reaches a commit stays in the history: revoke it. ([0.1](NOTES.md#01-set-up-the-project-skeleton))
- **#56 Structured logging.** Log an event name with fields (`log.info("startup", version=...)`), one JSON line per event, to stdout, in UTC. Configure it once, in `main()`. ([0.1](NOTES.md#01-set-up-the-project-skeleton))
- **#58 A data contract protects you only if every rule can fail:** an exact value, a count, a range or a link between tables. Plant the hard cases with code, exact strings and fixed IDs; keep answer keys out of anything a model reads. ([0.2](NOTES.md#02-write-the-dataset-spec))
- **#58 Enforce the contract with tests that are independent of the producer.** The tests take their values from the spec, never from the generator's code (maker and checker). Every failure message names the rule, the case and the lab that needs it. ([0.P](NOTES.md#0p-write-data-contract-tests))
- **#58 Declare known gaps, don't hide them.** The photos are deferred with a switch in the generator, a `pending` list in the manifest, and `xfail(strict=True)` tests driven by that list. ([0.3](NOTES.md#03-generate-the-synthetic-retailer-data), [0.P](NOTES.md#0p-write-data-contract-tests))
- **#54 applied to data: reproducibility has three layers.** Seeds for code; record-and-replay caches for LLM text, keyed by a hash of each prompt and committed; and fixed timestamps inside generated files. Prove it by fingerprinting two rebuilds. ([0.3](NOTES.md#03-generate-the-synthetic-retailer-data))
- **Code decides; the LLM only writes the words.** Counts, distributions, IDs, planted strings and arithmetic are all code. Every LLM reply is checked against the spec before it's kept. ([0.3](NOTES.md#03-generate-the-synthetic-retailer-data))
- **#4, #5 preview: the same brief sent twice gives different text.** At temperature 1.0, five briefs sent twice produced no identical texts. The facts held; the wording didn't. ([0.3](NOTES.md#03-generate-the-synthetic-retailer-data))
- **#59 preview:** saving the cache after every batch means a crash never loses text that has already been paid for, and a rerun picks up where it stopped. ([0.3](NOTES.md#03-generate-the-synthetic-retailer-data))

## Numbers to remember
| Measurement | Value | Source |
|---|---|---|
| Packages installed by `uv add pydantic-settings` | 7 (most "it worked last week" breakages are in packages you never asked for) | [0.1 notes](NOTES.md#01-set-up-the-project-skeleton) |
| First `pre-commit run --all-files` | 51.96 s, most of it building gitleaks | [0.1 notes](NOTES.md#01-set-up-the-project-skeleton) |
| Dataset | 500 customers, 60 products, 3,000 orders, 226 returns, 178 refunds, 500 reviews and tickets, 17 PDFs, 10 calls | [manifest.json](../../data/manifest.json) |
| Size of `data/` | 5.22 MB of a 50 MB budget | [manifest.json](../../data/manifest.json) |
| Returns per category per month | about 2: shop-wide trends are solid, per-category monthly ones noisy | [0.2 notes](NOTES.md#02-write-the-dataset-spec) |
| The same 5 briefs sent twice | 0 of 5 identical; 13–39% word overlap; at most $0.0074 | [results/rerun_diff.md](results/rerun_diff.md) |
| DeepSeek reasoning tokens in the pilot | about 7 of every 8 output tokens billed, so thinking was switched off | [0.3 notes](NOTES.md#03-generate-the-synthetic-retailer-data) |
| Rebuild before pinning timestamps | 8 files identical, 27 different (all PDFs and audio) | [0.3 notes](NOTES.md#03-generate-the-synthetic-retailer-data) |
| Same WAV encoded twice, 9 s apart | 6 of 19,832 bytes differed: the timestamps | [0.3 notes](NOTES.md#03-generate-the-synthetic-retailer-data) |
| Two rebuilds after pinning | 36 of 36 files identical | [0.3 notes](NOTES.md#03-generate-the-synthetic-retailer-data) |
| Data contract | 57 results: 55 passed, 2 expected failures, in 0.52 s | [0.P notes](NOTES.md#0p-write-data-contract-tests) |
| `NOT IN` against `NOT EXISTS` for P14 | 0 rows against 12 (goodwill refunds have NULL `return_id`) | [0.P notes](NOTES.md#0p-write-data-contract-tests) |
| One deleted review | 4 failing tests, 2 with misleading messages; 5 failing after the fixes, all naming the row | [0.P notes](NOTES.md#0p-write-data-contract-tests) |

## Rules of thumb
- Commit `pyproject.toml` and `uv.lock`; never `.venv/` or `.env`.
- Read settings from the environment and give them types; give required ones no default.
- Log event names with fields, not sentences with values baked in.
- Write a data rule only if a test could fail on it. "About" and "typical" need a number before they can be tested.
- Let code decide anything that must be exact; let the LLM write only the words; check every reply.
- Cache every paid LLM reply, keyed by a hash of its prompt, and commit the cache.
- Stamp generated files with a fixed time, then prove reproducibility with two rebuilds and checksums.
- Take test values from the spec, never from the code that produced the data.
- Check that a row exists before checking its content; check "exactly one" in both directions.
- Use `NOT EXISTS`, not `NOT IN`, when the subquery's column can be NULL.
- Defer a requirement only with a switch, a manifest entry and a strict expected-failure test.

## Real-world uses
- **Banking:** contract tests on an upstream feed (a core-banking or payments extract) that run before month-end and regulatory reports: exact row counts, no transactions pointing at missing accounts, control totals that add up. The checks are written from the agreed interface document, not from the sending team's code: maker and checker.
- **Healthcare and insurance:** synthetic records with planted edge cases (missing fields, contradictory notes, another language) to test a claims or document-extraction system without touching real patient data, with the answer key written at generation time.
- **Software distribution:** reproducible builds, where the same source must give byte-identical packages so anyone can verify that a binary wasn't tampered with. The same hidden-timestamp problem as the 0.3 PDFs and audio, fixed the same way.
- **Don't use it for:** judging meaning. A contract test can prove review 433 contains the injection sentence, but not that a review is really about its theme or that the policy is correct. And don't treat a generator's answer key as ground truth: it records what was asked for, and LLMs add details nobody asked for.

## Hackathon shortcut
`uv init`, `uv add` your libraries, a typed `Settings` class with a required API key, and a one-line structlog JSON setup. For data: generate it once with a seed and a cache, commit it, and write a 10-line pytest file that checks the row counts and the two or three cases your demo depends on.

## Quiz yourself
1. What does `uv.lock` protect you from that a `requirements.txt` with loose versions doesn't?
   <details><summary>Answer</summary>Drift over time and across machines, including in libraries you never asked for directly. A loose file re-resolves to whatever is newest on the day; the lockfile pins exact versions with hashes for every OS. <a href="NOTES.md#01-set-up-the-project-skeleton">0.1</a></details>
2. Why is `.env.example` committed while `.env` isn't?
   <details><summary>Answer</summary><code>.env</code> holds your real settings, secrets included. <code>.env.example</code> holds placeholders that tell the next person what to fill in, with no secrets in it. <a href="NOTES.md#01-set-up-the-project-skeleton">0.1</a></details>
3. A key was committed and pushed, then the file was deleted in the next commit. Is the key safe?
   <details><summary>Answer</summary>No. Git keeps every commit as a full snapshot, so the key is still in the history for anyone who fetched it. Revoke it and issue a new one; cleaning the history afterwards is housekeeping, not the fix. <a href="NOTES.md#01-set-up-the-project-skeleton">0.1</a></details>
4. Why plant edge cases deliberately instead of hoping random generation produces them?
   <details><summary>Answer</summary>The cases later labs need (an injection attempt, gibberish, a self-contradicting ticket) are rare by nature, so typical data won't contain them. Planting them with code, exact strings and fixed IDs makes them certain, findable and testable. <a href="NOTES.md#02-write-the-dataset-spec">0.2</a></details>
5. Why are the answer keys kept out of the tables a model reads?
   <details><summary>Answer</summary>Target leakage: if the label sits in the input, a model scores perfectly without learning anything. <a href="NOTES.md#02-write-the-dataset-spec">0.2</a></details>
6. Why can't a seed make LLM-written text reproducible, and what does instead?
   <details><summary>Answer</summary>The seed controls Python's <code>random</code> on your laptop, but the sampling happens on the provider's servers. Record every accepted reply in a cache keyed by a hash of its prompt, commit it, and replay it. <a href="NOTES.md#03-generate-the-synthetic-retailer-data">0.3</a></details>
7. Two rebuilds have the same content but different checksums. What's the likely cause, and the fix?
   <details><summary>Answer</summary>A file format that records when the file was made: the PDFs' <code>/CreationDate</code> and the <code>.m4a</code> header times. Stamp every file with one fixed time (here, the snapshot date). <a href="NOTES.md#03-generate-the-synthetic-retailer-data">0.3</a></details>
8. LLM-written reviews tend to be cleaner than real ones. How might that flatter the models you test later?
   <details><summary>Answer</summary>Still open: see 0.3's Still unclear. What the notes record so far: the generator varies the style (typos, Hinglish, all-lowercase), but whether that's enough wasn't measured.</details>
9. What's the difference between a test of your code and a test of your data, and which would have caught a generator change that removed the injection review?
   <details><summary>Answer</summary>A code test checks logic; a data test checks the committed artefact against the spec. <code>test_p5_injection_sentence_appears_only_in_review_433</code> catches it whatever the generator did, because it reads the data and takes the sentence from the spec. A code test catches it only if someone wrote one for that code, and not if the code and its test were changed together. <a href="NOTES.md#0p-write-data-contract-tests">0.P</a></details>
10. Why did the P14 count come out as 0 with `NOT IN`?
    <details><summary>Answer</summary>Goodwill refunds have <code>return_id = NULL</code>. <code>x NOT IN (…, NULL)</code> includes <code>x != NULL</code>, which is unknown, never true, so no row matches. <code>NOT EXISTS</code> gives the right count, 12. <a href="NOTES.md#0p-write-data-contract-tests">0.P</a></details>
11. Deleting review 317 first produced "SKU-shaped text found in reviews []". What was wrong with that message, and what fixed it?
    <details><summary>Answer</summary>It described a SKU problem when the real problem was a missing row: the message was written for the failure its author pictured. Checking that the planted row exists before checking its content gives "review 317, the planted SKU review, is missing". <a href="NOTES.md#0p-write-data-contract-tests">0.P</a></details>
12. What does `strict=True` add to an expected-failure (`xfail`) test?
    <details><summary>Answer</summary>An unexpected pass counts as a failure. If the photos arrive but the manifest still lists P11 as pending, the test fails, so the record of the gap can't go stale. <a href="NOTES.md#0p-write-data-contract-tests">0.P</a></details>
