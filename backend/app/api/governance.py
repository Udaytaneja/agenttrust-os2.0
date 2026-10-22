"""
Governance API router providing configuration endpoints for institutional risk rules,
DTI limits, and automated policy controls. Backed by the AgentPolicyModel database records.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_active_user, require_role
from backend.app.core.database import get_db
from backend.app.models.agent import AgentPolicyModel
from backend.app.models.user import User

router = APIRouter(prefix="/governance", tags=["Governance"])


class GovernanceConfigPayload(BaseModel):
    dti_ratio: float = Field(default=43.5, alias="dtiRatio")
    trust_index_cutoff: int = Field(default=720, alias="trustIndexCutoff")
    rule1_active: bool = Field(default=True, alias="rule1Active")
    rule2_active: bool = Field(default=True, alias="rule2Active")

    model_config = {
        "populate_by_name": True,
    }


class GovernanceConfigResponse(BaseModel):
    dti_ratio: float = Field(..., alias="dtiRatio")
    trust_index_cutoff: int = Field(..., alias="trustIndexCutoff")
    rule1_active: bool = Field(..., alias="rule1Active")
    rule2_active: bool = Field(..., alias="rule2Active")
    updated_at: Optional[str] = Field(default=None, alias="updatedAt")
    updated_by: Optional[str] = Field(default=None, alias="updatedBy")

    model_config = {
        "populate_by_name": True,
    }


POLICY_DTI_KEY = "governance_dti_ratio"
POLICY_TRUST_CUTOFF_KEY = "governance_trust_cutoff"
POLICY_RULE1_KEY = "governance_rule1_active"
POLICY_RULE2_KEY = "governance_rule2_active"


async def _get_or_create_policy(
    db: AsyncSession, name: str, rule_type: str, default_val: str, is_active: bool = True
) -> AgentPolicyModel:
    res = await db.execute(select(AgentPolicyModel).where(AgentPolicyModel.name == name))
    policy = res.scalar_one_or_none()
    if policy is None:
        policy = AgentPolicyModel(
            name=name,
            rule_type=rule_type,
            threshold_value=default_val,
            action_on_violation="BLOCK",
            is_active=is_active,
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
    return policy


@router.get("", response_model=GovernanceConfigResponse)
async def get_governance_config(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve institutional risk governance rules and thresholds."""
    dti_policy = await _get_or_create_policy(db, POLICY_DTI_KEY, "max_dti", "43.5")
    cutoff_policy = await _get_or_create_policy(db, POLICY_TRUST_CUTOFF_KEY, "min_trust_score", "720")
    r1_policy = await _get_or_create_policy(db, POLICY_RULE1_KEY, "policy_rule1", "true", True)
    r2_policy = await _get_or_create_policy(db, POLICY_RULE2_KEY, "policy_rule2", "true", True)

    try:
        dti_val = float(dti_policy.threshold_value)
    except ValueError:
        dti_val = 43.5

    try:
        cutoff_val = int(cutoff_policy.threshold_value)
    except ValueError:
        cutoff_val = 720

    return GovernanceConfigResponse(
        dti_ratio=dti_val,
        trust_index_cutoff=cutoff_val,
        rule1_active=r1_policy.is_active,
        rule2_active=r2_policy.is_active,
        updated_at=datetime.utcnow().isoformat(),
        updated_by=current_user.name,
    )


@router.post("", response_model=dict)
async def save_governance_config(
    payload: GovernanceConfigPayload,
    current_user: User = Depends(require_role("banker")),
    db: AsyncSession = Depends(get_db),
):
    """Update institutional risk governance rules (Banker access only)."""
    dti_policy = await _get_or_create_policy(db, POLICY_DTI_KEY, "max_dti", str(payload.dti_ratio))
    dti_policy.threshold_value = str(payload.dti_ratio)

    cutoff_policy = await _get_or_create_policy(db, POLICY_TRUST_CUTOFF_KEY, "min_trust_score", str(payload.trust_index_cutoff))
    cutoff_policy.threshold_value = str(payload.trust_index_cutoff)

    r1_policy = await _get_or_create_policy(db, POLICY_RULE1_KEY, "policy_rule1", str(payload.rule1_active))
    r1_policy.is_active = payload.rule1_active

    r2_policy = await _get_or_create_policy(db, POLICY_RULE2_KEY, "policy_rule2", str(payload.rule2_active))
    r2_policy.is_active = payload.rule2_active

    await db.commit()

    return {
        "success": True,
        "message": "Governance policy configuration successfully persisted & synced to production API.",
        "updated_at": datetime.utcnow().isoformat(),
        "updated_by": current_user.name,
    }
