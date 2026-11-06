# API contract

Base `/api`; local ownership uses HttpOnly `recovery_owner` cookie, established on list/create. Every case route checks ownership and conceals unknown/foreign cases behind 404. In local mode there are no public resident accounts. JSON validation errors return 422; errors use `{"error":{"message":"...","fields":[]}}`. Provider unavailable: 503; invalid provider output: 502; unsafe media: 415; oversized input: 413.

- `GET /health`: service mode, AI configured flag, selected model. Does not test provider credentials.
- `GET /cases`: this owner's summaries. `POST /cases`: create case (201).
- `GET /cases/{id}`: full aggregate; `PUT`: replace editable intake fields.
- `POST /cases/{id}/documents`: multipart `file`, `category` (damage/policy/estimate/receipt/identity/other), 10 MB local limit, at most 30 documents.
- `GET /cases/{id}/documents/{doc}/file`: authorized original bytes.
- `POST /cases/{id}/documents/{doc}/analyze`: JSON `consent: true`, structured Claude interpretation saved only on success.
- `GET /cases/{id}/damage`; `POST`: resident `item`, `area`, `observation`.
- `GET /resources?q=&category=&location=`: curated source search; no current availability claim.
- `GET /cases/{id}/resources`: need-ranked local sources.
- `GET /cases/{id}/programs`: deterministic preliminary prerequisites with final_eligibility false.
- `GET /cases/{id}/readiness`: percent and five evidence checks; never eligibility/safety score.
- `GET /cases/{id}/plan`: deterministic sorted tasks.
- `POST /cases/{id}/plan/ai`: consent; supplemental structured Claude suggestions.
- `POST /cases/{id}/tasks`: title, explanation, priority, optional resident target date.
- `PATCH /cases/{id}/tasks/{task}`: status todo/done.
- `PUT /cases/{id}/insurance`: insurer, policy_number, claim_number, notes.
- `POST /cases/{id}/contacts`: organization, contacted_on (ISO date), notes.
- `POST /cases/{id}/assistant`: consent and question; saved context/history, verified source IDs.
- `POST /cases/{id}/report`: generated PDF attachment; report metadata saved.

Intake requires fictional resident_name, municipality, five-digit zip_code, disaster_type (flood/storm/tornado/fire/other), non-future incident_date, description, property_situation, displaced and immediate_needs. See executable OpenAPI at `/openapi.json` or `/docs` for exact schemas and bounds. No external applications/submissions or coverage approvals exist.
