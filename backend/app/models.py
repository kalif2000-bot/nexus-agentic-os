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
    max_discount_percent: float = Field(..., ge=0, le=100, examples=[15])


class CompanyRegistrationRequest(BaseModel):
    company_name: str = Field(..., examples=["Nexus Pilot Customer"])
    admin_email: str = Field(..., examples=["founder@company.com"])
    plan: str = Field(..., examples=["Growth"])


class CompanyResponse(BaseModel):
    id: int
    company_name: str
    admin_email: str
    plan: str
    api_key: str
    created_at: str


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
    company: CompanyResponse
