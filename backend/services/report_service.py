"""
GRAMTWIN - Report Generation Service
Generates downloadable CSV and comprehensive PDF analysis reports
containing satellite metrics, NDVI statistics, land cover distribution, and temporal changes.
"""

import io
import csv
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from backend.services.vegetation_service import compute_vegetation_analysis
from backend.services.landcover_service import predict_village_landcover
from backend.services.change_detection_service import analyze_temporal_changes
from backend.services.ai_analysis_service import generate_ai_analysis_summary

def generate_csv_report(village_id: str = "hiware_bazar"):
    """Generates a structured CSV report containing all computed satellite metrics."""
    veg = compute_vegetation_analysis(village_id, "t2")
    lc = predict_village_landcover(village_id, "t2")
    change = analyze_temporal_changes(village_id)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["GRAMTWIN AI - VILLAGE SATELLITE & VEGETATION INTELLIGENCE REPORT"])
    writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow(["Village Name", veg["village_name"]])
    writer.writerow(["Village ID", village_id])
    writer.writerow(["Sentinel-2 Acquisition Date", veg["date"]])
    writer.writerow(["Satellite Sensor", veg["satellite"]])
    writer.writerow([])

    # Section 1: Overview & Area
    writer.writerow(["--- SECTION 1: GEOGRAPHICAL & VEGETATION OVERVIEW ---"])
    writer.writerow(["Metric", "Value", "Unit"])
    writer.writerow(["Total Village Area", veg["stats"]["total_area_ha"], "Hectares"])
    writer.writerow(["Vegetation Coverage", veg["stats"]["vegetation_coverage_pct"], "%"])
    writer.writerow(["Healthy Vegetation (NDVI >= 0.66)", veg["stats"]["healthy_vegetation_pct"], "%"])
    writer.writerow(["Stressed / Low Vegetation (NDVI < 0.40)", veg["stats"]["stressed_vegetation_pct"], "%"])
    writer.writerow(["Mean NDVI", veg["stats"]["mean_ndvi"], "Index [-1 to 1]"])
    writer.writerow(["Min NDVI", veg["stats"]["min_ndvi"], "Index [-1 to 1]"])
    writer.writerow(["Max NDVI", veg["stats"]["max_ndvi"], "Index [-1 to 1]"])
    writer.writerow(["Std Dev NDVI", veg["stats"]["std_ndvi"], "Index"])
    writer.writerow(["Mean NDRE (Chlorophyll)", veg["stats"]["mean_ndre"], "Index"])
    writer.writerow(["Mean NDWI (Water Index)", veg["stats"]["mean_ndwi"], "Index"])
    writer.writerow(["Mean SAVI (Soil Adjusted)", veg["stats"]["mean_savi"], "Index"])
    writer.writerow([])

    # Section 2: NDVI Categories
    writer.writerow(["--- SECTION 2: VEGETATION HEALTH CLASSIFICATION ---"])
    writer.writerow(["Category", "NDVI Range", "Area (ha)", "Percentage (%)", "Pixel Count"])
    for cat in veg["categories"]:
        writer.writerow([cat["name"], cat["range"], cat["area_ha"], cat["percentage"], cat["pixels"]])
    writer.writerow([])

    # Section 3: Land Cover
    writer.writerow(["--- SECTION 3: LAND COVER CLASSIFICATION (U-NET AI) ---"])
    writer.writerow(["Class Name", "Area (ha)", "Percentage (%)", "Pixel Count"])
    for c in lc["classes"]:
        writer.writerow([c["name"], c["area_ha"], c["percentage"], c["pixel_count"]])
    writer.writerow([])

    # Section 4: Temporal Change Detection
    writer.writerow(["--- SECTION 4: TEMPORAL CHANGE DETECTION (T1 vs T2) ---"])
    writer.writerow(["Comparison Period", f"{change['t1']['date']} to {change['t2']['date']}"])
    writer.writerow(["Vegetation Gain", change["stats"]["vegetation_gain_ha"], "ha", f"+{change['stats']['vegetation_gain_pct']}%"])
    writer.writerow(["Vegetation Loss", change["stats"]["vegetation_loss_ha"], "ha", f"-{change['stats']['vegetation_loss_pct']}%"])
    writer.writerow(["Net Vegetation Change", change["stats"]["net_vegetation_change_ha"], "ha", f"{change['stats']['net_vegetation_change_pct']}%"])
    writer.writerow(["Built-up Area Increase", change["stats"]["builtup_increase_ha"], "ha", f"+{change['stats']['builtup_increase_pct']}%"])
    writer.writerow(["Stable Vegetation", change["stats"]["stable_vegetation_ha"], "ha", f"{change['stats']['stable_vegetation_pct']}%"])
    writer.writerow([])

    # Section 5: Hotspots
    writer.writerow(["--- SECTION 5: OPENCV VEGETATION STRESS HOTSPOTS ---"])
    writer.writerow(["Hotspot ID", "Severity", "Latitude", "Longitude", "Area (ha)", "Mean NDVI"])
    for h in veg["hotspots"]:
        writer.writerow([h["id"], h["severity"], h["coordinates"][0], h["coordinates"][1], h["area_ha"], h["mean_ndvi"]])

    return output.getvalue().encode("utf-8")

