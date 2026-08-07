"""
Generador de facturas peruanas sintéticas en PDF.
Sigue el formato de campos oficiales de Factura Electrónica 2.1 de SUNAT
(RUC 11 dígitos, serie F001-XXXXXXXX, IGV 18%), pero con datos 100%
inventados — no representa ninguna operación ni empresa real.

Uso: python generar_facturas.py
Genera los PDFs en ./facturas_sinteticas/
"""

import os
import random
from datetime import date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

OUT_DIR = "data/sample-invoices/sinteticas"
os.makedirs(OUT_DIR, exist_ok=True)

EMPRESAS_PROVEEDORAS = [
    {"razon_social": "ACEROS Y METALES DEL NORTE SAC", "ruc": "20501234567", "direccion": "Av. Industrial 845, Lurín, Lima"},
    {"razon_social": "CABLES Y CONDUCTORES INDUSTRIALES EIRL", "ruc": "20489765432", "direccion": "Jr. Los Talladores 220, Ate, Lima"},
    {"razon_social": "MAQUINARIAS PESADAS DEL SUR SA", "ruc": "20512398761", "direccion": "Carretera Panamericana Sur Km 18, Villa El Salvador"},
    {"razon_social": "SUMINISTROS ELECTRICOS ANDINOS SRL", "ruc": "20498761234", "direccion": "Av. Argentina 1450, Callao"},
]

CLIENTES = [
    {"razon_social": "CONSTRUCTORA ANDINA SAC", "ruc": "20603214569"},
    {"razon_social": "INVERSIONES METALMECANICAS DEL PERU SAC", "ruc": "20609874321"},
]

ITEMS_POOL = [
    ("Cable THW 4mm x 100m", "UND", 850.00),
    ("Plancha de acero corrugado 3mm", "UND", 320.50),
    ("Tubería PVC industrial 6\"", "UND", 145.00),
    ("Casco de seguridad certificado", "UND", 45.00),
    ("Guantes dieléctricos clase 2", "PAR", 78.90),
    ("Soldadora inverter 200A", "UND", 1250.00),
    ("Cemento portland tipo I (bolsa 42.5kg)", "BOL", 28.50),
    ("Varilla de acero corrugado 1/2\"", "UND", 32.80),
]


def generar_factura(numero_correlativo, proveedor, cliente):
    serie = "F001"
    correlativo = str(numero_correlativo).zfill(8)
    fecha_emision = date.today() - timedelta(days=random.randint(0, 60))

    items = random.sample(ITEMS_POOL, k=random.randint(2, 4))
    lineas = []
    subtotal = 0
    for desc, unidad, precio in items:
        cantidad = random.randint(2, 20)
        importe = round(cantidad * precio, 2)
        subtotal += importe
        lineas.append((desc, unidad, cantidad, precio, importe))

    igv = round(subtotal * 0.18, 2)
    total = round(subtotal + igv, 2)

    filename = f"{OUT_DIR}/{serie}-{correlativo}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # --- Encabezado ---
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, height - 25 * mm, proveedor["razon_social"])
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, height - 31 * mm, f"RUC: {proveedor['ruc']}")
    c.drawString(20 * mm, height - 36 * mm, proveedor["direccion"])

    c.rect(140 * mm, height - 40 * mm, 50 * mm, 22 * mm)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(165 * mm, height - 27 * mm, "FACTURA ELECTRÓNICA")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(165 * mm, height - 34 * mm, f"{serie}-{correlativo}")

    # --- Datos del cliente ---
    y = height - 50 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20 * mm, y, "CLIENTE:")
    c.setFont("Helvetica", 9)
    c.drawString(45 * mm, y, f"{cliente['razon_social']}  |  RUC: {cliente['ruc']}")
    y -= 5 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20 * mm, y, "FECHA EMISIÓN:")
    c.setFont("Helvetica", 9)
    c.drawString(50 * mm, y, fecha_emision.strftime("%d/%m/%Y"))
    y -= 5 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20 * mm, y, "MONEDA:")
    c.setFont("Helvetica", 9)
    c.drawString(50 * mm, y, "PEN - Soles")

    # --- Tabla de ítems ---
    y -= 12 * mm
    c.setFillColor(colors.whitesmoke)
    c.rect(20 * mm, y - 2 * mm, 170 * mm, 7 * mm, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(21 * mm, y, "DESCRIPCIÓN")
    c.drawString(110 * mm, y, "UNIDAD")
    c.drawString(130 * mm, y, "CANT.")
    c.drawString(150 * mm, y, "P. UNIT (S/)")
    c.drawString(175 * mm, y, "IMPORTE (S/)")

    y -= 8 * mm
    c.setFont("Helvetica", 8)
    for desc, unidad, cantidad, precio, importe in lineas:
        c.drawString(21 * mm, y, desc[:45])
        c.drawString(110 * mm, y, unidad)
        c.drawString(132 * mm, y, str(cantidad))
        c.drawRightString(168 * mm, y, f"{precio:,.2f}")
        c.drawRightString(190 * mm, y, f"{importe:,.2f}")
        y -= 6 * mm

    # --- Totales ---
    y -= 6 * mm
    c.line(130 * mm, y, 190 * mm, y)
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    c.drawString(140 * mm, y, "Op. Gravada:")
    c.drawRightString(190 * mm, y, f"S/ {subtotal:,.2f}")
    y -= 5.5 * mm
    c.drawString(140 * mm, y, "IGV (18%):")
    c.drawRightString(190 * mm, y, f"S/ {igv:,.2f}")
    y -= 6 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(140 * mm, y, "IMPORTE TOTAL:")
    c.drawRightString(190 * mm, y, f"S/ {total:,.2f}")

    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.grey)
    c.drawString(20 * mm, 15 * mm, "Documento sintético generado con fines de prueba — no representa una operación real.")

    c.save()
    return filename, {
        "serie_correlativo": f"{serie}-{correlativo}",
        "ruc_proveedor": proveedor["ruc"],
        "razon_social_proveedor": proveedor["razon_social"],
        "ruc_cliente": cliente["ruc"],
        "fecha_emision": fecha_emision.isoformat(),
        "subtotal": subtotal,
        "igv": igv,
        "total": total,
        "items": [{"descripcion": d, "unidad": u, "cantidad": c_, "precio_unitario": p, "importe": i} for d, u, c_, p, i in lineas],
    }


if __name__ == "__main__":
    import json
    referencias = []
    for i in range(1, 20):
        proveedor = random.choice(EMPRESAS_PROVEEDORAS)
        cliente = random.choice(CLIENTES)
        filename, data = generar_factura(i, proveedor, cliente)
        referencias.append(data)
        print(f"Generado: {filename}  (Total: S/ {data['total']:.2f})")

    with open(f"{OUT_DIR}/_referencia_ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(referencias, f, indent=2, ensure_ascii=False)

    print(f"\n{len(referencias)} facturas generadas en ./{OUT_DIR}/")
    print("Incluye _referencia_ground_truth.json con los datos reales de cada una,")
    print("para comparar contra lo que extraiga tu IA.")