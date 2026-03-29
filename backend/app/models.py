from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    customer_name: str = Field(..., examples=["Acme Corp"])
    deal_size: float = Field(..., gt=0, examples=[12000])
    sales_context: str = Field(
        ...,
        examples=[
            "The customer is asking for a steep discount because they want to sign this week."
        ],
    )
    max_discount_percent: float | None = Field(default=None, ge=0, le=100, examples=[15])


class CompanyRegistrationRequest(BaseModel):
    company_name: str = Field(..., examples=["Nexus Pilot Customer"])
    admin_email: str = Field(..., examples=["founder@company.com"])
    full_name: str = Field(..., examples=["Ariana Founder"])
    password: str = Field(..., min_length=8, examples=["securepass123"])
    plan: str = Field(..., examples=["Growth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class ApiKeyCreateRequest(BaseModel):
    label: str = Field(..., examples=["Staging Key"])


class PolicyUpdateRequest(BaseModel):
    policy_name: str
    max_discount_percent: float = Field(..., ge=0, le=100)
    auto_correct: bool = True
    escalation_message: str


class CompanyProfile(BaseModel):
    id: int
    company_name: str
    admin_email: str
    plan: str
    created_at: str


class AdminUserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    created_at: str


class ApiKeyResponse(BaseModel):
    id: int
    label: str
    api_key: str
    is_active: int
    created_at: str


class PolicyResponse(BaseModel):
    id: int
    policy_name: str
    max_discount_percent: float
    auto_correct: int
    escalation_message: str | None = None
    created_at: str
    updated_at: str


class WorkspaceResponse(BaseModel):
    company: CompanyProfile
    admin_user: AdminUserResponse | None = None
    policy: PolicyResponse | None = None
    api_keys: list[ApiKeyResponse]


class AuthResponse(BaseModel):
    token: str
    workspace: WorkspaceResponse


class SalesAgentResult(BaseModel):
    raw_text: str
    suggested_discount_percent: float
    reasoning: str


class PolicyCheckResult(BaseModel):
    max_allowed_discount_percent: float
    conflict_detected: bool
    violation_reason: str | None = None


class FinalDecisionResult(BaseModel):
    approved_discount_percent: float
    was_adjusted: bool
    decision_summary: str


class RunResponse(BaseModel):
    sales_agent: SalesAgentResult
    finance_policy: PolicyCheckResult
    final_decision: FinalDecisionResult


class AuthenticatedRunResponse(RunResponse):
    company: CompanyProfile


class DecisionLogResponse(BaseModel):
    id: int
    customer_name: str
    deal_size: float
    sales_context: str
    requested_max_discount_percent: float
    suggested_discount_percent: float
    approved_discount_percent: float
    conflict_detected: int
    sales_raw_text: str
    sales_reasoning: str
    decision_summary: str
    created_at: str
