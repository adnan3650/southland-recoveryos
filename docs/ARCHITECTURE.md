# Architecture

## Implemented local system

React 19 / TypeScript uses HashRouter so case routes reload under a static server. Public screens cover landing, safety, intake, saved cases and resources. Workspace screens cover overview/tasks, case editing, evidence/inventory, resources, insurance/contacts, programs, contextual assistant and report preview/download. Shared API/types live in `frontend/src/lib/api.ts`; accessible feedback and source cards in `components/ui.tsx`. Form and navigation acceptance runs on desktop and mobile Chromium.

FastAPI routes in `backend/app/main.py` validate bounded Pydantic schemas, resolve ownership and call services. CaseService owns timestamps/audit history; DocumentService validates uploads and stores generated keys; AIAnalysisService calls the official Anthropic SDK with structured Pydantic outputs; ResourceService validates and searches curated records. InsuranceGuidanceService, AssistanceMatchingService and RecoveryPlanService expose boundaries around deterministic rules. ReportService generates a PDF from saved records. No AI instruction can execute a tool or submit an application.

Request flow: same-origin browser → FastAPI middleware → ownership dependency → case repository → service → validated result → saved case/audit event → UI refresh. SQLite stores each case as a bounded JSON aggregate indexed by owner. Resident, event, documents, damage items, insurance, contacts, tasks, conversations, reports and audit events live within this aggregate. User identity is an opaque browser capability in local mode, not a registered account. Resources/program requirements live in curated JSON. This is deliberately a local MVP data model, not a relational organization/caseworker system.

Upload flow: multipart request → category/size/content validation → safe generated storage key → private local file → metadata/hash appended to owned case. Evidence downloads require the same owner. Only raster previews render inline; text/PDF are attachments. AI transmission requires `consent: true` and explicit UI consent. Vision, PDF and text blocks go to Claude; model outputs are schema checked, evidence/source IDs verified, labeled as AI interpretations and persisted. Failure does not create a successful AI result.

Rules separately calculate five documentation checks, rank safety/essential/evidence/insurance tasks, and produce preliminary program statuses. Task completion does not imply documentation completeness. Government requirements never use AI as the authority. No live feed exists.

## Storage and security boundaries

CaseRepository and BlobStore protocols support SQLite/LocalBlobStore and prepared DynamoRepository/S3BlobStore adapters. All case reads/writes filter by owner. Local HTTP accepts loopback clients/trusted hostnames only; cross-origin writes are rejected. Cookies are HttpOnly/SameSite Strict. No secrets enter frontend bundles. Security headers disable framing/active objects and caching. The local runtime contains synthetic data; metadata logging and aggregate response timings omit request bodies. Audit history is bounded and is not tamper-proof.

Local asynchronous mutations use per-case process locks. One backend worker is supported. Locks are not distributed and AWS concurrency is a production blocker until conditional-version writes and idempotent blob transactions exist. Aggregate limits prevent unbounded case growth; orphaned blobs can remain when persistence fails after upload. Production needs transactional cleanup.

## Prepared cloud architecture; not deployed

Static React frontend → HTTPS gateway with Cognito JWT → Lambda/Mangum → DynamoDB + private S3; CloudWatch redacted metadata and limited log retention; server-only Anthropic secret. SAM candidate in infrastructure/template.yaml has encryption, private buckets, scoped application IAM, throttling, budget notification and retention controls. It is a reviewed starting point, not a validated production package.

Required before cloud acceptance: actual frontend sign-in/token flow; JWKS/access validation tests; distributed concurrency; Lambda payload limits and signed upload flow; AI jobs asynchronous beyond gateway timeout; health authorization policy; deployment packaging; CORS/preflight verification; budget confirmation; staging security and restore tests. Existing AWS backend JWT code does not make the frontend cloud-ready.

No EC2/NAT/Kubernetes resources are needed. Cost is usage-based; no free-tier assumption. Local app itself creates no cloud charges; Claude usage costs depend on account/model and token counts. Usage metadata captures tokens/latency for real responses. No observed AI/cloud spend is available because none was exercised.
