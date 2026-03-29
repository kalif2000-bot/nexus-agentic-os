import json
import os
import sys
from pathlib import Path
from textwrap import dedent

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
            --surface: rgba(255, 251, 245, 0.84);
            --ink: #151515;
            --muted: #5b6168;
            --accent: #e5673b;
            --accent-2: #1f6f78;
            --border: rgba(21, 21, 21, 0.08);
            --shadow: 0 26px 72px rgba(28, 41, 61, 0.14);
        }
        .stApp {
            background:
                radial-gradient(circle at 0% 0%, rgba(244, 196, 96, 0.20), transparent 28%),
                radial-gradient(circle at 100% 8%, rgba(31, 111, 120, 0.18), transparent 30%),
                linear-gradient(180deg, #fcf7ef 0%, #f4eddf 48%, #f7f7f2 100%);
            color: var(--ink);
        }
        .block-container { max-width: 1240px; padding-top: 1.1rem; padding-bottom: 3rem; }
        .shell, .card, .metric, .pricing, .panel, .kb {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(8px);
        }
        .shell { padding: 2rem; position: relative; overflow: hidden; }
        .shell::after {
            content: "";
            position: absolute;
            right: -60px;
            bottom: -60px;
            width: 230px;
            height: 230px;
            background: radial-gradient(circle, rgba(229, 103, 59, 0.24), transparent 70%);
        }
        .card, .metric, .pricing, .panel, .kb { padding: 1.05rem 1.15rem; }
        .eyebrow {
            display: inline-block; padding: 0.36rem 0.68rem; border-radius: 999px;
            background: rgba(31, 111, 120, 0.10); color: var(--accent-2);
            font-weight: 700; font-size: 0.79rem; text-transform: uppercase; letter-spacing: 0.04em;
        }
        .hero-title { font-size: clamp(2.7rem, 5.8vw, 5rem); line-height: 0.92; margin: 1rem 0; font-weight: 850; }
        .muted, .hero-copy { color: var(--muted); line-height: 1.7; }
        .section-title { font-size: 2rem; font-weight: 800; margin-top: 1.35rem; margin-bottom: 0.2rem; }
        .pills { display:flex; flex-wrap: wrap; gap:0.55rem; margin-top: 1rem; }
        .pill { padding: 0.42rem 0.76rem; border-radius: 999px; background: rgba(21,21,21,0.06); font-size: 0.92rem; }
        .metric-label { text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em; color: var(--muted); }
        .metric-value { font-size: 1.95rem; font-weight: 800; margin-top: 0.2rem; }
        .price { font-size: 2.1rem; font-weight: 900; margin: 0.35rem 0; }
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            border: none; border-radius: 999px; background: linear-gradient(135deg, var(--accent), #f18a47);
            color: #fff; font-weight: 700; padding: 0.75rem 1.25rem; box-shadow: 0 14px 28px rgba(229,103,59,0.24);
        }
        .nav-note { margin-bottom: 0.8rem; color: var(--muted); }
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
    st.session_state.setdefault("auth_token", "")
    st.session_state.setdefault("workspace", None)
    st.session_state.setdefault("workspace_api_key", "")
    st.session_state.setdefault("decision_logs", [])


def auth_headers() -> dict:
    token = st.session_state.get("auth_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def render_html_card(title: str, body: str, eyebrow: str | None = None, class_name: str = "card") -> None:
    eyebrow_html = f"<div class='eyebrow'>{eyebrow}</div>" if eyebrow else ""
    st.markdown(
        f"""
        <div class="{class_name}">
            {eyebrow_html}
            <h3 style="margin-top:0.7rem;">{title}</h3>
            <p class="muted" style="margin-bottom:0;">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def api_request(method: str, path: str, payload: dict | None = None, headers: dict | None = None):
    try:
        response = requests.request(
            method=method,
            url=f"{API_BASE_URL}{path}",
            json=payload,
            headers=headers or {},
            timeout=60,
        )
        response.raise_for_status()
        if response.text:
            return response.json()
        return None
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")
        return None


def set_workspace(auth_response: dict) -> None:
    st.session_state["auth_token"] = auth_response["token"]
    st.session_state["workspace"] = auth_response["workspace"]
    api_keys = auth_response["workspace"].get("api_keys", [])
    st.session_state["workspace_api_key"] = api_keys[0]["api_key"] if api_keys else ""
    policy = auth_response["workspace"].get("policy")
    if policy:
        st.session_state["max_discount_percent"] = int(policy["max_discount_percent"])


def refresh_workspace() -> None:
    data = api_request("GET", "/workspace", headers=auth_headers())
    if data:
        st.session_state["workspace"] = data
        api_keys = data.get("api_keys", [])
        active = next((key["api_key"] for key in api_keys if key["is_active"] == 1), "")
        st.session_state["workspace_api_key"] = active


def refresh_decisions() -> None:
    data = api_request("GET", "/workspace/decisions", headers=auth_headers())
    if data is not None:
        st.session_state["decision_logs"] = data


def set_scenario(use_case: dict) -> None:
    st.session_state["selected_use_case"] = use_case["name"]
    st.session_state["customer_name"] = use_case["customer_name"]
    st.session_state["deal_size"] = float(use_case["deal_size"])
    st.session_state["sales_context"] = use_case["sales_context"]
    st.session_state["max_discount_percent"] = int(use_case["max_discount_percent"])


def render_home() -> None:
    st.markdown(
        """
        <div class="shell">
            <span class="eyebrow">Policy-Aware AI Infrastructure</span>
            <div class="hero-title">Nexus Agentic OS</div>
            <p class="hero-copy">
                Nexus helps companies deploy AI agents safely by enforcing business policy before any agent decision
                reaches a revenue workflow, refund system, approval chain, or customer-facing process.
            </p>
            <div class="pills">
                <div class="pill">Company workspaces</div>
                <div class="pill">Bearer-auth dashboard</div>
                <div class="pill">Tenant API keys</div>
                <div class="pill">Saved policies and decision logs</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    metrics = [
        ("Platform", "Control Layer", "Between agents and systems"),
        ("Core Modules", "5", "Auth, policy, keys, logs, API"),
        ("Primary Wedge", "Revenue Ops", "Pricing and approval controls"),
        ("Deployment", "Public SaaS", "Phone, tablet, desktop ready"),
    ]
    for col, (label, value, caption) in zip(cols, metrics):
        with col:
            st.markdown(
                f"<div class='metric'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='muted'>{caption}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='section-title'>What Companies Buy</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Companies don’t buy a chatbot here. They buy safe AI decisioning: API calls come in, Nexus checks policy, and business-safe outputs come back with an audit trail.</p>", unsafe_allow_html=True)
    feature_cols = st.columns(3)
    with feature_cols[0]:
        render_html_card("Decision Guardrails", "Enforce finance and operations policy before an agent recommendation becomes a real action.", "Core")
    with feature_cols[1]:
        render_html_card("Workspace Management", "Each company gets a tenant, dashboard, API keys, and editable policy settings.", "Core")
    with feature_cols[2]:
        render_html_card("Operational Visibility", "Every protected decision can be logged, reviewed, and explained to operators and leadership.", "Core")


def render_pricing() -> None:
    st.markdown("<div class='section-title'>Pricing</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>These plans are positioned for founder-led sales today and can later be tied to Stripe billing and usage enforcement.</p>", unsafe_allow_html=True)
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


def render_auth_portal() -> None:
    st.markdown("<div class='section-title'>Workspace Access</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Create a workspace for a company or log into an existing one. This is the operator surface your customers would use before integrating the API.</p>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        with st.form("signup_form"):
            company_name = st.text_input("Company Name")
            full_name = st.text_input("Admin Full Name")
            admin_email = st.text_input("Admin Email")
            password = st.text_input("Password", type="password")
            plan = st.selectbox("Plan", ["Starter", "Growth", "Enterprise"], index=1)
            submitted = st.form_submit_button("Create Workspace")

        if submitted:
            payload = {
                "company_name": company_name,
                "full_name": full_name,
                "admin_email": admin_email,
                "password": password,
                "plan": plan,
            }
            data = api_request("POST", "/auth/signup", payload=payload)
            if data:
                set_workspace(data)
                st.success("Workspace created and logged in.")
                refresh_decisions()

    with right:
        with st.form("login_form"):
            email = st.text_input("Workspace Email")
            password = st.text_input("Workspace Password", type="password")
            submitted = st.form_submit_button("Log In")

        if submitted:
            data = api_request("POST", "/auth/login", payload={"email": email, "password": password})
            if data:
                set_workspace(data)
                st.success("Logged into workspace.")
                refresh_decisions()

    if st.session_state.get("workspace"):
        workspace = st.session_state["workspace"]
        render_html_card(
            f"{workspace['company']['company_name']} is active",
            f"Logged in as {workspace['admin_user']['email']} on the {workspace['company']['plan']} plan.",
            "Session",
            class_name="panel",
        )


def render_workspace_dashboard() -> None:
    workspace = st.session_state.get("workspace")
    if not workspace:
        st.info("Create or log into a workspace first.")
        return

    refresh_workspace()
    refresh_decisions()
    workspace = st.session_state["workspace"]
    decisions = st.session_state.get("decision_logs", [])
    policy = workspace.get("policy")
    api_keys = workspace.get("api_keys", [])

    st.markdown("<div class='section-title'>Workspace Dashboard</div>", unsafe_allow_html=True)
    stats = st.columns(4)
    with stats[0]:
        st.metric("Company", workspace["company"]["company_name"])
    with stats[1]:
        st.metric("Plan", workspace["company"]["plan"])
    with stats[2]:
        st.metric("API Keys", len(api_keys))
    with stats[3]:
        st.metric("Logged Decisions", len(decisions))

    tabs = st.tabs(["Overview", "Policy", "API Keys", "Decision Sandbox", "Decision Logs"])

    with tabs[0]:
        cols = st.columns(2)
        with cols[0]:
            render_html_card(
                "Company Overview",
                f"Admin: {workspace['admin_user']['full_name']} ({workspace['admin_user']['email']}). Workspace created on {workspace['company']['created_at']}.",
                "Workspace",
                class_name="panel",
            )
        with cols[1]:
            render_html_card(
                "Active Policy",
                f"{policy['policy_name']} with max discount {policy['max_discount_percent']}%. Auto-correct is {'enabled' if policy['auto_correct'] else 'disabled'}.",
                "Policy",
                class_name="panel",
            )

    with tabs[1]:
        with st.form("policy_form"):
            policy_name = st.text_input("Policy Name", value=policy["policy_name"])
            max_discount_percent = st.slider("Max Discount Percent", min_value=0, max_value=100, value=int(policy["max_discount_percent"]))
            auto_correct = st.checkbox("Auto-correct unsafe decisions", value=bool(policy["auto_correct"]))
            escalation_message = st.text_area("Escalation Message", value=policy.get("escalation_message") or "", height=120)
            submitted = st.form_submit_button("Save Policy")

        if submitted:
            payload = {
                "policy_name": policy_name,
                "max_discount_percent": max_discount_percent,
                "auto_correct": auto_correct,
                "escalation_message": escalation_message,
            }
            data = api_request("PUT", "/workspace/policy", payload=payload, headers=auth_headers())
            if data:
                st.success("Policy updated.")
                refresh_workspace()

    with tabs[2]:
        key_cols = st.columns([1, 1.4])
        with key_cols[0]:
            with st.form("api_key_form"):
                label = st.text_input("New API Key Label", value="Staging Key")
                submitted = st.form_submit_button("Create API Key")
            if submitted:
                data = api_request("POST", "/workspace/api-keys", payload={"label": label}, headers=auth_headers())
                if data:
                    st.success("API key created.")
                    refresh_workspace()
        with key_cols[1]:
            for key in api_keys:
                st.markdown(f"**{key['label']}**  \n`{key['api_key']}`  \nStatus: {'active' if key['is_active'] else 'revoked'}")
                if key["is_active"] == 1 and st.button(f"Revoke {key['label']}", key=f"revoke-{key['id']}"):
                    api_request("DELETE", f"/workspace/api-keys/{key['id']}", headers=auth_headers())
                    refresh_workspace()
                    st.success("API key revoked.")

    with tabs[3]:
        scenario_names = [case["name"] for case in USE_CASES]
        selected_name = st.selectbox("Scenario", scenario_names, index=scenario_names.index(st.session_state["selected_use_case"]))
        selected_case = next(case for case in USE_CASES if case["name"] == selected_name)
        if st.button("Load Scenario", key="load-sandbox"):
            set_scenario(selected_case)

        c1, c2 = st.columns(2)
        with c1:
            customer_name = st.text_input("Customer Name", key="customer_name")
            deal_size = st.number_input("Deal Size ($)", min_value=100.0, step=500.0, key="deal_size")
            max_discount = st.slider("Max Discount (%)", 0, 100, key="max_discount_percent")
        with c2:
            sales_context = st.text_area("Sales Context", key="sales_context", height=160)
            api_key_input = st.text_input("Workspace API Key", value=st.session_state.get("workspace_api_key", ""), type="password")

        if st.button("Run Protected Decision", type="primary"):
            payload = {
                "customer_name": customer_name,
                "deal_size": deal_size,
                "sales_context": sales_context,
                "max_discount_percent": max_discount,
            }
            headers = {"x-api-key": api_key_input}
            data = api_request("POST", "/api/run", payload=payload, headers=headers)
            if data:
                st.success("Decision completed.")
                st.json(data)
                refresh_decisions()

    with tabs[4]:
        if not decisions:
            st.info("No decisions logged yet.")
        else:
            for row in decisions:
                render_html_card(
                    f"{row['customer_name']} — approved {row['approved_discount_percent']}%",
                    f"Suggested {row['suggested_discount_percent']}%. Conflict detected: {'yes' if row['conflict_detected'] else 'no'}. {row['decision_summary']}",
                    row["created_at"],
                    class_name="panel",
                )


def render_api_docs() -> None:
    st.markdown("<div class='section-title'>API Docs</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>These are the core APIs a customer integrates with in Nexus v2.</p>", unsafe_allow_html=True)

    docs_tabs = st.tabs(["Auth", "Workspace", "Protected Run", "cURL"])
    with docs_tabs[0]:
        st.markdown(f"### {API_GUIDE['Create Workspace']['method']}")
        st.code(json.dumps(API_GUIDE["Create Workspace"]["body"], indent=2), language="json")
        st.markdown(f"### {API_GUIDE['Login']['method']}")
        st.code(json.dumps(API_GUIDE["Login"]["body"], indent=2), language="json")
    with docs_tabs[1]:
        st.markdown("### GET /workspace")
        st.markdown("Header: `Authorization: Bearer <token>`")
        st.markdown("### PUT /workspace/policy")
        st.markdown("Header: `Authorization: Bearer <token>`")
        st.markdown("### POST /workspace/api-keys")
        st.markdown("Header: `Authorization: Bearer <token>`")
        st.markdown("### GET /workspace/decisions")
        st.markdown("Header: `Authorization: Bearer <token>`")
    with docs_tabs[2]:
        run_api = API_GUIDE["Run A Policy-Aware Decision"]
        st.markdown(f"### {run_api['method']}")
        st.code(json.dumps(run_api["headers"], indent=2), language="json")
        st.code(json.dumps(run_api["body"], indent=2), language="json")
    with docs_tabs[3]:
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
        st.code(curl_example, language="bash")


def render_use_cases() -> None:
    st.markdown("<div class='section-title'>Use Cases</div>", unsafe_allow_html=True)
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
                class_name="panel",
            )
        with cols[1]:
            render_html_card(
                "How It Plugs In",
                "Customer app -> Nexus API -> policy check -> approved action -> customer system. This pattern can govern pricing, refunds, procurement, and approvals.",
                "Integration",
                class_name="card",
            )


def render_knowledge_base() -> None:
    st.markdown("<div class='section-title'>Knowledge Base</div>", unsafe_allow_html=True)
    tabs = st.tabs(["Concepts", "FAQ", "Next Steps"])
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
            1. Add Stripe subscriptions and billing portal
            2. Move from SQLite to Postgres
            3. Add team invites and multi-user workspaces
            4. Add webhook integrations and Slack notifications
            5. Add more decision workflows beyond discount approval
            """
        )


def main() -> None:
    inject_styles()
    init_state()

    st.markdown(
        """
        <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:0.8rem;">
            <div>
                <div class="eyebrow">Nexus v2</div>
                <h1 style="margin:0.4rem 0 0.2rem 0;">Nexus Agentic OS</h1>
                <div class="nav-note">Workspace-ready AI control layer with auth, policy management, API keys, and decision history.</div>
            </div>
            <div class="pill">FastAPI + Streamlit SaaS MVP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.segmented_control(
        "Navigate",
        options=["Home", "Pricing", "Access", "Workspace", "API Docs", "Use Cases", "Knowledge Base"],
        default="Home",
    )

    if page == "Home":
        render_home()
    elif page == "Pricing":
        render_pricing()
    elif page == "Access":
        render_auth_portal()
    elif page == "Workspace":
        render_workspace_dashboard()
    elif page == "API Docs":
        render_api_docs()
    elif page == "Use Cases":
        render_use_cases()
    elif page == "Knowledge Base":
        render_knowledge_base()


main()
