# AI Hackathon Readiness Plan

How the Mastery Labs turn into the ability to enter AI hackathons in any field and ship something that works, live, within the time limit.

## What wins a hackathon

1. **Speed from idea to working app** — the first hours shouldn't go on setup.
2. **A public URL** judges can open on their own phones.
3. **A demo that feels alive** — streaming output, voice or image input, something visual.
4. **Scope discipline** — knowing what to cut at hour 8.
5. **Proof it works** — few teams can show a measured quality number. You will be able to.

## Where the labs cover each one

| Need | Built in | What you'll have |
|---|---|---|
| Fast start | Milestone 1 | A starter-kit repo: package, LLM client, FastAPI, Streamlit, Docker, CD |
| Public URL | Lab 6.P | Push-to-deploy on Google Cloud Run, with rollback |
| Live-feeling demo | Labs 1.4, 2.4, 5.P | Streaming responses, image, PDF and audio input |
| A demo that doesn't fall over | Labs 2.P, 9.3, 9.P | Retries, fallbacks, rate limits, error states |
| Provider required by the event | Lab 10.P | Switch model provider by config |
| Proof of quality | Lab 3 | A small golden set and a scorecard in minutes |
| Polished frontend *(optional)* | Lab 11 | A React UI against the same API |

## Gaps the labs don't cover

These are quick to add when a hackathon brief needs them; don't build them in advance.

- **Generating media:** text-to-speech, image generation. Each is usually one API call; try the sponsor's offering first.
- **Pitching:** a 2-minute demo script and video. Practised in Milestone 2.
- **Finding events:** check Devpost, lu.ma and sponsor announcements; prefer events whose sponsor APIs you can try beforehand.

## Milestone 2: the timed mock hackathon

Run it after Lab 9, from the Milestone 1 starter kit. Pick a brief outside retail so you practise a new domain:

| Field | Example brief |
|---|---|
| Healthcare | Turn discharge-summary PDFs into a plain-language checklist for patients |
| Insurance | Triage claim photos: damage type, severity, next step |
| Education | Turn a recorded lecture into notes and a quiz |
| Finance | Q&A over an earnings-call transcript, with citations |
| Food | Voice-driven weekly meal planner with a shopping list |
| Legal | Extract and flag risky clauses from a contract PDF |

### Suggested 12-hour timeline

| Hours | Phase | Deliverable |
|---|---|---|
| 0:00–0:45 | Brief & scope | One-paragraph brief, data models, a scope list with the cut-first items marked |
| 0:45–1:15 | Deploy first | Starter kit cloned and a hello-world endpoint live on a public URL |
| 1:15–6:00 | Core AI feature | Working end to end, checked against 5 hand-written examples |
| 6:00–8:00 | Demo experience | UI, streaming, and at least one non-text input |
| 8:00–9:30 | Hardening | Error states, fallback model, rate limit |
| 9:30–10:30 | Ship | Final deploy, smoke test on a phone |
| 10:30–12:00 | Demo | Script, 2-minute video, a fallback recording, README |

Deploying in the first hour is deliberate: deployment problems found at hour 11 sink projects.

## Readiness checklist

- [ ] The starter kit deploys a new AI app to a public URL in under 30 minutes.
- [ ] I can stream model output into a UI.
- [ ] I can take audio, image and PDF input.
- [ ] I can switch model provider by config.
- [ ] I can produce a quality number for a demo from a 20-example golden set.
- [ ] I always record a fallback demo video before presenting live.
- [ ] I've completed one timed mock run and written its retro.
