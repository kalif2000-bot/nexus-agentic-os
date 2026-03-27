# Nexus Agentic OS Deployment Guide

## 1. GitHub Push Checklist

Before you push, confirm these are true:

- `.env` is not committed
- `.venv/` is not committed
- `logs/` is not committed
- your OpenAI key exists only in local env vars or in Render environment variables
- `render.yaml` is present in the repo root

Recommended commands:

```bash
git status
git add .
git commit -m "Build Nexus Agentic OS MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## 2. Production-Safe Secrets Checklist

Use this checklist before deploying.

### Backend secrets

- `OPENAI_API_KEY`
  - Required for live OpenAI calls
  - Set only in Render environment variables
  - Never commit into `.env.example`, source code, screenshots, or chat logs

- `OPENAI_MODEL`
  - Recommended value: `gpt-4o-mini`
  - Safe to store in Render env vars

- `ALLOW_MOCK_FALLBACK`
  - Recommended value for demos: `true`
  - If `true`, the app still works when OpenAI quota is unavailable
  - If `false`, backend returns an error when OpenAI is unavailable

### Hosting reality check

- A free public deployment is good for demos and investor links.
- It is not a true production-grade setup for a subscription SaaS.
- Free Render web services spin down after 15 minutes of inactivity.
- Free Render web services use an ephemeral filesystem, so local SQLite data is not durable.
- Render persistent disks require a paid service.

For a real subscription business, the next upgrade path is:

- managed database such as Render Postgres
- hosted authentication
- Stripe billing
- custom domain
- production monitoring

### Frontend secrets

- `API_BASE_URL`
  - Set this to your deployed backend URL
  - Example: `https://nexus-agentic-os-backend.onrender.com`

### Local-only files

- `.env`
- `logs/`
- `.venv/`

### Safe files to commit

- `.env.example`
- `requirements.txt`
- `render.yaml`
- `backend/`
- `frontend/`
- `README.md`
- `DEPLOY.md`

## 3. Render Deployment Screen-by-Screen

This project uses Render Blueprint deploys from `render.yaml`.

### Step 1: Push code to GitHub

1. Open your terminal in the project root.
2. Run:

```bash
git add .
git commit -m "Build Nexus Agentic OS MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Open Render

1. Go to [https://render.com](https://render.com)
2. Sign in
3. From the dashboard, click `New +`
4. Click `Blueprint`

### Step 3: Connect GitHub

1. If GitHub is not connected yet, Render will ask to connect it
2. Authorize Render to access the repository
3. Select the repo that contains this project

### Step 4: Blueprint detection

1. Render will detect `render.yaml`
2. You should see two services listed:
   - `nexus-agentic-os-backend`
   - `nexus-agentic-os-frontend`
3. Click `Apply`

### Step 5: Configure backend service

After the services are created:

1. Click the backend service: `nexus-agentic-os-backend`
2. Open the `Environment` tab
3. Add these environment variables:

```text
OPENAI_API_KEY=your_real_openai_key
OPENAI_MODEL=gpt-4o-mini
ALLOW_MOCK_FALLBACK=true
```

4. Click `Save Changes`
5. Click `Manual Deploy` if Render does not redeploy automatically

### Step 6: Copy backend URL

1. Wait for the backend deploy to finish
2. Open the backend service homepage
3. Copy the public URL

Example:

```text
https://nexus-agentic-os-backend.onrender.com
```

4. Test it in the browser:

```text
https://nexus-agentic-os-backend.onrender.com/docs
```

### Step 7: Configure frontend service

1. Go back to the Render dashboard
2. Click the frontend service: `nexus-agentic-os-frontend`
3. Open the `Environment` tab
4. Add:

```text
API_BASE_URL=https://your-backend-service.onrender.com
```

5. Click `Save Changes`
6. Trigger redeploy if needed

### Step 8: Verify frontend

1. Open the frontend public URL from Render
2. You should see the Streamlit app
3. Click `Run Agents`
4. Confirm you see:
   - Sales Agent Output
   - Conflict Warning
   - Final Decision

## 4. First Production Test

Use this sample input in the UI:

- Customer Name: `Acme Corp`
- Deal Size: `12000`
- Sales Context: `The customer wants a very strong incentive to close before quarter-end.`
- Finance Max Discount: `15`

Expected result:

- Sales agent suggests a discount
- finance policy detects a violation if the suggestion is over `15%`
- final decision is corrected to `15%`

## 5. Known Production Note

Your current OpenAI account returned `insufficient_quota` during live testing.

That means:

- the app is deployable now
- the fallback simulator will keep the demo working if `ALLOW_MOCK_FALLBACK=true`
- live OpenAI output will start working once billing or credits are added to your OpenAI account

## 6. Current SaaS MVP Scope

This repository now includes:

- landing page for investors and prospects
- pricing page
- company registration portal
- tenant API key generation
- secure `x-api-key` protected decision endpoint
- API documentation page
- extensive use cases
- knowledge base content

This is enough for a public MVP demo.
It is not yet full production billing/auth infrastructure.
