USE_CASES = [
    {
        "name": "Enterprise Discount Guardrails",
        "industry": "B2B SaaS",
        "customer_name": "Acme Corp",
        "deal_size": 12000,
        "sales_context": "The customer wants a very strong incentive to close before quarter-end and sales is pushing for an aggressive offer.",
        "max_discount_percent": 15,
        "challenge": "A sales agent wants to move fast, but finance policy caps discount exposure.",
        "agent_action": "Sales recommends a larger discount to accelerate conversion.",
        "policy": "Finance allows a maximum of 15 percent discount for this deal band.",
        "system_response": "Nexus detects the violation, rewrites the decision, and returns a compliant approval path.",
        "outcome": "Revenue is protected while the rep still gets a clear next-best action.",
    },
    {
        "name": "Procurement Approval Routing",
        "industry": "Manufacturing",
        "customer_name": "Northline Supply",
        "deal_size": 78000,
        "sales_context": "A strategic enterprise buyer is asking for pricing relief plus custom terms because the contract size is significant.",
        "max_discount_percent": 12,
        "challenge": "Large enterprise deals mix pricing, risk, and approval complexity.",
        "agent_action": "The selling motion favors speed and relationship preservation.",
        "policy": "Strategic discounts above 12 percent require CFO review.",
        "system_response": "Nexus constrains the offer and shows the escalation rule before the contract moves forward.",
        "outcome": "Teams align on an approvable path without back-and-forth email loops.",
    },
    {
        "name": "Renewal Rescue With Margin Control",
        "industry": "Subscription Software",
        "customer_name": "BrightWave Media",
        "deal_size": 26000,
        "sales_context": "An existing customer is threatening churn and expects concessions during the renewal call.",
        "max_discount_percent": 10,
        "challenge": "Retention pressure can push agents into margin-damaging offers.",
        "agent_action": "The renewal agent proposes a more aggressive retention package.",
        "policy": "Renewals can offer up to 10 percent without VP approval.",
        "system_response": "Nexus trims the discount and logs the reason so the account team can justify the final package.",
        "outcome": "Customer save motions stay consistent with retention policy and gross margin targets.",
    },
    {
        "name": "Channel Partner Incentive Review",
        "industry": "Cloud Infrastructure",
        "customer_name": "Apex Integrators",
        "deal_size": 54000,
        "sales_context": "A channel partner wants special pricing because they promise a future pipeline commitment across multiple regions.",
        "max_discount_percent": 14,
        "challenge": "Partner deals often combine long-term upside with short-term pricing risk.",
        "agent_action": "The partner agent leans toward a bigger incentive to secure strategic distribution.",
        "policy": "Partner discounts above 14 percent require a structured business case.",
        "system_response": "Nexus keeps the recommendation inside policy and highlights the missing business-case requirement.",
        "outcome": "Partnerships move forward with disciplined controls instead of ad hoc exceptions.",
    },
]


KNOWLEDGE_BASE = {
    "What Nexus Is": [
        "Nexus Agentic OS is a control plane for AI agents. It sits between agent outputs and operational systems so businesses can allow AI speed without surrendering policy enforcement.",
        "Instead of trusting every model decision directly, Nexus evaluates the recommendation against rules, constraints, and approval logic before anything becomes final.",
        "The result is a system that feels autonomous to users, but accountable to leadership, finance, legal, and operations teams.",
    ],
    "How A Decision Flows": [
        "1. An application submits a scenario, such as a pricing request or contract recommendation.",
        "2. A specialist agent produces a proposed action in natural language.",
        "3. Nexus extracts structured values from that proposal, such as a discount percentage.",
        "4. Policy logic compares the recommendation against business constraints.",
        "5. If the proposal is compliant, Nexus approves it. If not, Nexus adjusts or escalates it.",
        "6. The frontend presents the original recommendation, the policy analysis, and the final approved action.",
    ],
    "Why This Matters": [
        "Without a control layer, multiple AI agents can create operational inconsistency: one agent optimizes for growth, another for margin, another for risk.",
        "Nexus gives startups and enterprises a simple way to coordinate those competing incentives in one place.",
        "For investors, this means the product speaks directly to one of the biggest adoption blockers in enterprise AI: trust, governance, and safe automation.",
    ],
    "Current MVP Scope": [
        "The current MVP demonstrates one clean workflow: a Sales Agent proposes a discount and a Finance Policy constrains it.",
        "This is intentionally small but strategically useful because the same pattern extends to credit underwriting, procurement approvals, customer support refunds, HR screening, and AI workflow orchestration.",
        "What matters is the pattern: propose, inspect, detect conflict, correct, and explain.",
    ],
    "How To Explain It To Others": [
        "Simple version: Nexus makes AI agents safer for real businesses.",
        "Operator version: Nexus is a policy-aware AI orchestration layer that mediates agent outputs before they touch critical systems.",
        "Investor version: Nexus is infrastructure for enterprise AI reliability, enabling adoption by reducing model conflict, policy drift, and operational risk.",
    ],
}


FAQ = [
    (
        "Is this a workflow engine or an AI product?",
        "It is both. Nexus uses AI to generate decisions, then applies deterministic policy logic to make those decisions safe and production-ready.",
    ),
    (
        "Can this work beyond discounts?",
        "Yes. The same design applies to approvals, routing, pricing, risk checks, procurement, support credits, legal review, and multi-agent coordination.",
    ),
    (
        "Why not let the model follow the rules directly?",
        "Because prompt-only controls are fragile. A dedicated control layer gives you enforceable, inspectable rules that stay stable even if prompts or models change.",
    ),
    (
        "What happens if OpenAI is unavailable?",
        "This MVP can fall back to a built-in simulator for demo continuity. In production, you would use retries, provider failover, audit logs, and stronger policy services.",
    ),
]


PRICING_PLANS = [
    {
        "name": "Starter",
        "price": "$0",
        "subtitle": "Perfect for investor demos and small pilots",
        "features": [
            "1 company workspace",
            "Manual policy configuration",
            "Basic decision sandbox",
            "Mock fallback mode for uninterrupted demos",
        ],
    },
    {
        "name": "Growth",
        "price": "$299/mo",
        "subtitle": "For startups rolling Nexus into real ops",
        "features": [
            "5 company workspaces",
            "Live API access with tenant API keys",
            "Policy-aware decision endpoint",
            "Team onboarding and use-case templates",
        ],
    },
    {
        "name": "Enterprise",
        "price": "Custom",
        "subtitle": "For large multi-agent operations",
        "features": [
            "Unlimited workspaces",
            "Advanced governance and audit controls",
            "Custom policy registry",
            "Priority onboarding and dedicated support",
        ],
    },
]


API_GUIDE = {
    "Create Workspace": {
        "method": "POST /auth/signup",
        "body": {
            "company_name": "Acme Revenue Ops",
            "admin_email": "ops@acme.com",
            "full_name": "Ariana Founder",
            "password": "securepass123",
            "plan": "Growth",
        },
    },
    "Login": {
        "method": "POST /auth/login",
        "body": {
            "email": "ops@acme.com",
            "password": "securepass123",
        },
    },
    "Run A Policy-Aware Decision": {
        "method": "POST /api/run",
        "headers": {"x-api-key": "nexus_your_company_key"},
        "body": {
            "customer_name": "Acme Corp",
            "deal_size": 12000,
            "sales_context": "The customer wants a large incentive to close this week.",
            "max_discount_percent": 15,
        },
    },
}
