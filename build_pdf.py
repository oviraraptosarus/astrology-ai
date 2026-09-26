import sys, os, json
sys.path.insert(0, r"E:\ASTROLOGY AI")

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def create_pdf(json_path, out_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)

    doc = SimpleDocTemplate(out_path, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # Custom heading styles
    styles.add(ParagraphStyle(name='H1', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='H2', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=10, textColor=colors.indigo))
    styles.add(ParagraphStyle(name='Body', parent=styles['Normal'], fontSize=11, leading=16, spaceAfter=12))

    story = []
    
    story.append(Paragraph(spec.get("title", ""), styles['H1']))
    
    for el in spec.get("elements", []):
        if el["type"] == "heading":
            sty = 'H1' if el.get("level") == 1 else 'H2'
            story.append(Paragraph(el["text"], styles[sty]))
        elif el["type"] == "paragraph":
            text = el["text"].replace('\n', '<br/>')
            story.append(Paragraph(text, styles['Body']))
        elif el["type"] == "table":
            data = el["data"]
            t = Table(data, colWidths=[60, 60, 50, 40, 150, 90])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f0f0f0")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('BACKGROUND', (0,1), (-1,-1), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
            ]))
            story.append(t)
            story.append(Spacer(1, 12))

    doc.build(story)
    print("Done")

create_pdf(r"E:\ASTROLOGY AI\her_psych_blueprint.json", r"E:\ASTROLOGY AI\Her_Psychological_Blueprint.pdf")
