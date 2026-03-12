import json
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from .prompts import GENERATE_FINAL_REPORT_TEST1, GENERATE_FINAL_REPORT_TEST2


# Parse JSON from the original report_markdown string directly
report_markdown = GENERATE_FINAL_REPORT_TEST1

summary = GENERATE_FINAL_REPORT_TEST2

def convert_inline(text):
    text = text.replace('&', '&amp;')
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
    return text


def markdown_to_flowables(md_text):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('MyTitle', parent=styles['Title'],
                                 fontSize=22, spaceAfter=18,
                                 textColor=colors.HexColor('#1a3a5c'))
    h2_style = ParagraphStyle('MyH2', parent=styles['Heading2'],
                              fontSize=14, spaceBefore=14, spaceAfter=6,
                              textColor=colors.HexColor('#1a3a5c'))
    h3_style = ParagraphStyle('MyH3', parent=styles['Heading3'],
                              fontSize=11, spaceBefore=10, spaceAfter=4,
                              textColor=colors.HexColor('#2e6da4'))
    body_style = ParagraphStyle('MyBody', parent=styles['Normal'],
                                fontSize=10, leading=15, spaceAfter=6)
    bullet_style = ParagraphStyle('MyBullet', parent=styles['Normal'],
                                  fontSize=10, leading=14, spaceAfter=3,
                                  leftIndent=18)
    flowables = []
    for line in md_text.split('\n'):
        stripped = line.strip()
        if not stripped:
            flowables.append(Spacer(1, 5))
            continue
        if stripped == '---':
            flowables += [Spacer(1, 4),
                          HRFlowable(width='100%', thickness=0.5,
                                     color=colors.HexColor('#aaaaaa')),
                          Spacer(1, 4)]
            continue
        if stripped.startswith('# '):
            flowables.append(Paragraph(convert_inline(stripped[2:]), title_style))
            continue
        if stripped.startswith('## '):
            flowables.append(Paragraph(convert_inline(stripped[3:]), h2_style))
            continue
        if stripped.startswith('### '):
            flowables.append(Paragraph(convert_inline(stripped[4:]), h3_style))
            continue
        m = re.match(r'^[-*]\s+(.*)', stripped)
        if m:
            indent = len(line) - len(line.lstrip())
            bs = ParagraphStyle('Bul', parent=bullet_style, leftIndent=18 + indent)
            flowables.append(Paragraph('&#8226; ' + convert_inline(m.group(1)), bs))
            continue
        m = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if m:
            flowables.append(Paragraph(
                f"{m.group(1)}. {convert_inline(m.group(2))}", bullet_style))
            continue
        flowables.append(Paragraph(convert_inline(stripped), body_style))
    return flowables

def generate_pdf(md_text, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    doc.build(markdown_to_flowables(md_text))
    print(f"PDF saved: {output_path}")

