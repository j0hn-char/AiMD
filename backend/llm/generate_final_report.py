import json
import re
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
 
# from .prompts import GENERATE_FINAL_REPORT_TEST1, GENERATE_FINAL_REPORT_TEST2
 
def register_fonts():
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/",
        "C:/Windows/Fonts/",
        "/Library/Fonts/",
        os.path.join(os.path.dirname(__file__), "fonts/"),
    ]
    for path in font_paths:
        regular    = os.path.join(path, "DejaVuSans.ttf")
        bold       = os.path.join(path, "DejaVuSans-Bold.ttf")
        italic     = os.path.join(path, "DejaVuSans-Oblique.ttf")
        bolditalic = os.path.join(path, "DejaVuSans-BoldOblique.ttf")
        if os.path.exists(regular):
            pdfmetrics.registerFont(TTFont("DejaVu",            regular))
            pdfmetrics.registerFont(TTFont("DejaVu-Bold",       bold))
            pdfmetrics.registerFont(TTFont("DejaVu-Italic",     italic))
            pdfmetrics.registerFont(TTFont("DejaVu-BoldItalic", bolditalic))
            from reportlab.pdfbase.pdfmetrics import registerFontFamily
            registerFontFamily("DejaVu",
                               normal="DejaVu",
                               bold="DejaVu-Bold",
                               italic="DejaVu-Italic",
                               boldItalic="DejaVu-BoldItalic")
            return "DejaVu"
    return "Helvetica"
 
FONT = register_fonts()
 
# --- FIX 1: Χαρακτήρες που δεν υποστηρίζονται → αντικατάσταση με ASCII/ασφαλή εκδοχή ---
# Αυτά εμφανίζονται ως τετράγωνα όταν η γραμματοσειρά δεν έχει το glyph.
UNICODE_REPLACEMENTS = {
    '\u2019': "'",   # right single quotation mark → απόστροφος
    '\u2018': "'",   # left single quotation mark
    '\u201c': '"',   # left double quotation mark
    '\u201d': '"',   # right double quotation mark
    '\u2013': '-',   # en dash
    '\u2014': '--',  # em dash
    '\u2026': '...', # ellipsis
    '\u00b7': '\u2022',  # middle dot → bullet (υποστηρίζεται από DejaVu)
    '\u25cf': '\u2022',  # black circle → bullet
    '\u2192': '->',  # rightwards arrow
    '\u2190': '<-',  # leftwards arrow
    '\u00a0': ' ',   # non-breaking space → κανονικό κενό
    '\u00ae': '(R)', # registered sign (αν λείπει από font)
    '\u00a9': '(c)', # copyright sign (αν λείπει από font)
}
 
_font_face = None

def _get_font_face():
    global _font_face
    if _font_face is None:
        try:
            _font_face = pdfmetrics.getFont("DejaVu").face
        except:
            _font_face = None
    return _font_face

def get_safe_replacement(char):
    cp = ord(char)
    if cp in (0x2010, 0x2011, 0x2012, 0x2013): return '-'   # hyphens/en-dash
    if cp == 0x2014: return '--'                              # em dash
    if cp in (0x2018, 0x2019, 0x02BC): return "'"
    if cp in (0x201C, 0x201D, 0x201E): return '"'
    if cp in (0x00A0, 0x202F, 0x2009, 0x2008, 0x2007,
              0x2006, 0x2005, 0x2004, 0x2003, 0x2002): return ' '
    if cp in (0x200B, 0x200C, 0x200D, 0xFEFF,
              0x200E, 0x200F): return ''   # zero-width → αφαίρεση
    if cp == 0x2026: return '...'
    if cp in (0x25CF, 0x25AA, 0x25A0): return '\u2022'
    if cp == 0x2192: return '->'
    if cp == 0x00AE: return '(R)'
    if cp == 0x00A9: return '(c)'
    if cp == 0x2122: return '(TM)'
    return None

def sanitize_text(text: str) -> str:
    face = _get_font_face()
    result = []
    for char in text:
        cp = ord(char)
        if cp < 128:
            result.append(char)
            continue
        # Αν το glyph υπάρχει στη DejaVu → κρατάμε τον χαρακτήρα
        if face and face.charToGlyph.get(cp, 0):
            result.append(char)
            continue
        # Δεν υπάρχει → ασφαλής αντικατάσταση
        replacement = get_safe_replacement(char)
        if replacement is not None:
            result.append(replacement)
        else:
            result.append(char.encode('ascii', 'replace').decode('ascii'))
    return ''.join(result)
 
 
