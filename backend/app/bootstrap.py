"""
Administrative CLI utility to bootstrap initial banker and applicant accounts into Supabase/PostgreSQL.

Usage:
    python -m backend.app.bootstrap

Expects standard environment variables:
    DATABASE_URL
    BOOTSTRAP_BANKER_EMAIL
    BOOTSTRAP_BANKER_PASSWORD
    BOOTSTRAP_BANKER_NAME (optional)
    BOOTSTRAP_APPLICANT_EMAIL
    BOOTSTRAP_APPLICANT_PASSWORD
    BOOTSTRAP_APPLICANT_NAME (optional)
"""
import asyncio
import sys

from backend.app.core.database import AsyncSessionLocal
from backend.app.services.bootstrap_service import bootstrap_initial_accounts


async def main():
    print("AgentTrust OS — Initial Account Bootstrap Utility")
    async with AsyncSessionLocal() as session:
        res = await bootstrap_initial_accounts(session)
        print(f"Bootstrap completed: {res}")


if __name__ == "__main__":
    asyncio.run(main())
