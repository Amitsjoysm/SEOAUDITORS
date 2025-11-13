"""Report generation and download routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import os
from pathlib import Path

from database import get_db
from models import User, Audit, AuditResult
from auth import get_current_user
from utils.report_generator import generate_pdf_report, generate_docx_report

router = APIRouter(prefix="/reports", tags=["Reports"])
logger = logging.getLogger(__name__)

# Reports directory
REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


@router.get("/{audit_id}/pdf")
async def download_pdf_report(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate and download PDF report for an audit"""
    # Verify audit access
    result = await db.execute(
        select(Audit).where(Audit.id == audit_id)
    )
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    if audit.user_id != current_user.id and current_user.role != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this audit"
        )
    
    if audit.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audit not yet completed"
        )
    
    # Get audit results
    result = await db.execute(
        select(AuditResult)
        .where(AuditResult.audit_id == audit_id)
        .order_by(AuditResult.category, AuditResult.impact_score.desc())
    )
    results = result.scalars().all()
    
    # Generate PDF
    try:
        pdf_path = await generate_pdf_report(audit, results, REPORTS_DIR)
        
        # Update audit with PDF path
        audit.report_pdf_path = str(pdf_path)
        await db.commit()
        
        # Return file for download
        filename = f"SEO_Audit_{audit.website_url.replace('https://', '').replace('http://', '').replace('/', '_')}_{audit_id[:8]}.pdf"
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF report: {str(e)}"
        )


@router.get("/{audit_id}/docx")
async def download_docx_report(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate and download DOCX report for an audit"""
    # Verify audit access
    result = await db.execute(
        select(Audit).where(Audit.id == audit_id)
    )
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    if audit.user_id != current_user.id and current_user.role != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this audit"
        )
    
    if audit.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audit not yet completed"
        )
    
    # Get audit results
    result = await db.execute(
        select(AuditResult)
        .where(AuditResult.audit_id == audit_id)
        .order_by(AuditResult.category, AuditResult.impact_score.desc())
    )
    results = result.scalars().all()
    
    # Generate DOCX
    try:
        docx_path = await generate_docx_report(audit, results, REPORTS_DIR)
        
        # Update audit with DOCX path
        audit.report_docx_path = str(docx_path)
        await db.commit()
        
        # Return file for download
        filename = f"SEO_Audit_{audit.website_url.replace('https://', '').replace('http://', '').replace('/', '_')}_{audit_id[:8]}.docx"
        
        return FileResponse(
            path=docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating DOCX report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating DOCX report: {str(e)}"
        )
