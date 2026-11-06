# Verification results — November 6, 2026

## Live Claude follow-up — November 6, 2026, 3:10 PM Central

The replacement server key is configured privately in ignored `.env`; the local server was restarted and `/api/health` reports `ai_configured: true`. No credential is recorded here.

`RUN_LIVE_AI=1 .venv/bin/python scripts/live_acceptance.py` passed real provider-backed policy-text analysis (14,018 ms), contextual assistant (11,142 ms), and recovery-plan generation (17,500 ms), including structured schemas and application reference validation. A separate synthetic demo-image upload and analysis returned HTTP 200 in 14,882 ms. Its response was reviewed: it recognized the AI-generated image label, retained the supplied evidence ID, expressed uncertainty, left absent policy fields unknown, and avoided safety/coverage/eligibility determinations. Tests used temporary fictional cases, not the resident demo case.

The earlier missing-key status below is historical and superseded by this follow-up. This is basic live integration acceptance, not comprehensive semantic safety acceptance: policy/assistant/plan outputs were schema-checked but not fully reviewed, and broad injection evaluation remains open. Cloud deployment and production acceptance remain incomplete. Allow approximately 11–18 seconds per model call based on this single run; latency is not guaranteed.

These are observed local results, not a claim of production acceptance.

## Passed

- `bash scripts/check.sh`: Ruff passed; **40 Pytest tests passed** in 1.23 seconds; **4 Vitest component tests passed**; TypeScript and Vite production build passed. Latest production bundle: 331.43 kB JS (101.40 kB gzip), 35.01 kB CSS (8.34 kB gzip).
- `npm --prefix frontend run test:e2e`: **2 Playwright tests passed in 5.8 seconds**, desktop Chromium and mobile iPhone 13 viewport emulated in Chromium. Workflows took 1.9 / 2.6 seconds; these omit live Claude. No browser page errors; no horizontal overflow at final dashboard.
- Browser journey: landing/safety/intake → owned case → text evidence upload → resident damage inventory → insurer/contact notes → preliminary program matching → searchable food resources → consent gate/visible unavailable Claude state → task completion/new task → PDF download → reload/resume. The steps use genuine APIs/storage; no manual database changes. Screenshots are saved in `demo/screenshots/`.
- API tests exercise persistence after app recreation, owner isolation for reads/writes/documents, validation errors, invalid/future dates, disallowed origins/hosts, oversized/active/malformed uploads, filename normalization, missing task and bad enums, resource duplicates/search, mitigation geography/tenure/disaster rules, priority ordering, evidence readiness and insurer-contact matching.
- AI boundary tests verify required consent, missing-key failures, no persisted invented conversations, rejection of unknown sources/evidence, strict result schemas and context boundary. One controlled transport fixture uses the actual installed Anthropic SDK to parse structured output. **This is a fixture, not a live Claude response or a proof of semantic safety.**
- PDF test generated a five-page packet and verified extracted case/inventory/insurance/task/source content. Final four-page synthetic QA packet was rasterized using PDFium; all pages were visually inspected for wrapping, margins, footer placement and clipping. No layout defects observed. This does not establish exhaustive Unicode coverage; standard fonts normalize unsupported characters.
- Lambda/Mangum handler imported successfully. Candidate SAM YAML parsed with seven resources. This is syntax/import verification only, not `sam validate`, deployment or cloud integration testing.
- `pip check`: no broken requirements. Curated ingestion validator: 11 unique valid records. Credential-pattern scan of application/source/script/data files: no Anthropic/AWS key-pattern matches. This is not a full secret audit or penetration test.

## Measurements

In-process FastAPI TestClient, temporary SQLite, 20 samples each: health median 1.13 ms/max 1.44 ms; retrieve case 1.63/2.39 ms; readiness 1.39/1.72 ms; resources 1.44/1.64 ms. PDF generation in a representative workflow run: 18.3 ms; 11,122 bytes, five pages. Measurements exclude network, production load and Claude calls. They are engineering observations, not service-level guarantees.

## Fixed during verification

Missing frontend stylesheet prevented builds; added responsive design. Decorative AI badge altered the assistant link's accessible name; hid it from accessibility text. Checklist summary anchor could replace the HashRouter route; replaced with a scroll button. Skip link now focuses main content without changing application route. Unrelated contact notes incorrectly satisfied insurer readiness; require matching insurer organization, with regression coverage. Added explicit resource loading/error feedback.

Initial browser attempts failed because loopback binding needed sandbox permission and installed Chromium did not match Playwright. After approved local execution and installing matching Chromium, workflow tests passed. A controlled SDK transport fixture initially used httpx; installed Anthropic 1.17 uses httpx2, so the fixture now uses the correct transport. The application itself uses SDK defaults and was unaffected.

## Not run / remaining acceptance

- Live Claude vision, policy extraction, contextual answer, plan quality, latency/token spend and semantic prompt-injection/grounding evaluation: **BLOCKED — no ANTHROPIC_API_KEY configured**. The opt-in live acceptance script exists and refuses to run without authorization/key. No provider request or live AI result is claimed.
- AWS provisioning, auth/token frontend workflow, cloud concurrency/payload behavior, cost observation, SAM lint/build/deployment validation: **NOT RUN**. No AWS resources created.
- Manual screen-reader/assistive-technology review, Safari/Firefox, independent accessibility/security review, usability studies, real service availability, production load tests, operational restore drill and remote CI execution: **NOT RUN**.
- In-app preview could not open because the computer-use browser host was unavailable. Automated local Chromium acceptance and screenshots succeeded independently.
- Full demo recording and official event rules: unconfirmed. No recording, organizer verification or competition submission is claimed.

## Judge demonstration follow-up

Added a local-only judge fixture page at `/#/demo` with synthetic image/policy/estimate uploads, resident inventory, insurance record and seven timed speaking cues. The fixture uses genuine application APIs and creates no AI responses. Repeated setup preserves the same case and avoids duplicate documents/inventory.

Four Playwright tests passed in 7.3 seconds across desktop/mobile: the original resident workflow plus fixture idempotency, three saved evidence files, 80% initial documentation readiness, a matching insurer-contact transition to 100%, genuine PDF download and same-browser resumption. Build, 40 backend tests and four component tests also passed after the demo-page addition. The image is AI-generated and prominently labeled as synthetic.

The separate paced recording test passed in 1.7 minutes. It exercised the same real local fixture, evidence image viewing, inventory, source navigation, insurer-contact readiness update, program prerequisites, explicit missing-key assistant state, task completion, actual PDF download and reload. The silent WebM was saved to `demo/recordings/prototype-walkthrough.webm` (ignored by Git). Frames from the beginning, middle and end were extracted and visually inspected. The recording contains no live Claude responses and is not a provider acceptance result.
