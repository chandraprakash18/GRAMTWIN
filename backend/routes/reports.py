"""
GRAMTWIN - Reports API Routes
Endpoints to download CSV and PDF reports.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.services.report_service import generate_csv_report, generate_pdf_report

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports Generation"]
)

@router.get("/download/csv")
def download_csv(village_id: str = "hiware_bazar"):
    """Generates and downloads a comprehensive CSV satellite intelligence report."""
    try:
        csv_bytes = generate_csv_report(village_id)
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=GRAMTWIN_{village_id}_report.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/pdf")
def download_pdf(village_id: str = "hiware_bazar"):
    """Generates and downloads a professional multi-page PDF geospatial analysis report."""
    try:
        pdf_bytes = generate_pdf_report(village_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=GRAMTWIN_{village_id}_analysis.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
