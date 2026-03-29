from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.db import init_db
from backend.app.models import (
    AdminUserResponse,
    ApiKeyCreateRequest,
    ApiKeyResponse,
    AuthResponse,
    AuthenticatedRunResponse,
    CompanyProfile,
    CompanyRegistrationRequest,
    DecisionLogResponse,
    FinalDecisionResult,
    LoginRequest,
    PolicyCheckResult,
    PolicyResponse,
    PolicyUpdateRequest,
    RunRequest,
    RunResponse,
    SalesAgentResult,
    WorkspaceResponse,
)
from backend.app.services.company import (
    authenticate_user,
    create_api_key,
    create_company_with_admin,
    create_decision_log,
    get_company_by_api_key,
    get_company_workspace,
    get_workspace_by_session,
    list_decisions,
    revoke_api_key,
    update_policy,
)
from backend.app.services.llm import get_sales_agent_recommendation
from backend.app.services.policy import (
    build_final_decision,
    check_discount_policy,
    extract_discount_percent,
)


app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="Policy-aware control layer for AI decisions across company workflows.",
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


def _workspace_response(workspace: dict) -> WorkspaceResponse:
    return WorkspaceResponse(
        company=CompanyProfile(**workspace["company"]),
        admin_user=AdminUserResponse(**workspace["admin_user"]) if workspace.get("admin_user") else None,
        policy=PolicyResponse(**workspace["policy"]) if workspace.get("policy") else None,
        api_keys=[ApiKeyResponse(**row) for row in workspace.get("api_keys", [])],
    )


def _resolve_policy_max(request: RunRequest, company_workspace: dict | None = None) -> float:
    if request.max_discount_percent is not None:
        return request.max_discount_percent
    if company_workspace and company_workspace.get("policy"):
        return float(company_workspace["policy"]["max_discount_percent"])
    raise HTTPException(status_code=400, detail="max_discount_percent is required when no workspace policy exists.")


def execute_run(request: RunRequest, max_discount_percent: float) -> RunResponse:
    sales_output = get_sales_agent_recommendation(
        customer_name=request.customer_name,
        deal_size=request.deal_size,
        sales_context=request.sales_context,
    )

    suggested_discount = extract_discount_percent(sales_output["raw_text"])
    policy_result = check_discount_policy(
        suggested_discount_percent=suggested_discount,
        max_discount_percent=max_discount_percent,
    )
    final_decision = build_final_decision(
        suggested_discount_percent=suggested_discount,
        max_discount_percent=max_discount_percent,
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


def require_workspace(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token.")
    token = authorization.split(" ", 1)[1]
    workspace = get_workspace_by_session(token)
    if not workspace:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return workspace


@app.post("/run", response_model=RunResponse)
def run_agents(request: RunRequest) -> RunResponse:
    try:
        max_discount = _resolve_policy_max(request)
        return execute_run(request, max_discount)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/auth/signup", response_model=AuthResponse)
def signup(request: CompanyRegistrationRequest) -> AuthResponse:
    try:
        create_company_with_admin(
            company_name=request.company_name,
            admin_email=request.admin_email,
            full_name=request.full_name,
            password=request.password,
            plan=request.plan,
        )
        auth = authenticate_user(request.admin_email, request.password)
        if not auth:
            raise HTTPException(status_code=500, detail="Workspace was created, but session login failed.")
        return AuthResponse(token=auth["token"], workspace=_workspace_response(auth["workspace"]))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/auth/login", response_model=AuthResponse)
def login(request: LoginRequest) -> AuthResponse:
    auth = authenticate_user(request.email, request.password)
    if not auth:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return AuthResponse(token=auth["token"], workspace=_workspace_response(auth["workspace"]))


@app.get("/workspace", response_model=WorkspaceResponse)
def get_workspace(authorization: str | None = Header(default=None)) -> WorkspaceResponse:
    workspace = require_workspace(authorization)
    return _workspace_response(workspace)


@app.put("/workspace/policy", response_model=PolicyResponse)
def save_policy(request: PolicyUpdateRequest, authorization: str | None = Header(default=None)) -> PolicyResponse:
    workspace = require_workspace(authorization)
    policy = update_policy(
        company_id=workspace["company"]["id"],
        policy_name=request.policy_name,
        max_discount_percent=request.max_discount_percent,
        auto_correct=request.auto_correct,
        escalation_message=request.escalation_message,
    )
    return PolicyResponse(**policy)


@app.post("/workspace/api-keys", response_model=ApiKeyResponse)
def create_workspace_api_key(
    request: ApiKeyCreateRequest,
    authorization: str | None = Header(default=None),
) -> ApiKeyResponse:
    workspace = require_workspace(authorization)
    api_key = create_api_key(workspace["company"]["id"], request.label)
    return ApiKeyResponse(**api_key)


@app.delete("/workspace/api-keys/{key_id}")
def deactivate_workspace_api_key(
    key_id: int,
    authorization: str | None = Header(default=None),
) -> dict:
    workspace = require_workspace(authorization)
    revoke_api_key(workspace["company"]["id"], key_id)
    return {"status": "revoked", "key_id": key_id}


@app.get("/workspace/decisions", response_model=list[DecisionLogResponse])
def get_workspace_decisions(authorization: str | None = Header(default=None)) -> list[DecisionLogResponse]:
    workspace = require_workspace(authorization)
    decisions = list_decisions(workspace["company"]["id"])
    return [DecisionLogResponse(**row) for row in decisions]


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
    workspace = get_company_workspace(company["id"])
    max_discount = _resolve_policy_max(request, workspace)

    try:
        result = execute_run(request, max_discount)
        create_decision_log(
            company_id=company["id"],
            customer_name=request.customer_name,
            deal_size=request.deal_size,
            sales_context=request.sales_context,
            requested_max_discount_percent=result.finance_policy.max_allowed_discount_percent,
            suggested_discount_percent=result.sales_agent.suggested_discount_percent,
            approved_discount_percent=result.final_decision.approved_discount_percent,
            conflict_detected=result.finance_policy.conflict_detected,
            sales_raw_text=result.sales_agent.raw_text,
            sales_reasoning=result.sales_agent.reasoning,
            decision_summary=result.final_decision.decision_summary,
        )
        return AuthenticatedRunResponse(
            company=CompanyProfile(**company),
            **result.model_dump(),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
