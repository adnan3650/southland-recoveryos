# Demonstration and pitches

## Ready-to-open judge rehearsal

Open http://127.0.0.1:8000/#/demo. Prepare the fictional case and follow the on-screen speaking cues. See `demo/JUDGES_RUN_OF_SHOW.md` for the concise presenter script. The fixture uses genuine case/upload/inventory APIs and a prominently labeled AI-generated image. No simulated Claude results are created. Logging a matching Synthetic Insurer contact changes documentation readiness from 80% to 100%; neither means approval.

## Honest acceptance boundary

The local deterministic resident journey is implemented. Live Claude demonstration requires ANTHROPIC_API_KEY and passing the opt-in acceptance script. Do not present unavailable AI as running, replay recordings as live inference, or treat unit-test stubs as provider calls. Event format, pre-build rules, team limits and recording permission remain unconfirmed; verify with the organizer before submission. No first-place outcome is guaranteed.

## Preflight

Run `bash scripts/check.sh`, start the server, run Playwright, then configure the ignored local `.env` and run `RUN_LIVE_AI=1 .venv/bin/python scripts/live_acceptance.py`. Inspect actual results for grounding and safety. Refresh official resources before the event. Use fictional resident information only. Keep a clean demo browser profile; preserve its cookies for saved-case resumption. Open http://127.0.0.1:8000. Keep API and browser on the same machine. Do not publish local mode.

## Live sequence (adapt to confirmed pitch length)

1. Explain recovery fragmentation and show landing/safety screens.
2. Start Recovery. Fictional name Alex Morgan; South Holland 60473; flood; 2026-09-12; homeowner; basement sofa/storage boxes affected; food need and displacement if desired. Say explicitly that the storm scenario is fictional.
3. Save case and show prioritized safety/essentials checklist.
4. Upload `demo/synthetic-estimate.txt` as estimate and `demo/synthetic-policy.txt` as policy. Add an actual synthetic damage photo if available; do not claim the text fixture is a vision test.
5. Check transmission consent, analyze with real Claude, wait for saved result and review uncertainty/evidence IDs. The policy excerpt exercises document reasoning; a photo is additionally required to demonstrate vision.
6. Show damage inventory; add a resident observation such as wet sofa upholstery. Explain provenance labels.
7. Explore 211/food/shelter official links and review checked timestamps and unverified capacity caveats.
8. Save fictional insurer details and log a contact. Show documentation checks updating without changing eligibility.
9. Review South Holland prevention-program prerequisites. Explain mitigation vs damage compensation and unknown declaration/applicability for federal assistance.
10. Ask Claude: “What should I do next, and what information is missing?” Show saved context, citations and uncertainties. Generate suggested plan; review before adding a suggestion as a task.
11. Complete a checklist task, add a resident target date and show dashboard.
12. Preview/download PDF, inspect it, reload and resume from My cases. No database edits are necessary.

If the API key/network is unavailable, demonstrate deterministic functionality and label live AI acceptance blocked. Do not claim the hackathon definition of done is met until live analysis, assistant and plan run successfully. A silent prototype rehearsal recording can be generated with `npm --prefix frontend run demo:record`; it explicitly shows missing live Claude configuration. It is not a live AI acceptance recording. Confirm organizer recording rules before presenting it. Desktop/mobile screenshots from browser tests are engineering evidence, not a replacement for a live demo.

## 30-second pitch

A disaster doesn't end when the floodwater disappears. That's when families face insurance questions, scattered evidence and disconnected assistance websites. Southland RecoveryOS brings the next steps into one recovery case. Residents organize damage, use Claude to interpret supplied evidence, see official local resources and identify missing paperwork. Deterministic checks keep program prerequisites separate from AI interpretation, and a downloadable packet helps residents prepare for conversations with people who can help.

## 2-minute pitch

For a Southland resident, the hardest recovery question may be: what do I do next? The answer is scattered across photos, policy documents, agency websites and phone notes. Southland RecoveryOS organizes those details into a saved case.

Our fictional resident Alex reports basement flooding in South Holland. The workspace starts with safety and essential needs. Alex uploads evidence and explicitly consents before Claude interprets it. AI observations retain evidence references and uncertainty; resident observations stay distinct. The insurance center shows which documentation is present and what still needs attention.

The readiness engine is deterministic. It checks evidence and program prerequisites rather than asking a model to decide eligibility. The Village prevention rebate is a mitigation option to confirm, not an automatic damage payment. Federal assistance requires a relevant declaration and agency review; the app doesn't invent one. Official resources link residents to 211, food and shelter references without claiming live capacity.

Alex asks a contextual question, reviews suggested steps, updates tasks and downloads a recovery packet. The purpose is a more organized conversation with an insurer or support worker. This is a synthetic local prototype with real Claude adapters; production authentication, live partner feeds and operational review remain required. We will measure resident task completion and packet preparation time in consented trials before claiming improved outcomes.

## 5-minute expanded pitch

Use the 2-minute narrative with a three-minute demonstration: 45 seconds for intake and checklist; 45 seconds for evidence, consent and actual Claude analysis; 45 seconds for readiness/program caveats; 30 seconds for contextual assistance; 15 seconds for PDF and resumption. Actual model latency varies; time the successful run before committing to the schedule. No official event pitch duration is assumed. Close with a request for community partners to validate terminology, prerequisites and usability.

## Architecture for engineers

React/TypeScript → typed same-origin REST → FastAPI/Pydantic → owned SQLite case aggregate/private files. Claude runs only server-side via official SDK structured parsing. Evidence and source IDs are validated; no model tools can execute external actions. Independent deterministic rules handle readiness/prerequisites. The PDF is generated from persisted state. AWS storage/JWT adapters and a SAM candidate are prepared but not accepted/deployed. See ARCHITECTURE.md for concurrency and cloud payload/time limitations.

## Community impact

The product helps a resident keep their story and next steps together. It does not replace emergency responders, insurers or caseworkers. Community partners should review local service descriptions, language access and the workflow before any real resident pilot. Measure completion rate, time to prepare a usable packet, identified missing prerequisites, and whether caseworkers find the records useful. No numerical improvement is claimed.

## Comparison and differentiation

Government/nonprofit directories supply authoritative referrals but typically do not organize this resident's complete evidence trail. Insurance portals focus on a particular insurer's claim. General AI chat can explain information but lacks this application's persisted case and deterministic prerequisites. RecoveryOS combines case documentation, traceable interpretation, source links, readiness checks and a shareable packet. This is a workflow comparison, not a verified claim that competitors lack these capabilities; named-vendor market research remains future work.

## Likely questions

- **Does it decide eligibility or coverage?** No. It identifies prerequisites and questions for responsible agencies/insurers.
- **Are shelter beds live?** No. It links established sources and requires direct confirmation.
- **Why Claude?** Multimodal interpretation and contextual reasoning over supplied evidence; deterministic rules remain separate.
- **How is injection handled?** Untrusted data boundary, no executable tools, strict schemas/reference checks. Live semantic red-team evaluation remains required.
- **What is built today?** Read the phase status and actual test results; distinguish local verified functionality from provider/cloud gates.
- **How do you protect resident data?** Current mode is synthetic and loopback-only with ownership isolation. Public authentication/privacy/retention are gates before a real pilot.
- **What does it cost?** No AWS resources were created. Claude/token costs and usage-based cloud costs require actual workload measurement. No free-tier assumption.
- **How do you know it helps?** We have workflow tests, not resident outcome studies. Partner-led usability evaluation is the next evidence step.