def convert_inline(text: str) -> str:
    """
    FIX 2: Σωστή σειρά επεξεργασίας.
 
    ΠΡΟΒΛΗΜΑ (παλιός κώδικας):
      1. text.replace('&', '&amp;')   ← αντικαθιστά ΟΛΑ τα & αμέσως
      2. Αργότερα προστίθεται '&#8226;' ← αλλά εδώ δεν υπάρχει πρόβλημα
         γιατί το &#8226; προστίθεται ΜΕΤΑ το convert_inline στα bullets.
         Ωστόσο αν το md_text περιέχει ήδη HTML entities, χαλάει.
 
    FIX: Κάνουμε escape μόνο τα & που δεν ανήκουν ήδη σε HTML entity,
    και χρησιμοποιούμε απευθείας τον Unicode χαρακτήρα • αντί για entity.
    """
    # Πρώτα sanitize για μη-υποστηριζόμενους χαρακτήρες
    text = sanitize_text(text)
 
    # Escape μόνο & που ΔΕΝ είναι ήδη μέρος entity (π.χ. &amp; &lt; &#8226;)
    text = re.sub(r'&(?!(?:#\d+|#x[\da-fA-F]+|[a-zA-Z]+);)', '&amp;', text)
 
    # Escape < και > που δεν είναι ReportLab tags
    # (προσοχή: αφήνουμε <b>, <i> κ.λπ. που θα προστεθούν παρακάτω)
    text = text.replace('<', '&lt;').replace('>', '&gt;')
 
    # Markdown links [text](#anchor) → κράτα μόνο το text
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
 
    # Bold+italic, bold, italic — τα ξαναβάζουμε ως ReportLab XML
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'\*\*(.*?)\*\*',     r'<b>\1</b>',         text)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
 
    return text
 
 
def markdown_to_flowables(md_text):
    # FIX 3: Sanitize ολόκληρο το κείμενο πριν την επεξεργασία
    md_text = sanitize_text(md_text)
 
    styles = getSampleStyleSheet()
 
    title_style = ParagraphStyle('MyTitle', parent=styles['Title'],
                                 fontName=f"{FONT}-Bold",
                                 fontSize=22, spaceAfter=18,
                                 textColor=colors.HexColor('#1a3a5c'))
    h2_style = ParagraphStyle('MyH2', parent=styles['Heading2'],
                               fontName=f"{FONT}-Bold",
                               fontSize=14, spaceBefore=14, spaceAfter=6,
                               textColor=colors.HexColor('#1a3a5c'))
    h3_style = ParagraphStyle('MyH3', parent=styles['Heading3'],
                               fontName=f"{FONT}-Bold",
                               fontSize=11, spaceBefore=10, spaceAfter=4,
                               textColor=colors.HexColor('#2e6da4'))
    body_style = ParagraphStyle('MyBody', parent=styles['Normal'],
                                fontName=FONT,
                                fontSize=10, leading=15, spaceAfter=6)
    bullet_style = ParagraphStyle('MyBullet', parent=styles['Normal'],
                                   fontName=FONT,
                                   fontSize=10, leading=14, spaceAfter=3,
                                   leftIndent=18)
    toc_bullet_style = ParagraphStyle('TocBullet', parent=styles['Normal'],
                                       fontName=FONT,
                                       fontSize=10, leading=14, spaceAfter=3,
                                       leftIndent=36)
 
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
        if stripped.startswith('####'):
            flowables.append(Paragraph(convert_inline(stripped[5:]), h3_style))
            continue
        if stripped.startswith('###'):
            flowables.append(Paragraph(convert_inline(stripped[4:]), h3_style))
            continue
        if stripped.startswith('##'):
            flowables.append(Paragraph(convert_inline(stripped[3:]), h2_style))
            continue
        if stripped.startswith('#'):
            flowables.append(Paragraph(convert_inline(stripped[2:]), title_style))
            continue
        
        
 
        # FIX 4: Χρησιμοποιούμε τον Unicode χαρακτήρα • απευθείας
        # αντί για HTML entity &#8226; που μπορεί να σπάσει από το &amp; escape.
        m = re.match(r'^[-*]\s+(.*)', stripped)
        if m:
            indent = len(line) - len(line.lstrip())
            if indent >= 2:
                bs = ParagraphStyle('SubBul', parent=toc_bullet_style,
                                    fontName=FONT, leftIndent=36 + indent)
            else:
                bs = ParagraphStyle('Bul', parent=bullet_style,
                                    fontName=FONT, leftIndent=18 + indent)
            # • είναι U+2022, υποστηρίζεται πλήρως από DejaVu
            flowables.append(Paragraph('\u2022 ' + convert_inline(m.group(1)), bs))
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
        output_path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm
    )
    doc.build(markdown_to_flowables(md_text))
 
 
if __name__ == "__main__":
    # report_markdown = GENERATE_FINAL_REPORT_TEST1
    # summary = GENERATE_FINAL_REPORT_TEST2
    # generate_pdf(report_markdown, "report.pdf")
 
    # Δοκιμή με χαρακτήρες που προκαλούσαν τετράγωνα
    test_md = """# Τίτλος Αναφοράς
 
## Ενότητα 1
 
Αυτό είναι **έντονο** και αυτό *πλάγιο* κείμενο.
 
Κείμενο με ειδικούς χαρακτήρες: "εισαγωγικά" – παύλα — μεγάλη παύλα...
 
- Πρώτο bullet
- Δεύτερο bullet με **bold**
  - Εσοχή bullet
- Τρίτο bullet
 
### Υπο-ενότητα
 
1. Πρώτο
2. Δεύτερο
 
---
 
Τέλος κειμένου.
"""
    generate_pdf(test_md, "test_output.pdf")
    print("PDF δημιουργήθηκε επιτυχώς: test_output.pdf")