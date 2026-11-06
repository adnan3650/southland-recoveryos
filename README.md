# Southland RecoveryOS

A local resident recovery workspace for **fictional cases only**. React/TypeScript/Vite + FastAPI/Python 3.12, SQLite and private local evidence storage. Real Claude integration is implemented; live acceptance needs a server API key. Cloud deployment and production readiness are separate, incomplete acceptance gates.

## Launch

Prerequisites: Python 3.12+, Node 24+, npm. From the project directory:

```sh
bash scripts/setup.sh
bash scripts/start.sh
```

Open **http://127.0.0.1:8000**. The frontend production build is served by FastAPI. Keep the process running; Ctrl+C stops it. Existing installations can run `bash scripts/start.sh` directly. The app must stay bound to loopback in local mode.

For Claude, copy `.env.example` to `.env` if `.env` does not already exist. Set `ANTHROPIC_API_KEY` using your editor, never in chat, and restart the server. The key stays server-side. Model `claude-sonnet-5-5` was checked against Anthropic documentation on November 6, 2026. A configured key is not proof that live analysis has passed.

## Judge demonstration

Open http://127.0.0.1:8000/#/demo and click **Prepare judge demo case**. Follow the speaking cues, or use [the presenter script](demo/JUDGES_RUN_OF_SHOW.md). Evidence is synthetic and no AI result is simulated. Record a silent local rehearsal with `npm --prefix frontend run demo:record`. Live Claude acceptance still requires a configured key.

## Resident journey

Start recovery → safety acknowledgement → create fictional case → upload evidence → record observations or consent to live Claude analysis → view official sources and preliminary program prerequisites → save insurance/contact notes → update tasks → download PDF → resume under My cases. Browser cookies own cases; clearing them loses access. Data persists in `runtime/`, not in browser local storage.

## Verification

```sh
bash scripts/check.sh
cd frontend
npx playwright install chromium
npm run test:e2e  # server must already be running on port 8000
```

Vitest component tests, Pytest API/security/rules tests, and Playwright desktop/mobile resident journeys are included. See [actual results](docs/TEST_RESULTS.md). Tests never disguise fixtures as live AI results. A live acceptance script requires explicit opt-in: `RUN_LIVE_AI=1 .venv/bin/python scripts/live_acceptance.py`.

## Developer mode

Run backend on port 8000 and `npm --prefix frontend run dev` on port 5173. Vite proxies `/api`. Use the production port 8000 for the browser acceptance tests. API documentation: http://127.0.0.1:8000/docs.

## Operations and limitations

Only synthetic data is authorized in this build. Local ownership cookies are bearer capabilities, not user registration. No live shelter capacity, guaranteed eligibility, coverage decisions, official submissions, or notifications. Resource timestamps describe page review, not service availability. Missing Claude credentials produce visible errors with no simulated answer. No AWS resources were created.

- [Requirements](docs/PRODUCT_REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md) / [API](docs/API.md)
- [Sources](docs/DATA_SOURCES.md) / [Security](docs/SECURITY.md)
- [Deployment and restore](docs/DEPLOYMENT.md)
- [Demo and pitch](docs/DEMO.md)
- [Phase status](docs/PROGRESS.md)
