import hashlib
import secrets
from datetime import UTC, datetime

from backend.app.db import get_db


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_company_with_admin(
    company_name: str,
    admin_email: str,
    full_name: str,
    password: str,
    plan: str,
) -> dict:
    created_at = _timestamp()
    password_hash = hash_password(password)
    api_key = f"nexus_{secrets.token_urlsafe(24)}"

    with get_db() as connection:
        company_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(companies)").fetchall()
        }
        if "api_key" in company_columns:
            cursor = connection.execute(
                """
                INSERT INTO companies (company_name, admin_email, plan, api_key, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (company_name, admin_email, plan, api_key, created_at),
            )
        else:
            cursor = connection.execute(
                """
                INSERT INTO companies (company_name, admin_email, plan, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (company_name, admin_email, plan, created_at),
            )
        company_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO users (company_id, full_name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (company_id, full_name, admin_email, password_hash, created_at),
        )

        connection.execute(
            """
            INSERT INTO api_keys (company_id, label, api_key, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (company_id, "Primary Production Key", api_key, created_at),
        )

        connection.execute(
            """
            INSERT INTO policies (
                company_id, policy_name, max_discount_percent, auto_correct, escalation_message, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company_id,
                "Default Revenue Policy",
                15.0,
                1,
                "Escalate to finance leadership when an AI recommendation exceeds the configured discount ceiling.",
                created_at,
                created_at,
            ),
        )

    return get_company_workspace(company_id)


def authenticate_user(email: str, password: str) -> dict | None:
    password_hash = hash_password(password)
    with get_db() as connection:
        row = connection.execute(
            """
            SELECT
                users.id AS user_id,
                users.company_id,
                users.full_name,
                users.email,
                companies.company_name,
                companies.admin_email,
                companies.plan,
                companies.created_at
            FROM users
            JOIN companies ON companies.id = users.company_id
            WHERE users.email = ? AND users.password_hash = ?
            """,
            (email, password_hash),
        ).fetchone()
        if not row:
            return None

        token = f"nexus_session_{secrets.token_urlsafe(24)}"
        connection.execute(
            """
            INSERT INTO sessions (user_id, token, created_at)
            VALUES (?, ?, ?)
            """,
            (row["user_id"], token, _timestamp()),
        )

    return {"token": token, "workspace": get_company_workspace(row["company_id"])}


def get_workspace_by_session(token: str) -> dict | None:
    with get_db() as connection:
        row = connection.execute(
            """
            SELECT users.company_id
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (token,),
        ).fetchone()
    if not row:
        return None
    return get_company_workspace(row["company_id"])


def get_company_workspace(company_id: int) -> dict | None:
    with get_db() as connection:
        company = connection.execute(
            """
            SELECT id, company_name, admin_email, plan, created_at
            FROM companies
            WHERE id = ?
            """,
            (company_id,),
        ).fetchone()
        if not company:
            return None

        admin = connection.execute(
            """
            SELECT id, full_name, email, created_at
            FROM users
            WHERE company_id = ?
            ORDER BY id ASC
            LIMIT 1
            """,
            (company_id,),
        ).fetchone()

        policy = connection.execute(
            """
            SELECT id, policy_name, max_discount_percent, auto_correct, escalation_message, created_at, updated_at
            FROM policies
            WHERE company_id = ?
            """,
            (company_id,),
        ).fetchone()

        api_keys = connection.execute(
            """
            SELECT id, label, api_key, is_active, created_at
            FROM api_keys
            WHERE company_id = ?
            ORDER BY id DESC
            """,
            (company_id,),
        ).fetchall()

    return {
        "company": dict(company),
        "admin_user": dict(admin) if admin else None,
        "policy": dict(policy) if policy else None,
        "api_keys": [dict(row) for row in api_keys],
    }


def get_company_by_api_key(api_key: str) -> dict | None:
    with get_db() as connection:
        row = connection.execute(
            """
            SELECT companies.id, companies.company_name, companies.admin_email, companies.plan, companies.created_at
            FROM api_keys
            JOIN companies ON companies.id = api_keys.company_id
            WHERE api_keys.api_key = ? AND api_keys.is_active = 1
            """,
            (api_key,),
        ).fetchone()
    return dict(row) if row else None


def create_api_key(company_id: int, label: str) -> dict:
    api_key = f"nexus_{secrets.token_urlsafe(24)}"
    created_at = _timestamp()
    with get_db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO api_keys (company_id, label, api_key, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (company_id, label, api_key, created_at),
        )
    return {
        "id": cursor.lastrowid,
        "label": label,
        "api_key": api_key,
        "is_active": 1,
        "created_at": created_at,
    }


def revoke_api_key(company_id: int, key_id: int) -> None:
    with get_db() as connection:
        connection.execute(
            """
            UPDATE api_keys
            SET is_active = 0
            WHERE id = ? AND company_id = ?
            """,
            (key_id, company_id),
        )


def update_policy(
    company_id: int,
    policy_name: str,
    max_discount_percent: float,
    auto_correct: bool,
    escalation_message: str,
) -> dict:
    updated_at = _timestamp()
    with get_db() as connection:
        connection.execute(
            """
            UPDATE policies
            SET policy_name = ?, max_discount_percent = ?, auto_correct = ?, escalation_message = ?, updated_at = ?
            WHERE company_id = ?
            """,
            (
                policy_name,
                max_discount_percent,
                1 if auto_correct else 0,
                escalation_message,
                updated_at,
                company_id,
            ),
        )
        policy = connection.execute(
            """
            SELECT id, policy_name, max_discount_percent, auto_correct, escalation_message, created_at, updated_at
            FROM policies
            WHERE company_id = ?
            """,
            (company_id,),
        ).fetchone()
    return dict(policy)


def create_decision_log(
    company_id: int,
    customer_name: str,
    deal_size: float,
    sales_context: str,
    requested_max_discount_percent: float,
    suggested_discount_percent: float,
    approved_discount_percent: float,
    conflict_detected: bool,
    sales_raw_text: str,
    sales_reasoning: str,
    decision_summary: str,
) -> dict:
    created_at = _timestamp()
    with get_db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO decisions (
                company_id, customer_name, deal_size, sales_context, requested_max_discount_percent,
                suggested_discount_percent, approved_discount_percent, conflict_detected, sales_raw_text,
                sales_reasoning, decision_summary, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company_id,
                customer_name,
                deal_size,
                sales_context,
                requested_max_discount_percent,
                suggested_discount_percent,
                approved_discount_percent,
                1 if conflict_detected else 0,
                sales_raw_text,
                sales_reasoning,
                decision_summary,
                created_at,
            ),
        )
    return {
        "id": cursor.lastrowid,
        "created_at": created_at,
    }


def list_decisions(company_id: int) -> list[dict]:
    with get_db() as connection:
        rows = connection.execute(
            """
            SELECT id, customer_name, deal_size, sales_context, requested_max_discount_percent,
                   suggested_discount_percent, approved_discount_percent, conflict_detected,
                   sales_raw_text, sales_reasoning, decision_summary, created_at
            FROM decisions
            WHERE company_id = ?
            ORDER BY id DESC
            """,
            (company_id,),
        ).fetchall()
    return [dict(row) for row in rows]
