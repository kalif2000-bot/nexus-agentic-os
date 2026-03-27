import secrets
from datetime import UTC, datetime

from backend.app.db import get_db


def create_company(company_name: str, admin_email: str, plan: str) -> dict:
    api_key = f"nexus_{secrets.token_urlsafe(24)}"
    created_at = datetime.now(UTC).isoformat()

    with get_db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO companies (company_name, admin_email, plan, api_key, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (company_name, admin_email, plan, api_key, created_at),
        )
        company_id = cursor.lastrowid

    return {
        "id": company_id,
        "company_name": company_name,
        "admin_email": admin_email,
        "plan": plan,
        "api_key": api_key,
        "created_at": created_at,
    }


def get_company_by_id(company_id: int) -> dict | None:
    with get_db() as connection:
        row = connection.execute(
            """
            SELECT id, company_name, admin_email, plan, api_key, created_at
            FROM companies
            WHERE id = ?
            """,
            (company_id,),
        ).fetchone()

    return dict(row) if row else None


def get_company_by_api_key(api_key: str) -> dict | None:
    with get_db() as connection:
        row = connection.execute(
            """
            SELECT id, company_name, admin_email, plan, api_key, created_at
            FROM companies
            WHERE api_key = ?
            """,
            (api_key,),
        ).fetchone()

    return dict(row) if row else None
