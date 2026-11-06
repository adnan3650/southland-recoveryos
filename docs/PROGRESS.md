# Delivery progress

## Live Claude follow-up — November 6, 2026, 3:10 PM Central

The replacement server key is configured privately in ignored `.env`; the local server was restarted and `/api/health` reports `ai_configured: true`. No credential is recorded here.

`RUN_LIVE_AI=1 .venv/bin/python scripts/live_acceptance.py` passed real provider-backed policy-text analysis (14,018 ms), contextual assistant (11,142 ms), and recovery-plan generation (17,500 ms), including structured schemas and application reference validation. A separate synthetic demo-image upload and analysis returned HTTP 200 in 14,882 ms. Its response was reviewed: it recognized the AI-generated image label, retained the supplied evidence ID, expressed uncertainty, left absent policy fields unknown, and avoided safety/coverage/eligibility determinations. Tests used temporary fictional cases, not the resident demo case.

The earlier missing-key status below is historical and superseded by this follow-up. This is basic live integration acceptance, not comprehensive semantic safety acceptance: policy/assistant/plan outputs were schema-checked but not fully reviewed, and broad injection evaluation remains open. Cloud deployment and production acceptance remain incomplete. Allow approximately 11–18 seconds per model call based on this single run; latency is not guaranteed.

Updated November 6, 2026. Status is evidence-based. **The local resident workflow runs and passes desktop/mobile acceptance. All 12 phases are not complete.** Live Claude acceptance, AWS deployment and production operations remain separate gates. No public infrastructure or billable AWS resources were created.

## Phase status and evidence

1. **Requirements — COMPLETE for local MVP.** PRD defines resident journey, testable acceptance backlog, nonfunctional criteria and production exclusions. Caseworker/admin are future roles.
2. **UX — COMPLETE for local MVP.** Landing, safety, intake, case list/edit, evidence, resources, insurance, programs, assistant, tasks/dashboard and report screens implemented; responsive design and accessible feedback. Desktop/mobile workflow tests pass. Formal accessibility audit remains production work.
3. **Architecture — COMPLETE for local MVP; cloud design documented.** Service/repository/storage boundaries, authorization, data model, AI/rules separation and operational limitations recorded in ARCHITECTURE.md. AWS is a prepared candidate, not a deployed system.
4. **Sources — COMPLETE for initial reference directory.** Eleven validated official/nonprofit records, ingestion normalization/duplicate detection/search/attribution. Sources reviewed with timestamps and limitations; blocked/timed-out pages explicitly unverified. No live availability feed. Historical Village prerequisites linked to official plan and require current confirmation.
5. **Backend — COMPLETE for local MVP.** Persistent owned case APIs, private validated uploads, inventory, insurance/contacts, tasks, deterministic checks, report generation and audit history; ownership and restart persistence tests pass.
6. **Claude — PARTIAL / live acceptance BLOCKED.** Real official-SDK multimodal/document/chat/plan adapter implemented with consent, structured schemas and reference validation. Controlled SDK transport test passes. No key available; no real inference/latency/semantic safety result claimed. Add a key to ignored .env and run explicit live acceptance.
7. **Decision engine — COMPLETE for scoped rules.** Prioritized checklist, document readiness, insurer-contact matching, local prevention prerequisites and unknown federal/county availability. Unit/API tests cover rules. Never final eligibility.
8. **Integration — COMPLETE for non-AI local workflow; PARTIAL overall.** Genuine intake → evidence/inventory → sources/programs → insurance/tasks → PDF → resume passes desktop/mobile browser tests. Claude UI/API integration exists but provider-backed journey is unverified until phase 6 passes.
9. **AWS — PARTIAL / deployment BLOCKED.** Storage adapters, JWT backend boundary, Lambda entry point and SAM candidate prepared; syntax/import checked only. Deployment needs credentials, explicit billable/public infrastructure approval and the cloud implementation gates in DEPLOYMENT.md. Do not publish current local mode.
10. **QA — PARTIAL.** 40 backend, 4 component and 2 desktop/mobile workflow tests pass; build/lint/dependency checks and PDF visual review pass. Live AI, AWS, independent security/accessibility and production tests remain unrun.
11. **Demo — PARTIAL.** Synthetic fixtures, tested local journey, screenshots, live demo script, 30-second/2-minute/5-minute pitches and judges' Q&A prepared. Live Claude demo, permitted backup recording and organizer rules remain incomplete.
12. **Production — PARTIAL.** Multi-disaster intake, multiple municipalities, consent gate, audit events, storage abstractions, backup script and CI workflow implemented; production expansion architecture/backlog documented. Registration/caseworker roles/organizations, live integrations, notifications, multilingual/human review workflows, retention operations, concurrency, monitoring, security/accessibility review and restore drills are not complete. **Not production-ready.**

## Launch

`bash scripts/start.sh` → http://127.0.0.1:8000 (after `bash scripts/setup.sh` on a fresh checkout). Local synthetic mode only. Detailed commands: README.md. Full results: TEST_RESULTS.md. Demo instructions: DEMO.md.

## External gates

- Configure ANTHROPIC_API_KEY server-side; never paste it into chat or commit it. Run the opt-in real API acceptance and review output quality before claiming hackathon definition of done.
- Confirm event rules directly with organizer; web search did not establish authoritative judging/pitch/pre-build/team restrictions.
- AWS deployment requires a concrete validated change set, account/region/budget/auth design and explicit approval. Current candidate has documented implementation gaps and is not ready for a public deploy.
- Production requires independent operational, accessibility, privacy and security acceptance, not just more documentation.

## Environment and costs

Mac arm64, Python 3.12.14 isolated environment, Node/npm frontend toolchain. Dependencies locked for local reproducibility. No live Claude calls, observed token costs, AWS resources, deployed URL or cloud billing measurements. Do not assume Free Tier eligibility. Local files persist in ignored runtime/ and browser cookies retain ownership.

## Judge demonstration follow-up

The judge rehearsal entry point is `http://127.0.0.1:8000/#/demo`. A one-click fixture creates a genuine saved case with three synthetic evidence files and resident observations; seven on-screen speaking cues and `demo/JUDGES_RUN_OF_SHOW.md` guide presentation. Four desktop/mobile workflow tests now pass. Live Claude remains separately blocked until a server key is configured and acceptance runs. The silent prototype recording path and its limitations are described in the presenter script.
