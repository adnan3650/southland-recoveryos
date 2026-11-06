# Local operation and cloud deployment gates

## Local launch

Run `bash scripts/setup.sh`, then `bash scripts/start.sh`. Open http://127.0.0.1:8000. Port 8000 serves frontend and API from one origin. `.env` is loaded from project root; never overwrite an existing `.env`. Set ANTHROPIC_API_KEY in your editor and restart for Claude. No API key is installed by the setup script. No AWS calls occur in local mode. Claude real analysis incurs provider usage only when consented actions or the explicit live acceptance script run.

## Backup and restore

Stop the server. Run `.venv/bin/python scripts/backup.py /private/tmp/recoveryos-backup-UNIQUE`. The destination must not exist. Preserve browser ownership cookies separately using your browser profile backup; the database alone cannot recover ownership capabilities. Protect backups as sensitive even though only synthetic data is authorized. To restore, stop the server, preserve the current runtime directory under a new name, copy a verified backup to `runtime/`, retain ownership cookies, then launch and verify case/file access. Do not overwrite existing runtime data. Restore is documented, not yet a completed operational drill.

## AWS candidate

`infrastructure/template.yaml` is an undeployed SAM candidate: HTTP gateway JWT authorizer, Lambda/Python 3.12/Mangum, encrypted DynamoDB, private encrypted versioned S3 with TLS-only policy, 14-day logs, throttles, reserved concurrency and a $10/month actual-cost budget alert. Budget alerts do not cap spend. No resources have been created; no deployed URL, observed charges or validated AWS cost estimate exists. Costs include gateway/Lambda/DynamoDB/S3/logging/backups/secrets/auth and separate Claude tokens; calculate for approved region/traffic before deployment and do not assume Free Tier eligibility.

Do not deploy the current candidate publicly. The local MVP lacks frontend Cognito authentication/token attachment, distributed version checks, cloud integration validation and a production privacy workflow. Gateway timeout is shorter than possible Claude latency. API Gateway/Lambda binary payload constraints mean 10 MB local uploads are not supported as-is. Use signed S3 upload plus scan/quarantine and an asynchronous AI job flow before cloud acceptance. Default static frontend deployment and Cognito resources are intentionally not provisioned without final design/approval.

## Required preparation before approval

1. Select region, account, budget, audience and retention policy. Verify event rules independently.
2. Implement and test Cognito frontend registration/sign-in/sign-out, auth header attachment and document authorization. Verify issuer/client/JWT claims with staging tests.
3. Add optimistic version checks to Dynamo updates, idempotency and blob cleanup; validate ownership under concurrent requests.
4. Add direct signed bounded uploads, scanning and asynchronous analysis polling. Make public health route policy explicit.
5. Create a sanitized build directory containing backend, data, built frontend if same-origin hosting is selected, and Python dependencies. `sam build` does not currently discover `backend/requirements.txt` at repository-root CodeUri; provide a Makefile/custom build or staged root requirements before validation. Never package `.env`, `.git`, runtime, backups or local `.venv`.
6. Validate using `sam validate --lint --template-file infrastructure/template.yaml`, package in a compatible arm64 Lambda environment, inspect IAM diff and deployment change set. These commands have not been executed here because SAM/AWS setup is absent.
7. Obtain explicit approval for the concrete change set and billable resources. Then `sam deploy --guided --template-file <validated-built-template>` using the approved account, secret ARN, origin, issuer/client and email. Never paste a raw secret as a CLI argument.
8. Run cloud auth/ownership/upload/Claude/report tests, verify private bucket blocks, budgets, alarms, redacted logs, restore and rate limits. Record actual resource IDs, URL and observed cost.

## Teardown after authorized deployment

Export approved data and confirm retention obligations first. `sam delete --stack-name <approved-stack>` removes stack-managed non-retained resources after review. DynamoDB and S3 are retained intentionally; versions/backups continue incurring charges. Deleting retained documents/tables/versions requires explicit approval. Remove approved secrets/auth/frontend resources only when no longer shared. Verify billing inventory and confirm no continuing resources; deleting a stack is not proof of zero spend.

## Production backlog

Caseworker assignments, organizations/roles; live resource partner agreements and refresh scheduling; notifications; reviewed translations; human review queue; consent/retention/export/deletion; full keyboard/screen-reader audit; bounded scalable search; immutable audit; incident monitoring and on-call; restore exercise; CI dependency/secret scanning; independent security review and load tests. None is described as implemented merely because an architecture exists.
