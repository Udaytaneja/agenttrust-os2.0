import logging
import os
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import hash_password
from backend.app.models.user import User

logger = logging.getLogger("agenttrust.bootstrap")


async def bootstrap_initial_accounts(db: AsyncSession) -> dict[str, bool]:
    """
    Idempotent, controlled account bootstrap routine.
    Only creates accounts when the corresponding BOOTSTRAP_* environment variables
    are explicitly configured.
    Does NOT overwrite existing accounts or alter existing passwords.
    Never prints or logs password values.
    """
    results = {"banker_created": False, "applicant_created": False}

    # 1. Banker Bootstrap
    banker_email = os.getenv("BOOTSTRAP_BANKER_EMAIL", "").strip().lower()
    banker_password = os.getenv("BOOTSTRAP_BANKER_PASSWORD", "")
    banker_name = os.getenv("BOOTSTRAP_BANKER_NAME", "Vikram Singh").strip()

    if banker_email and banker_password:
        res = await db.execute(select(User).where(User.email == banker_email))
        existing_banker = res.scalar_one_or_none()
        if existing_banker is None:
            new_banker = User(
                name=banker_name,
                email=banker_email,
                hashed_password=hash_password(banker_password),
                phone=os.getenv("BOOTSTRAP_BANKER_PHONE", "+1 (212) 555-0199"),
                role="banker",
                language="en",
                is_active=True,
                is_verified=True,
            )
            db.add(new_banker)
            await db.commit()
            results["banker_created"] = True
            logger.info("Admin bootstrap: Initial banker account provisioned successfully.")
        else:
            logger.info("Admin bootstrap: Banker account already exists, skipping creation.")

    # 2. Applicant Bootstrap
    applicant_email = os.getenv("BOOTSTRAP_APPLICANT_EMAIL", "").strip().lower()
    applicant_password = os.getenv("BOOTSTRAP_APPLICANT_PASSWORD", "")
    applicant_name = os.getenv("BOOTSTRAP_APPLICANT_NAME", "Alex Mercer").strip()

    if applicant_email and applicant_password:
        res = await db.execute(select(User).where(User.email == applicant_email))
        existing_applicant = res.scalar_one_or_none()
        if existing_applicant is None:
            new_applicant = User(
                name=applicant_name,
                email=applicant_email,
                hashed_password=hash_password(applicant_password),
                phone=os.getenv("BOOTSTRAP_APPLICANT_PHONE", "+1 (415) 555-0142"),
                role="user",
                language="en",
                is_active=True,
                is_verified=True,
            )
            db.add(new_applicant)
            await db.commit()
            results["applicant_created"] = True
            logger.info("Admin bootstrap: Initial applicant account provisioned successfully.")
        else:
            logger.info("Admin bootstrap: Applicant account already exists, skipping creation.")

    return results
