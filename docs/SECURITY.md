# Security and privacy

## Implemented controls

Local demonstration is loopback-only and synthetic-only. Opaque ownership cookies (UUID entropy, HttpOnly, SameSite Strict, 30 days) act as local capabilities. Repository ownership checks cover cases, documents, analysis, notes, tasks and reports. Foreign IDs return 404. Trusted hosts and origin checks prevent routine local cross-site writes. No permissive CORS is enabled. Inputs forbid unknown fields, limit text sizes and validate dates/enums. Credentials remain in ignored `.env`/backend memory. No body logging is configured.

Uploads use generated storage keys, bounded size/count, MIME detection by content, raster verification with decompression bounds, PDF parsing/page/encryption checks, download-only text/PDF and restricted active-markup acceptance. Never open uploaded PDFs in a privileged server context. PDF active content checks are basic, not a complete malware scanner. Production requires AV/content disarm, quarantine, streaming ingress limits and signed direct uploads. File writes use restricted permissions. Local files/SQLite are not separately encrypted; use OS disk encryption. File/database transaction rollback and orphan sweeping remain future work.

Claude is consent-gated. The system prompt marks resident content/documents/history untrusted, denies tools/actions, and forbids safety/coverage/eligibility claims. Pydantic validates result schemas and the server rejects unknown evidence/source IDs. These controls reduce risk; no claim of proven prompt-injection immunity or semantic grounding correctness is made. Unit tests verify boundary plumbing, not the live model's behavior. A real provider evaluation corpus and human review are required.

## Operational boundaries

Do not bind local mode to public interfaces or proxy it publicly. Do not enter real personal data. Case IDs alone do not authorize access. Clearing cookies loses the capability; there is no account recovery. Anyone with the cookie can access that browser's cases. No caseworker/organization access exists.

Runtime is ignored by Git. Stop server before backing up `runtime/`; browser ownership cookies also require preservation. No destructive reset or automated deletion runs. Synthetic audit events are bounded and mutable, not compliance evidence. Backups and retention deletion require an operational policy before real residents participate.

## Outstanding production gates

Registration/recovery, MFA policy, organizational roles and assignment authorization; session revocation; CSRF hardening for chosen auth model; rate limiting; distributed write versioning; S3 scan lifecycle; consent versioning and deletion/export workflows; regional data processing terms; dependency/secret scanning; external penetration testing; accessibility audit; monitoring/alerts; incident response; disaster restore drill. SAM candidate and backend JWT adapter are not production acceptance.
