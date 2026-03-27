# Nexus Agentic OS MVP

Nexus Agentic OS is a simple working MVP that shows how an AI control layer can sit between an AI agent and business policy.

The flow is:

1. A Sales Agent uses OpenAI to recommend a discount.
2. A Finance Policy defines the maximum allowed discount.
3. The backend detects whether the recommendation violates policy.
4. The system corrects the decision if needed.
5. The frontend shows the original agent output, conflict status, and final approved decision.

## 1. Full Folder Structure

```text
Nexus Agentic OS/
├── backend/
│   ├── __init__.py
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       ├── models.py
│       └── services/
│           ├── __init__.py
│           ├── llm.py
│           └── policy.py
├── frontend/
│   └── app.py
├── .env.example
├── .gitignore
├── render.yaml
├── requirements.txt
└── README.md
```

## 2. What the Backend Does

The FastAPI backend exposes:

- `GET /` for a simple health check
- `POST /run` to run the full agent-policy flow

The `/run` endpoint:

1. Sends the sales scenario to OpenAI
2. Receives a sales recommendation
3. Extracts the discount percent from the model's text
4. Compares it with the finance policy limit
5. Adjusts the final decision if the recommendation is too aggressive
6. Returns structured JSON

## 3. Setup From Scratch

### Step 1: Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

## 4. OpenAI Integration

### Install the OpenAI package

It is already included in `requirements.txt`, but the standalone command is:

```bash
pip install openai
```

### Set your API key

Windows PowerShell for the current session:

```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
$env:OPENAI_MODEL="gpt-4o-mini"
$env:ALLOW_MOCK_FALLBACK="true"
```

macOS/Linux:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_MODEL="gpt-4o-mini"
export ALLOW_MOCK_FALLBACK="true"
```

Or copy `.env.example` to `.env` and fill in your values.

If your OpenAI account has no quota yet, set `ALLOW_MOCK_FALLBACK=true` so the demo still runs using the built-in Sales Agent simulator.

### Exact API call code

The project uses this code in `backend/app/services/llm.py`:

```python
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)

response = client.responses.create(
    model=settings.openai_model,
    input=prompt,
)

content = response.output_text
```

This matches the current OpenAI Responses API pattern from the official docs:

- [Text generation guide](https://platform.openai.com/docs/guides/text?lang=python)
- [Responses API reference](https://platform.openai.com/docs/api-reference/responses/list?lang=python)

## 5. Run the Backend Locally

```bash
uvicorn backend.app.main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

Swagger docs:

```text
http://localhost:8000/docs
```

## 6. Run the Frontend Locally

Set the backend URL first if needed:

Windows PowerShell:

```powershell
$env:API_BASE_URL="http://localhost:8000"
```

macOS/Linux:

```bash
export API_BASE_URL="http://localhost:8000"
```

Then start Streamlit:

```bash
streamlit run frontend/app.py
```

Frontend URL:

```text
http://localhost:8501
```

## 7. API Flow

The full request path is:

```text
Streamlit frontend
    -> POST /run to FastAPI backend
    -> FastAPI calls OpenAI Responses API
    -> OpenAI returns the Sales Agent recommendation
    -> FastAPI extracts the discount and checks finance policy
    -> FastAPI adjusts the decision if needed
    -> FastAPI returns structured JSON
    -> Streamlit renders the output
```

## 8. Core Features Implemented

### Sales Agent simulation

The Sales Agent is the LLM call in `backend/app/services/llm.py`.

### Rule system

The Finance Policy lives in `backend/app/services/policy.py`.

### Conflict detection

If:

```text
suggested_discount_percent > max_discount_percent
```

then a conflict is detected.

### Final decision logic

If there is a conflict:

- the backend lowers the discount to the max allowed policy value
- the response marks `was_adjusted = true`

If there is no conflict:

- the original recommendation is approved

## 9. Example Request

### cURL

