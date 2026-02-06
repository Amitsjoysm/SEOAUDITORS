"""
Anomaly Detection Routes
View and manage detected anomalies
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from auth import get_current_user
from models import User, Audit, AnomalyDetection, AnomalyType, AnomalySeverity

router = APIRouter(prefix="/audits/{audit_id}/anomalies", tags=["Anomaly Detection"])


# Schemas
class AnomalyResponse(BaseModel):
    id: str
    anomaly_type: str
    severity: str
    detected_at: datetime
    metric_name: str | None
    expected_value: float | None
    actual_value: float | None
    deviation_percentage: float | None
    impact_assessment: str | None
    recommended_action: str | None
    is_resolved: bool
    resolved_at: datetime | None
    
    class Config:
        from_attributes = True


# Routes
@router.get("/", response_model=List[AnomalyResponse])
async def list_anomalies(
    audit_id: str,
    severity: AnomalySeverity | None = None,
    is_resolved: bool | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all anomalies for an audit"""
    # Verify audit belongs to user
    audit_result = await db.execute(
        select(Audit).where(
            Audit.id == audit_id,
            Audit.user_id == current_user.id
        )
    )
    audit = audit_result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Build query
    query = select(AnomalyDetection).where(AnomalyDetection.audit_id == audit_id)
    
    if severity:
        query = query.where(AnomalyDetection.severity == severity)
    
    if is_resolved is not None:
        query = query.where(AnomalyDetection.is_resolved == is_resolved)
    
    query = query.order_by(AnomalyDetection.severity.desc(), AnomalyDetection.detected_at.desc())
    
    result = await db.execute(query)
    anomalies = result.scalars().all()
    
    return [AnomalyResponse.from_orm(anomaly) for anomaly in anomalies]


@router.get("/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(
    audit_id: str,
    anomaly_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed anomaly information"""
    # Verify audit belongs to user
    audit_result = await db.execute(
        select(Audit).where(
            Audit.id == audit_id,
            Audit.user_id == current_user.id
        )
    )
    audit = audit_result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Get anomaly
    result = await db.execute(
        select(AnomalyDetection).where(
            AnomalyDetection.id == anomaly_id,
            AnomalyDetection.audit_id == audit_id
        )
    )
    anomaly = result.scalar_one_or_none()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    return AnomalyResponse.from_orm(anomaly)


@router.post("/{anomaly_id}/resolve")
async def resolve_anomaly(
    audit_id: str,
    anomaly_id: str,
    resolution_notes: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark an anomaly as resolved"""
    # Verify audit belongs to user
    audit_result = await db.execute(
        select(Audit).where(
            Audit.id == audit_id,
            Audit.user_id == current_user.id
        )
    )
    audit = audit_result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Get anomaly
    result = await db.execute(
        select(AnomalyDetection).where(
            AnomalyDetection.id == anomaly_id,
            AnomalyDetection.audit_id == audit_id
        )
    )
    anomaly = result.scalar_one_or_none()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    # Mark as resolved
    anomaly.is_resolved = True
    anomaly.resolved_at = datetime.utcnow()
    anomaly.resolved_by = current_user.id
    if resolution_notes:
        anomaly.resolution_notes = resolution_notes
    
    await db.commit()
    
    return {
        "message": "Anomaly marked as resolved",
        "anomaly_id": anomaly_id
    }


@router.post("/{anomaly_id}/dismiss")
async def dismiss_anomaly(
    audit_id: str,
    anomaly_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Dismiss a false positive anomaly"""
    # Verify audit belongs to user
    audit_result = await db.execute(
        select(Audit).where(
            Audit.id == audit_id,
            Audit.user_id == current_user.id
        )
    )
    audit = audit_result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Delete anomaly
    result = await db.execute(
        select(AnomalyDetection).where(
            AnomalyDetection.id == anomaly_id,
            AnomalyDetection.audit_id == audit_id
        )
    )
    anomaly = result.scalar_one_or_none()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    await db.delete(anomaly)
    await db.commit()
    
    return {
        "message": "Anomaly dismissed",
        "anomaly_id": anomaly_id
    }
