import json
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

# Parse JSON from the original report_markdown string directly
report_markdown = """# Medical Report

## Table of Contents
1. Overview
2. Clinical Findings
3. Supporting Evidence
   - 3.1 Etiology and Epidemiology
   - 3.2 Diagnostic Indicators
   - 3.3 Laboratory Markers and Severity
   - 3.4 Radiographic Findings
   - 3.5 Severity Assessment and Risk Stratification
   - 3.6 Treatment Considerations
   - 3.7 Supportive Care
4. Discrepancies or Limitations
5. Conclusion
6. References

---

## 1. Overview
The patient presents with **community-acquired pneumonia (CAP)** caused by *Streptococcus pneumoniae*. Clinical manifestations include fever (39.2°C), productive cough with rust-colored sputum, right lower lobe consolidation on chest X-ray, and elevated inflammatory markers (CRP 142 mg/L and WBC 14,500/μL). Oxygen saturation is 94% on room air, and the Pneumonia Severity Index (PSI) places the patient in **Risk Class III**, suggesting moderate disease severity.

Community-acquired pneumonia is one of the most common infectious diseases worldwide, with *Streptococcus pneumoniae* being the most frequently identified pathogen when a causative organism is detected (Mandell et al., 2007).

---

## 2. Clinical Findings
The patient's presentation includes several classical findings consistent with pneumococcal pneumonia:

- **High fever (39.2°C)** indicating systemic inflammatory response
- **Productive cough with rust-colored sputum**
- **Elevated inflammatory markers:**
  - C-reactive protein (CRP): 142 mg/L
  - White blood cell count: 14,500/μL
- **Chest radiograph:** right lower lobe consolidation
- **Oxygen saturation:** 94% on room air
- **PSI Risk Class III** indicating moderate severity

These findings collectively support the diagnosis of bacterial community-acquired pneumonia.

---

## 3. Supporting Evidence

### 3.1 Etiology and Epidemiology
*Streptococcus pneumoniae* is the most common cause of community-acquired pneumonia in adults, responsible for up to 35% of identified cases (Mandell et al., 2007). This epidemiological evidence supports the likelihood of pneumococcus as the causative organism in patients presenting with typical bacterial CAP features.

### 3.2 Diagnostic Indicators
The presence of **rust-colored sputum** is a classic clinical feature of pneumococcal pneumonia. This phenomenon occurs due to red blood cell leakage into the alveolar spaces during the consolidation phase of infection (Musher and Thorner, 2014). The patient's sputum characteristics therefore strongly support pneumococcal etiology.

### 3.3 Laboratory Markers and Severity
The patient's **CRP level of 142 mg/L** is markedly elevated. CRP levels above 100 mg/L at admission have been associated with bacteremic pneumococcal pneumonia and correlate with increased disease severity and risk of complications (Torres et al., 2013).

### 3.4 Radiographic Findings
Chest radiography demonstrates **right lower lobe consolidation**, a pattern commonly associated with bacterial pneumonia rather than atypical pathogens. Lobar or segmental consolidation is strongly linked to bacterial infection, and right lower lobe involvement is frequently observed in pneumococcal pneumonia (Wunderink and Waterer, 2014).

### 3.5 Severity Assessment and Risk Stratification
Severity assessment tools such as the **Pneumonia Severity Index (PSI)** help determine appropriate management and site of care. Patients in **PSI Risk Class III** may be suitable for either outpatient treatment or a short inpatient stay depending on clinical judgment and comorbid conditions (Lim et al., 2009).

### 3.6 Treatment Considerations
Empirical antibiotic therapy targeting *Streptococcus pneumoniae* is recommended for CAP. **Beta-lactam antibiotics**, including amoxicillin-clavulanate and third-generation cephalosporins, remain central to empirical therapy and demonstrate high clinical success rates when initiated early (File and Marrie, 2010).

### 3.7 Supportive Care
Beyond antimicrobial therapy, supportive interventions may improve recovery. Early mobilization and physiotherapy in hospitalized CAP patients have been associated with shorter hospital stays and fewer respiratory complications without increased adverse events (Smith et al., 2018).

---

## 4. Discrepancies or Limitations
While the clinical presentation strongly supports pneumococcal CAP, several limitations remain:

- The diagnosis is based on clinical features and typical patterns rather than confirmed microbiological testing.
- Radiographic and laboratory findings support bacterial pneumonia but are not exclusive to *Streptococcus pneumoniae*.
- PSI Class III represents an intermediate risk category, meaning management decisions may vary.

These limitations highlight the importance of clinical monitoring and potential microbiological confirmation where appropriate.

---

## 5. Conclusion
The patient's symptoms, laboratory findings, and imaging results are highly consistent with **community-acquired pneumonia** caused by *Streptococcus pneumoniae*. Key diagnostic indicators include rust-colored sputum, lobar consolidation on chest imaging, and markedly elevated CRP levels. Severity assessment using the Pneumonia Severity Index places the patient in **Risk Class III**, suggesting moderate disease. Early administration of beta-lactam antibiotics and supportive care measures are recommended to optimize clinical outcomes.

---

## 6. References
Mandell et al., 2007

Lim et al., 2009

Torres et al., 2013

File and Marrie, 2010

Musher and Thorner, 2014

Wunderink and Waterer, 2014

Smith et al., 2018
"""

summary = ("The patient's symptoms and test results are consistent with community-acquired pneumonia "
           "caused by Streptococcus pneumoniae. Key supporting findings include rust-colored sputum, "
           "right lower lobe consolidation on chest X-ray, and a very high CRP level. The Pneumonia "
           "Severity Index places the patient in Risk Class III, indicating moderate severity.")


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
    doc = SimpleDocTemplate(
        output_path,  # δέχεται είτε path string είτε BytesIO object
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm
    )
    doc.build(markdown_to_flowables(md_text))

generate_pdf(report_markdown, "report.pdf")
print(f"Summary preview: {summary[:100]}...")