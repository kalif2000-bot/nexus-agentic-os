from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.db import init_db
from backend.app.models import (
    AuthenticatedRunResponse,
    CompanyRegistrationRequest,
    CompanyResponse,
    FinalDecisionResult,
    PolicyCheckResult,
    RunRequest,
    RunResponse,
    SalesAgentResult,
)
from backend.app.services.company import create_company, get_company_by_api_key, get_company_by_id
from backend.app.services.llm import get_sales_agent_recommendation
from backend.app.services.policy import (
    build_final_decision,
    check_discount_policy,
    extract_discount_percent,
)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI control layer that checks agent decisions against business policy.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/")
def healthcheck() -> dict:
    return {"message": "Nexus Agentic OS backend is running."}


def execute_run(request: RunRequest) -> RunResponse:
    sales_output = get_sales_agent_recommendation(
        customer_name=request.customer_name,
        deal_size=request.deal_size,
        sales_context=request.sales_context,
    )

    suggested_discount = extract_discount_percent(sales_output["raw_text"])

    policy_result = check_discount_policy(
        suggested_discount_percent=suggested_discount,
        max_discount_percent=request.max_discount_percent,
    )

    final_decision = build_final_decision(
        suggested_discount_percent=suggested_discount,
        max_discount_percent=request.max_discount_percent,
    )

    return RunResponse(
        sales_agent=SalesAgentResult(
            raw_text=sales_output["raw_text"],
            suggested_discount_percent=suggested_discount,
            reasoning=sales_output["reasoning"],
        ),
        finance_policy=PolicyCheckResult(**policy_result),
        final_decision=FinalDecisionResult(**final_decision),
    )


@app.post("/run", response_model=RunResponse)
def run_agents(request: RunRequest) -> RunResponse:
    try:
        return execute_run(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/companies/register", response_model=CompanyResponse)
def register_company(request: CompanyRegistrationRequest) -> CompanyResponse:
    company = create_company(
        company_name=request.company_name,
        admin_email=request.admin_email,
        plan=request.plan,
    )
    return CompanyResponse(**company)


@app.get("/companies/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int) -> CompanyResponse:
    company = get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")
    return CompanyResponse(**company)


@app.post("/api/run", response_model=AuthenticatedRunResponse)
def run_agents_for_company(
    request: RunRequest,
    x_api_key: str | None = Header(default=None),
) -> AuthenticatedRunResponse:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing x-api-key header.")

    company = get_company_by_api_key(x_api_key)
    if not company:
        raise HTTPException(status_code=401, detail="Invalid API key.")

    try:
        result = execute_run(request)
        return AuthenticatedRunResponse(
            company=CompanyResponse(**company),
            **result.model_dump(),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