```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Acme Corp",
    "deal_size": 12000,
    "sales_context": "The customer wants a very strong incentive to close before quarter-end.",
    "max_discount_percent": 15
  }'
```

### PowerShell

```powershell
$body = @{
  customer_name = "Acme Corp"
  deal_size = 12000
  sales_context = "The customer wants a very strong incentive to close before quarter-end."
  max_discount_percent = 15
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/run" -ContentType "application/json" -Body $body
```

## 10. Example Expected Output

If the Sales Agent suggests `18%` and policy allows only `15%`, the API response will look like:

```json
{
  "sales_agent": {
    "raw_text": "I recommend offering an 18% discount to close the deal this week.",
    "suggested_discount_percent": 18.0,
    "reasoning": "The customer is price-sensitive and the timeline is short, so a stronger incentive could improve close probability."
  },
  "finance_policy": {
    "max_allowed_discount_percent": 15.0,
    "conflict_detected": true,
    "violation_reason": "Suggested discount 18.0% exceeds the finance policy limit of 15.0%."
  },
  "final_decision": {
    "approved_discount_percent": 15.0,
    "was_adjusted": true,
    "decision_summary": "Nexus Agentic OS adjusted the sales suggestion from 18.0% down to 15.0% to satisfy finance policy."
  }
}
```

If the Sales Agent suggests `10%` and policy allows `15%`, then:

- `conflict_detected` is `false`
- `approved_discount_percent` stays `10.0`
- `was_adjusted` is `false`

## 11. How the Discount Extraction Works

The backend scans the Sales Agent text for:

- percentages like `18%`
- words like `18 percent`

If no percentage is found, the backend returns an error.

## 12. Deployment on Render for Free

This repository includes `render.yaml`, which defines:

- one free Python web service for FastAPI
- one free Python web service for Streamlit

Important: Render’s docs currently say free web services are available, but they spin down after 15 minutes of inactivity and can take about a minute to wake up again.
Source:

- [Render free services](https://render.com/docs/free)
- [Render web services](https://render.com/docs/web-services)
- [Render deploy flow](https://render.com/docs/deploys)

### Step-by-step backend deployment

1. Push this code to GitHub.
2. Sign in to Render.
3. Click `New`.
4. Choose `Blueprint`.
5. Connect your GitHub repo.
6. Render will detect `render.yaml`.
7. Create the services.
8. Open the backend service in Render.
9. Add environment variables:
   - `OPENAI_API_KEY=your_openai_api_key_here`
   - `OPENAI_MODEL=gpt-4o-mini`
10. Deploy.

Backend start command used by Render:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

### Step-by-step frontend deployment

1. Open the frontend service in Render.
2. Add environment variable:
   - `API_BASE_URL=https://your-backend-service.onrender.com`
3. Redeploy the frontend.

Frontend start command used by Render:

```bash
streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
```

### Exact Git commands to deploy

```bash
git init
git add .
git commit -m "Build Nexus Agentic OS MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## 13. Alternative Deployment Split

If you prefer:

- deploy the FastAPI backend on Render
- deploy the Streamlit frontend on another free Python web host

But the simplest copy-paste path for this MVP is to deploy both services on Render using the included `render.yaml`.

## 14. Files You Will Most Likely Edit

- `backend/app/services/llm.py` if you want to change the Sales Agent prompt
- `backend/app/services/policy.py` if you want to change rules
- `frontend/app.py` if you want to change the UI
- `render.yaml` if you want different service names

## 15. End-to-End Demo Story

When you click `Run Agents`:

1. The frontend sends your scenario to `/run`
2. The Sales Agent uses OpenAI to propose a discount
3. Nexus Agentic OS extracts the proposed percentage
4. Finance Policy checks whether the percentage is allowed
5. If the Sales Agent violates policy, the system corrects it
6. The UI shows both the original recommendation and the corrected final answer

This gives you a working demo of an AI coordination layer that prevents agent-policy conflicts.