def generate_pdf_report(village_id: str = "hiware_bazar"):
    """
    Generates a professional multi-page PDF report using ReportLab.
    """
    veg = compute_vegetation_analysis(village_id, "t2")
    lc = predict_village_landcover(village_id, "t2")
    change = analyze_temporal_changes(village_id)
    ai = generate_ai_analysis_summary(village_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#064e3b')
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#047857')
    )
    heading_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )
    callout_style = ParagraphStyle(
        'DocCallout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569')
    )

    elements = []

    # Title Banner
    elements.append(Paragraph("GRAMTWIN AI — GEOSPATIAL INTELLIGENCE REPORT", title_style))
    elements.append(Paragraph(f"Village Scale Satellite Monitoring, Vegetation Health & Temporal Change Report — {veg['village_name']}", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#10b981'), spaceAfter=10))

    # Meta Table
    meta_data = [
        ["Village:", veg["village_name"], "Acquisition Date:", veg["date"]],
        ["Sensor:", veg["satellite"], "Resolution:", "10m / Pixel (Calibrated Sentinel-2)"],
        ["Total Area:", f"{veg['stats']['total_area_ha']} Hectares", "Coordinates:", f"{veg['coordinates'][0]} N, {veg['coordinates'][1]} E"]
    ]
    meta_table = Table(meta_data, colWidths=[1.1*inch, 2.3*inch, 1.3*inch, 2.3*inch])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#1e293b')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # Key Analytics Summary
    elements.append(Paragraph("1. EXECUTIVE ANALYTICAL SUMMARY", heading_style))
    sum_data = [
        ["Mean NDVI:", f"{veg['stats']['mean_ndvi']}", "Vegetation Coverage:", f"{veg['stats']['vegetation_coverage_pct']}%"],
        ["Healthy Canopy:", f"{veg['stats']['healthy_vegetation_pct']}%", "Moisture / Stress:", f"{veg['stats']['stressed_vegetation_pct']}%"],
        ["Mean NDRE (Chlorophyll):", f"{veg['stats']['mean_ndre']}", "Mean NDWI (Water):", f"{veg['stats']['mean_ndwi']}"],
        ["Temporal Net Veg Change:", f"{change['stats']['net_vegetation_change_ha']} ha ({change['stats']['net_vegetation_change_pct']}%)", "Built-up Expansion:", f"+{change['stats']['builtup_increase_ha']} ha"]
    ]
    sum_table = Table(sum_data, colWidths=[1.8*inch, 1.6*inch, 1.8*inch, 1.8*inch])
    sum_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#14532d')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bbf7d0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#86efac')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(sum_table)
    elements.append(Spacer(1, 12))

    # Land Cover Breakdown (U-Net AI)
    elements.append(Paragraph("2. DEEP LEARNING LAND-COVER SEGMENTATION (PyTorch U-Net)", heading_style))
    lc_table_data = [["Class Name", "Area (Hectares)", "Coverage (%)", "Pixel Count"]]
    for c in lc["classes"]:
        lc_table_data.append([c["name"], f"{c['area_ha']} ha", f"{c['percentage']}%", f"{c['pixel_count']:,}"])
    
    lc_table = Table(lc_table_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    lc_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#065f46')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(lc_table)
    elements.append(Spacer(1, 12))

    # Temporal Change Detection Table
    elements.append(Paragraph(f"3. TEMPORAL CHANGE DETECTION ({change['t1']['date']} vs {change['t2']['date']})", heading_style))
    ch_data = [
        ["Change Classification", "NDVI Difference Threshold", "Land Area", "Proportion"],
        ["Significant Vegetation Increase", "NDVI Change >= +0.25", f"{change['categories'][0]['area_ha']} ha", f"{change['categories'][0]['percentage']}%"],
        ["Moderate Vegetation Increase", "+0.10 <= NDVI Change < +0.25", f"{change['categories'][1]['area_ha']} ha", f"{change['categories'][1]['percentage']}%"],
        ["Relatively Stable Vegetation", "-0.10 <= NDVI Change < +0.10", f"{change['categories'][2]['area_ha']} ha", f"{change['categories'][2]['percentage']}%"],
        ["Moderate Vegetation Decrease", "-0.25 < NDVI Change <= -0.10", f"{change['categories'][3]['area_ha']} ha", f"{change['categories'][3]['percentage']}%"],
        ["Significant Vegetation Decrease", "NDVI Change <= -0.25", f"{change['categories'][4]['area_ha']} ha", f"{change['categories'][4]['percentage']}%"]
    ]
    ch_table = Table(ch_data, colWidths=[2.3*inch, 2.0*inch, 1.3*inch, 1.4*inch])
    ch_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(ch_table)
    elements.append(Spacer(1, 12))

    # AI Recommendations
    elements.append(Paragraph("4. ACTIONABLE AGRONOMIC & WATERSHED RECOMMENDATIONS", heading_style))
    for rec in ai["recommendations"]:
        rec_text = f"<b>[{rec['priority']} Priority] {rec['action']}:</b> {rec['details']}"
        elements.append(Paragraph(rec_text, body_style))
        elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 8))
    elements.append(Paragraph(ai["methodology_note"], callout_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
