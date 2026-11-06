# Southland RecoveryOS product requirements

## Objective and scope
Deliver a resident-controlled recovery workspace for synthetic South Holland flooding cases. The critical journey is intake → evidence → readiness and sources → Claude assistance → tasks → PDF → resumption. No official applications are submitted. Caseworker and administrator are future roles; the local MVP represents one resident browser with multiple private cases.

## Acceptance backlog
Each critical story has an API, UI and verification requirement.

- **P0 Safety / resident:** before intake, show emergency limitations, 911 guidance and official flood guidance. Acceptance: keyboard-operable acknowledgement and next action; never assert current alerts.
- **P0 Disaster report:** collect event type, municipality, ZIP, date, situation, description and needs. Acceptance: invalid/future dates rejected server-side; create returns owned saved case; edit persists.
- **P0 Saved cases:** list and resume this browser's cases. Acceptance: reload preserves case; another cookie cannot read or mutate it.
- **P0 Evidence:** accept JPEG/PNG, PDF and UTF-8 text with document category. Acceptance: content validated; bounded sizes; private previews/downloads; reject disguised files and traversal names.
- **P0 Damage analysis:** with explicit transmission consent, send selected evidence to Claude. Acceptance: schema-valid observations, evidence IDs, uncertainty and missing details saved; unavailable provider fails visibly without simulated output.
- **P0 Inventory:** record resident observations and distinguish AI interpretations. Acceptance: inventory persists, appears in readiness and report, AI observations retain evidence references.
- **P0 Immediate help:** filter official shelter referral, food and essentials by need and location. Acceptance: original source, checked date, geographic limits and availability caveat displayed; no fabricated open beds.
- **P0 Insurance:** save insurer and claim references; organize policy, photos, inventory and receipts. Acceptance: missing evidence checklist updates when evidence changes; no coverage determination.
- **P0 Programs:** evaluate municipality, disaster, tenure, documents and unknown official prerequisites. Acceptance: statuses never promise eligibility; pre-approval and declaration uncertainties explicit; no inferred deadlines.
- **P0 Tasks:** prioritize safety, essential needs, evidence, insurance and assistance. Acceptance: resident can create and update tasks; completion persists separately from evidence readiness.
- **P0 Contextual AI:** saved facts and resources inform conversation. Acceptance: history persists, cited resource IDs checked server-side; invalid references rejected; no actions executed from documents.
- **P0 Report:** preview case summary and download PDF. Acceptance: packet includes supplied facts, inventory, evidence metadata, program caveats, sources, tasks and AI limitations; long text wraps.
- **P0 Resumption:** return to dashboard after restart. Acceptance: durable database and cookie ownership retain data; no manual database edits needed.
- **P1 Contact log:** record who was contacted and when; include in report.
- **P1 Claude plan:** generate supplemental prioritized suggestions; deterministic tasks remain authoritative until resident adds suggestions.
- **P1 Local portability:** one-command setup/start; lock dependencies and document reset and backup.
- **P2 Production:** Cognito registration, caseworker assignments, organizations, multilingual translation review, human verification, live feeds, notifications, data retention workflows, security review and accessibility audit.

## Nonfunctional criteria
Loopback-only synthetic mode; no keys in browser; same-origin requests; ownership on every case operation; typed bounded inputs; upload validation; sensitive logging excluded; no unapproved spending. Desktop and 390px mobile layouts usable. Time APIs and PDF generation and record measurements; provider latency measured only if live calls run.

## Out of scope
Structural safety assessment, precise photo-based repair pricing, insurance approval, official eligibility decisions, active shelter capacity, autonomous applications or communications. September 2026 scenario is fictional and asserts no actual storm/declaration.

## Impact hypotheses
Measure workflow completion and time to prepare a packet in consented usability trials; record prerequisite completeness before/after. No quantitative benefit or competition outcome claimed without testing.
