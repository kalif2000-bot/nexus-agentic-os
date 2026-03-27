import json
import os
import sys
from textwrap import dedent
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from content import API_GUIDE, FAQ, KNOWLEDGE_BASE, PRICING_PLANS, USE_CASES


load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Nexus Agentic OS",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --surface: rgba(255, 251, 245, 0.82);
            --surface-strong: rgba(255, 255, 255, 0.9);
            --ink: #161616;
            --muted: #5e6368;
            --accent: #e45d37;
            --accent-2: #197278;
            --accent-3: #f3c969;
            --border: rgba(22, 22, 22, 0.08);
            --shadow: 0 26px 80px rgba(31, 42, 68, 0.13);
        }

        .stApp {
            background:
                radial-gradient(circle at 10% 0%, rgba(243, 201, 105, 0.22), transparent 26%),
                radial-gradient(circle at 100% 10%, rgba(25, 114, 120, 0.18), transparent 30%),
                linear-gradient(180deg, #fcf8f2 0%, #f4eee3 45%, #f8f8f4 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1240px;
            padding-top: 1.2rem;
            padding-bottom: 3.4rem;
        }

        h1, h2, h3 {
            letter-spacing: -0.03em;
        }

        .shell, .card, .metric, .pricing, .kb, .api, .demo {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 26px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(10px);
        }

        .shell {
            padding: 2rem;
            position: relative;
            overflow: hidden;
        }

        .shell::after {
            content: "";
            position: absolute;
            right: -60px;
            bottom: -70px;
            width: 240px;
            height: 240px;
            background: radial-gradient(circle, rgba(228, 93, 55, 0.26), transparent 70%);
        }

        .card, .pricing, .kb, .api, .demo, .metric {
            padding: 1.1rem 1.2rem;
        }

        .eyebrow {
            display: inline-block;
            padding: 0.38rem 0.68rem;
            border-radius: 999px;
            background: rgba(25, 114, 120, 0.11);
            color: var(--accent-2);
            font-weight: 700;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .hero-title {
            font-size: clamp(2.7rem, 5.6vw, 5rem);
            line-height: 0.92;
            margin: 1rem 0;
            font-weight: 850;
        }

        .hero-copy, .muted {
            color: var(--muted);
            line-height: 1.7;
        }

        .section-title {
            font-size: 2rem;
            font-weight: 800;
            margin-top: 1.4rem;
            margin-bottom: 0.25rem;
        }

        .pills {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 1rem;
        }

        .pill {
            padding: 0.45rem 0.76rem;
            border-radius: 999px;
            background: rgba(22, 22, 22, 0.06);
            font-size: 0.92rem;
        }

        .metric-label {
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.82rem;
            color: var(--muted);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            margin-top: 0.25rem;
        }

        .price {
            font-size: 2.1rem;
            font-weight: 900;
            margin: 0.4rem 0;
        }

        .code-block {
            border-radius: 20px;
            padding: 1rem;
            background: rgba(20, 20, 20, 0.92);
            color: #f7f5ef;
            overflow-x: auto;
            font-family: Consolas, monospace;
            font-size: 0.92rem;
        }

        div.stButton > button {
            border: none;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--accent), #f28047);
            color: #fff;
            font-weight: 700;
            padding: 0.76rem 1.35rem;
            box-shadow: 0 14px 28px rgba(228, 93, 55, 0.24);
        }

        .nav-note {
            margin-bottom: 0.8rem;
            color: var(--muted);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    default = USE_CASES[0]
    st.session_state.setdefault("selected_use_case", default["name"])
    st.session_state.setdefault("customer_name", default["customer_name"])
    st.session_state.setdefault("deal_size", float(default["deal_size"]))
    st.session_state.setdefault("sales_context", default["sales_context"])
    st.session_state.setdefault("max_discount_percent", int(default["max_discount_percent"]))
    st.session_state.setdefault("company_api_key", "")
    st.session_state.setdefault("company_name", "")
    st.session_state.setdefault("company_plan", "")
    st.session_state.setdefault("company_email", "")


def render_html_card(title: str, body: str, eyebrow: str | None = None, class_name: str = "card") -> None:
    eyebrow_html = f"<div class='eyebrow'>{eyebrow}</div>" if eyebrow else ""
    st.markdown(
        f"""
        <div class="{class_name}">
            {eyebrow_html}
            <h3 style="margin-top:0.75rem;">{title}</h3>
            <p class="muted" style="margin-bottom:0;">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def set_scenario(use_case: dict) -> None:
    st.session_state["selected_use_case"] = use_case["name"]
    st.session_state["customer_name"] = use_case["customer_name"]
    st.session_state["deal_size"] = float(use_case["deal_size"])
    st.session_state["sales_context"] = use_case["sales_context"]
    st.session_state["max_discount_percent"] = int(use_case["max_discount_percent"])


def post_json(path: str, payload: dict, headers: dict | None = None) -> dict | None:
    try:
        response = requests.post(f"{API_BASE_URL}{path}", json=payload, headers=headers or {}, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")
        return None


def render_home() -> None:
    st.markdown(
        """
        <div class="shell">
            <span class="eyebrow">Global AI Infrastructure</span>
            <div class="hero-title">Nexus Agentic OS</div>
            <p class="hero-copy">
                The control plane for companies adopting AI agents in revenue, operations, finance, and support.
                Nexus makes agent decisions safe, explainable, and policy-compliant before they hit real workflows.
            </p>
            <div class="pills">
                <div class="pill">Tenant-aware API access</div>
                <div class="pill">Company onboarding portal</div>
                <div class="pill">Policy-aware decision correction</div>
                <div class="pill">Investor-ready product story</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = st.columns(4)
    metric_data = [
        ("Core Story", "AI control layer", "From agent output to safe action"),
        ("Portal Modes", "6", "Marketing, pricing, docs, onboarding, dashboard, knowledge"),
        ("API Surface", "3 endpoints", "Register company, run demo, run secure company flow"),
        ("Device Reach", "Responsive", "Phone, tablet, laptop, and desktop friendly"),
    ]
    for col, (label, value, caption) in zip(metrics, metric_data):
        with col:
            st.markdown(
                f"""
                <div class="metric">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="muted">{caption}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div class='section-title'>What The Product Does</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Nexus is positioned as a subscription product that companies plug into their own workflows. Teams register, receive API credentials, send decisions through the control layer, and get policy-safe outputs back.</p>", unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        render_html_card("For Revenue Teams", "Prevent discounting chaos, renewal leakage, and inconsistent deal approvals by letting sales agents move fast inside hard finance guardrails.", "Revenue")
    with cols[1]:
        render_html_card("For Operations Leaders", "Turn prompt-only automation into governed workflows with inspectable rules, structured outputs, and repeatable decision quality.", "Ops")
    with cols[2]:
        render_html_card("For Investors", "Nexus targets a foundational enterprise AI problem: businesses want AI capability, but adoption depends on trust, control, and governance.", "Market")

    st.markdown("<div class='section-title'>How Companies Use It</div>", unsafe_allow_html=True)
    flow = st.columns(5)
    steps = [
        ("Register", "A company creates a workspace and receives an API key."),
        ("Integrate", "Their application sends agent decisions to Nexus."),
        ("Check", "Nexus parses the output and checks policy constraints."),
        ("Correct", "Unsafe decisions are rewritten or escalated."),
        ("Operate", "Teams use the final approved action with confidence."),
    ]
    for col, step in zip(flow, steps):
        with col:
            render_html_card(step[0], step[1], "Flow")


def render_pricing() -> None:
    st.markdown("<div class='section-title'>Subscription Pricing</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>This page gives the product a clear business model. For the MVP, the pricing is illustrative and aligned to a SaaS pitch.</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for col, plan in zip(cols, PRICING_PLANS):
        with col:
            features = "".join(f"<li>{feature}</li>" for feature in plan["features"])
            st.markdown(
                f"""
                <div class="pricing">
                    <div class="eyebrow">Plan</div>
                    <h3 style="margin-top:0.7rem;">{plan['name']}</h3>
                    <div class="price">{plan['price']}</div>
                    <p class="muted">{plan['subtitle']}</p>
                    <ul class="muted">{features}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_portal() -> None:
    st.markdown("<div class='section-title'>Company Portal</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>This is the SaaS-style onboarding surface: a company registers, gets an API key, and immediately starts sending decisions through Nexus.</p>", unsafe_allow_html=True)

    left, right = st.columns([1, 1.1])
    with left:
        with st.form("register_company"):
            company_name = st.text_input("Company Name", value=st.session_state.get("company_name", ""))
            admin_email = st.text_input("Admin Email", value=st.session_state.get("company_email", ""))
            plan = st.selectbox("Plan", ["Starter", "Growth", "Enterprise"], index=1 if st.session_state.get("company_plan") == "Growth" else 0)
            submitted = st.form_submit_button("Create Company Workspace")

        if submitted:
            payload = {
                "company_name": company_name,
                "admin_email": admin_email,
                "plan": plan,
            }
            data = post_json("/companies/register", payload)
            if data:
                st.session_state["company_api_key"] = data["api_key"]
                st.session_state["company_name"] = data["company_name"]
                st.session_state["company_plan"] = data["plan"]
                st.session_state["company_email"] = data["admin_email"]
                st.success("Company registered. API key created.")
                st.json(data)

    with right:
        render_html_card(
            "What The Company Gets",
            "Each company receives a tenant API key, a dedicated workspace identity, and a secure endpoint they can call from their applications. This is the foundation for a subscription product.",
            "Workspace",
            class_name="demo",
        )
        if st.session_state["company_api_key"]:
            st.markdown("<div class='api' style='margin-top:1rem;'>", unsafe_allow_html=True)
            st.markdown("<div class='eyebrow'>Issued API Key</div>", unsafe_allow_html=True)
            st.code(st.session_state["company_api_key"])
            st.markdown(f"**Workspace:** {st.session_state['company_name']}  \n**Plan:** {st.session_state['company_plan']}")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Register a company to generate a tenant API key and unlock the secure API flow.")

    st.markdown("<div class='section-title'>Secure Workspace Demo</div>", unsafe_allow_html=True)
    scenario_names = [case["name"] for case in USE_CASES]
    current_name = st.session_state.get("selected_use_case", scenario_names[0])
    selected_name = st.selectbox("Load a business scenario", scenario_names, index=scenario_names.index(current_name))
    selected_case = next(case for case in USE_CASES if case["name"] == selected_name)
    if st.button("Load Into Workspace"):
        set_scenario(selected_case)

    c1, c2 = st.columns(2)
    with c1:
        customer_name = st.text_input("Customer Name", key="customer_name")
        deal_size = st.number_input("Deal Size ($)", min_value=100.0, step=500.0, key="deal_size")
        max_discount_percent = st.slider("Finance Max Discount (%)", min_value=0, max_value=100, key="max_discount_percent")
    with c2:
        sales_context = st.text_area("Sales Context", key="sales_context", height=160)
        api_key_input = st.text_input("Workspace API Key", value=st.session_state.get("company_api_key", ""), type="password")

    if st.button("Run Secure Company Request", type="primary"):
        if not api_key_input:
            st.warning("Create a company workspace first or paste a valid API key.")
        else:
            payload = {
                "customer_name": customer_name,
                "deal_size": deal_size,
                "sales_context": sales_context,
                "max_discount_percent": max_discount_percent,
            }
            headers = {"x-api-key": api_key_input}
            data = post_json("/api/run", payload, headers=headers)
            if data:
                st.success(f"Decision processed for {data['company']['company_name']}.")
                tabs = st.tabs(["Workspace", "Decision", "JSON"])
                with tabs[0]:
                    st.json(data["company"])
                with tabs[1]:
                    st.write(data["sales_agent"]["raw_text"])
                    if data["finance_policy"]["conflict_detected"]:
                        st.error(data["finance_policy"]["violation_reason"])
                    else:
                        st.success("No policy conflict detected.")
                    st.write(data["final_decision"]["decision_summary"])
                with tabs[2]:
                    st.json(data)


def render_api_docs() -> None:
    st.markdown("<div class='section-title'>Developer API</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>This gives companies a direct integration story: register a workspace, issue an API key, and send decisions through a tenant-aware endpoint.</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        register = API_GUIDE["Register A Company"]
        st.markdown("<div class='api'>", unsafe_allow_html=True)
        st.markdown("<div class='eyebrow'>Endpoint</div>", unsafe_allow_html=True)
        st.markdown(f"### {register['method']}")
        st.code(json.dumps(register["body"], indent=2), language="json")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        run_api = API_GUIDE["Run A Policy-Aware Decision"]
        st.markdown("<div class='api'>", unsafe_allow_html=True)
        st.markdown("<div class='eyebrow'>Secure Endpoint</div>", unsafe_allow_html=True)
        st.markdown(f"### {run_api['method']}")
        st.code(json.dumps(run_api["headers"], indent=2), language="json")
        st.code(json.dumps(run_api["body"], indent=2), language="json")
        st.markdown("</div>", unsafe_allow_html=True)

    curl_example = dedent(
        """
        curl -X POST "https://your-backend-service.onrender.com/api/run" \
          -H "Content-Type: application/json" \
          -H "x-api-key: nexus_your_company_key" \
          -d '{
            "customer_name": "Acme Corp",
            "deal_size": 12000,
            "sales_context": "The customer wants a large incentive to close this week.",
            "max_discount_percent": 15
          }'
        """
    ).strip()
    st.markdown("<div class='section-title'>Copy-Paste Example</div>", unsafe_allow_html=True)
    st.code(curl_example, language="bash")


def render_use_cases() -> None:
    st.markdown("<div class='section-title'>Extensive Use Cases</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>These examples show how Nexus can be sold as horizontal infrastructure across multiple decision-heavy workflows.</p>", unsafe_allow_html=True)
    for use_case in USE_CASES:
        cols = st.columns([1.3, 1])
        with cols[0]:
            render_html_card(
                use_case["name"],
                (
                    f"{use_case['challenge']} Agent action: {use_case['agent_action']} "
                    f"Policy: {use_case['policy']} Nexus response: {use_case['system_response']} "
                    f"Outcome: {use_case['outcome']}"
                ),
                use_case["industry"],
                class_name="demo",
            )
        with cols[1]:
            render_html_card(
                "Launch Parameters",
                f"Customer: {use_case['customer_name']}. Deal size: ${use_case['deal_size']:,}. Max discount: {use_case['max_discount_percent']}%. Load this scenario into the company portal to demonstrate tenant-aware execution.",
                "Scenario",
            )
            if st.button(f"Prepare {use_case['name']}", key=f"scenario-{use_case['name']}"):
                set_scenario(use_case)
                st.success("Scenario loaded into the portal form.")


def render_knowledge_base() -> None:
    st.markdown("<div class='section-title'>Knowledge Base</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Built so founders, operators, and investors can understand the startup quickly.</p>", unsafe_allow_html=True)

    tabs = st.tabs(["Core Concepts", "FAQ", "Roadmap"])
    with tabs[0]:
        for title, paragraphs in KNOWLEDGE_BASE.items():
            st.markdown(
                f"""
                <div class="kb">
                    <h3 style="margin-top:0;">{title}</h3>
                    {''.join(f"<p class='muted'>{paragraph}</p>" for paragraph in paragraphs)}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")
    with tabs[1]:
        for question, answer in FAQ:
            with st.expander(question):
                st.write(answer)
    with tabs[2]:
        st.markdown(
            """
            - Add hosted authentication for company admins
            - Add Stripe subscriptions and billing webhooks
            - Add per-company policy bundles and audit logs
            - Add usage metering and monthly seat/API billing
            - Add multi-agent workflows beyond pricing
            """
        )


def main() -> None:
    inject_styles()
    init_state()

    st.markdown(
        """
        <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:0.8rem;">
            <div>
                <div class="eyebrow">Subscription SaaS MVP</div>
                <h1 style="margin:0.45rem 0 0.2rem 0;">Nexus Agentic OS</h1>
                <div class="nav-note">A globally deployable company portal for policy-aware AI decision infrastructure.</div>
            </div>
            <div class="pill">Mobile-friendly MVP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.segmented_control(
        "Navigate",
        options=["Home", "Pricing", "Company Portal", "API Docs", "Use Cases", "Knowledge Base"],
        default="Home",
    )

    if page == "Home":
        render_home()
    elif page == "Pricing":
        render_pricing()
    elif page == "Company Portal":
        render_portal()
    elif page == "API Docs":
        render_api_docs()
    elif page == "Use Cases":
        render_use_cases()
    elif page == "Knowledge Base":
        render_knowledge_base()


main()
