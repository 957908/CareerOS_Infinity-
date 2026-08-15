"""
JobScheduler / DailyJobPipeline — Autonomous daily pipeline scheduler with emergency stop controls.

INVARIANTS:
1. Daily processing limit (10/25/50) is a PREPARATION CEILING, not permission to auto-submit.
2. Emergency Stop IMMEDIATELY halts all discovery, preparation, and browser automation.
"""
import logging
import datetime
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job_discovery import JobPipelineControl, JobDiscoveryRun
from app.services.job_discovery_service import JobDiscoveryService
from app.services.job_orchestrator import JobOrchestrator

logger = logging.getLogger("app.services.job_scheduler")


class JobScheduler:
    """
    Manages daily job discovery pipelines and safety controls.
    """

    @staticmethod
    async def get_or_create_control(session: AsyncSession, user: User) -> JobPipelineControl:
        res = await session.execute(
            select(JobPipelineControl).filter(JobPipelineControl.user_id == user.id)
        )
        ctrl = res.scalars().first()
        if not ctrl:
            ctrl = JobPipelineControl(
                user_id=user.id,
                daily_processing_limit=25,
                is_paused=False,
                is_emergency_stopped=False,
            )
            session.add(ctrl)
            await session.commit()
        return ctrl

    @staticmethod
    async def set_emergency_stop(
        session: AsyncSession,
        user: User,
        reason: str = "User triggered emergency stop"
    ) -> Dict[str, Any]:
        ctrl = await JobScheduler.get_or_create_control(session, user)
        ctrl.is_emergency_stopped = True
        ctrl.emergency_stopped_at = datetime.datetime.utcnow()
        ctrl.emergency_stop_reason = reason
        await session.commit()
        logger.warning(f"EMERGENCY STOP ACTIVATED for user {user.id}: {reason}")
        return {
            "status": "EMERGENCY_STOPPED",
            "is_emergency_stopped": True,
            "emergency_stopped_at": ctrl.emergency_stopped_at.isoformat(),
            "reason": reason,
        }

    @staticmethod
    async def clear_emergency_stop(session: AsyncSession, user: User) -> Dict[str, Any]:
        ctrl = await JobScheduler.get_or_create_control(session, user)
        ctrl.is_emergency_stopped = False
        ctrl.emergency_stopped_at = None
        ctrl.emergency_stop_reason = None
        await session.commit()
        return {"status": "ACTIVE", "is_emergency_stopped": False}

    @staticmethod
    async def set_pause_state(session: AsyncSession, user: User, is_paused: bool) -> Dict[str, Any]:
        ctrl = await JobScheduler.get_or_create_control(session, user)
        ctrl.is_paused = is_paused
        await session.commit()
        return {"status": "PAUSED" if is_paused else "ACTIVE", "is_paused": is_paused}

    @staticmethod
    async def run_daily_pipeline(
        session: AsyncSession,
        user: User,
        query: str = "Backend Engineer",
        target_limit: int = 10
    ) -> Dict[str, Any]:
        ctrl = await JobScheduler.get_or_create_control(session, user)

        if ctrl.is_emergency_stopped:
            return {
                "status": "EMERGENCY_STOPPED",
                "error": "Pipeline blocked: Global Emergency Stop is active.",
                "emergency_stopped_at": ctrl.emergency_stopped_at.isoformat() if ctrl.emergency_stopped_at else None,
            }

        if ctrl.is_paused:
            return {"status": "PAUSED", "message": "Pipeline paused by candidate."}

        # Enforce daily processing limit
        limit = min(target_limit, ctrl.daily_processing_limit)

        # Run discovery
        disc_res = await JobDiscoveryService.run_discovery(
            session=session, user=user, query=query, sources=["mock"], max_jobs=limit
        )

        return {
            "status": "COMPLETED",
            "daily_limit_configured": ctrl.daily_processing_limit,
            "jobs_discovered": disc_res["jobs_discovered"],
            "jobs_qualified": disc_res["jobs_qualified"],
            "jobs_duplicate": disc_res["jobs_duplicate"],
            "requires_user_approval": True,
        }
