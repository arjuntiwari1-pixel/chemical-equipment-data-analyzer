from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import FileResponse
import io

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Dataset

import csv
from collections import Counter
from datetime import datetime


@csrf_exempt
@api_view(["POST"])
def upload_csv(request):
    print("=== UPLOAD HIT ===")

    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    decoded = file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)

    rows = []
    flowrates, pressures, temperatures, types = [], [], [], []

    for idx, row in enumerate(reader, start=1):
        try:
            r = {
                "id": idx,  # auto ID
                "name": row["Equipment Name"],
                "type": row["Type"],
                "flowrate": float(row["Flowrate"]),
                "pressure": float(row["Pressure"]),
                "temperature": float(row["Temperature"]),
            }
        except KeyError as e:
            print("CSV COLUMN MISSING:", e)
            return Response(
                {"error": f"Missing column in CSV: {str(e)}"}, status=400
            )

        rows.append(r)
        flowrates.append(r["flowrate"])
        pressures.append(r["pressure"])
        temperatures.append(r["temperature"])
        types.append(r["type"])

    if not rows:
        return Response({"error": "Empty CSV"}, status=400)

    total = len(rows)

    avg_flow = round(sum(flowrates) / total, 2)
    avg_pressure = round(sum(pressures) / total, 2)
    avg_temp = round(sum(temperatures) / total, 2)

    min_temp = min(temperatures)
    max_temp = max(temperatures)

    dataset = Dataset.objects.create(
        filename=file.name,
        total_equipment=total,
        avg_flowrate=avg_flow,
        max_pressure=max(pressures),
        min_temperature=min_temp,
        max_temperature=max_temp,
        uploaded_at=datetime.utcnow(),
    )

    # keep only last 5
    old = Dataset.objects.order_by("-uploaded_at")[5:]
    if old:
        Dataset.objects.filter(id__in=[d.id for d in old]).delete()

    return Response({
        "summary": {
            "total_equipment": total,
            "avg_flowrate": avg_flow,
            "max_pressure": max(pressures),
            "temperature_range": [min_temp, max_temp],
        },
        "averages": {
            "flowrate": avg_flow,
            "pressure": avg_pressure,
            "temperature": avg_temp,
        },
        "type_distribution": dict(Counter(types)),
        "rows": rows,
    })


@api_view(["GET"])
def upload_history(request):
    datasets = Dataset.objects.order_by("-uploaded_at")[:5]
    return Response([
        {
            "id": d.id,
            "filename": d.filename,
            "total_equipment": d.total_equipment,
            "avg_flowrate": d.avg_flowrate,
            "max_pressure": d.max_pressure,
            "uploaded_at": d.uploaded_at,
        }
        for d in datasets
    ])

@api_view(["GET"])
def download_report_pdf(request):
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y, "Chemical Equipment Analysis Report")
    y -= 40

    # Fetch latest dataset
    dataset = Dataset.objects.order_by("-uploaded_at").first()

    if not dataset:
        p.drawString(50, y, "No data available")
    else:
        p.setFont("Helvetica", 12)

        p.drawString(50, y, f"Filename: {dataset.filename}")
        y -= 25
        p.drawString(50, y, f"Total Equipment: {dataset.total_equipment}")
        y -= 20
        p.drawString(50, y, f"Avg Flowrate: {dataset.avg_flowrate}")
        y -= 20
        p.drawString(50, y, f"Max Pressure: {dataset.max_pressure}")
        y -= 20
        p.drawString(
            50, y,
            f"Temperature Range: {dataset.min_temperature} – {dataset.max_temperature}"
        )
        y -= 30

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Summary")
        y -= 20

        p.setFont("Helvetica", 11)
        p.drawString(50, y, "This report was generated automatically by the system.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename="equipment_analysis_report.pdf"
    )
