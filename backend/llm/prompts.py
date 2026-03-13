RESPONSE_COMPARISON_PROMPT = (
        "You will be given two medical diagnoses produced by AI chatbots. "
        "Your task is to analyze their consistency — that is, whether they convey "
        "roughly the same medical findings, conclusions, and recommendations.\n\n"
        "Diagnosis 1: {DIAGNOSIS_1}\n"
        "Diagnosis 2: {DIAGNOSIS_2}\n\n"
        "Compare the two diagnoses and respond only with a valid JSON object in the following format:\n\n"
        "{\n"
        '  "consistent": <true if the two diagnoses convey roughly the same findings and conclusions, false otherwise>,\n'
        '  "combined_diagnosis": "<a single, coherent combined diagnosis that merges the key points of both texts into one unified summary>",\n'
        '  "pubmed_keywords": ["<keyword1>", "<keyword2>", "<keyword3>", ...]\n'
        "}\n\n"
        "Rules:\n"
        "* Do not include any text outside the JSON object.\n"
        "* Do NOT wrap the response in markdown code blocks or backticks.\n"
        "* Set `consistent` to `true` only if the two diagnoses are in substantial agreement "
        "(same condition, similar severity, compatible recommendations).\n"
        "* The `combined_diagnosis` should be a clean, professional medical summary that integrates "
        "both texts without contradictions. If they are inconsistent, do not produce the combined text.\n"
        "* The `pubmed_keywords` field must contain 5 to 10 precise medical search terms in English (MeSH terms preferred) "
        "that, when searched on PubMed, would return peer-reviewed papers supporting or elaborating on the diagnosis. "
        "Include condition names, relevant pathogens, symptoms, and diagnostic methods where appropriate."
    )

FINALIZE_RESPONSE_PROMPT= """You will be given a medical diagnosis and a set of excerpts from scientific papers, each accompanied by its citation.

    Diagnosis:
    {DIAGNOSIS}

    Paper Excerpts:
    {PAPERS}
    (Each entry in PAPERS follows the format: [Citation] Excerpt text)

    Your task is to produce a JSON object with exactly two keys: "report" and "summary".

    ---

    "report" — A complete, well-structured medical report in Markdown format that:
    - Opens with a title (e.g., # Medical Report) and a table of contents
    - Is organized into clearly labeled sections with headings and subheadings, such as:
    ## 1. Overview
    ## 2. Clinical Findings
    ## 3. Supporting Evidence
    ### 3.1 ...
    ## 4. Discrepancies or Limitations (if any)
    ## 5. Conclusion
    - Presents the diagnosis as the central claim
    - Weaves in the provided paper excerpts to support, confirm, or elaborate on the diagnosis wherever relevant
    - Places the citation immediately after each use of a paper excerpt in inline format, e.g.: "...viral bronchitis is typically self-limiting (Smith et al., 2021)."
    - Only uses the provided excerpts — do not cite or invent any external sources
    - If a paper excerpt does not support the diagnosis, acknowledges the discrepancy briefly rather than forcing a false confirmation
    - Writes in a clear, clinical tone suitable for a formal medical report
    - Ends with a ## References section listing all cited sources

    "summary" — A concise 3–5 sentence plain-language summary of the report, suitable for display as a chatbot response to the patient or clinician. It should capture the key diagnosis, the main supporting evidence, and any notable caveats.

    ---

    Respond ONLY with a valid JSON object. Do not include any text, explanation, or markdown fences outside the JSON. The format must be exactly:
    {"report": "<full markdown report here>", "summary": "<short summary here>"}
    """

GENERATE_FINAL_REPORT_TEST1="""# Medical Report

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

GENERATE_FINAL_REPORT_TEST2=("The patient's symptoms and test results are consistent with community-acquired pneumonia "
           "caused by Streptococcus pneumoniae. Key supporting findings include rust-colored sputum, "
           "right lower lobe consolidation on chest X-ray, and a very high CRP level. The Pneumonia "
           "Severity Index places the patient in Risk Class III, indicating moderate severity.")
    
PUBMEDSHEARH_TEST= {
        "consistent": True,
        "combined_diagnosis": "The patient presents with headache, productive cough, and low-grade fever (approximately 37.1–37.9°C), a symptom cluster most consistent with an acute respiratory tract infection, most likely of viral etiology. The differential diagnosis includes acute viral bronchitis and viral upper respiratory infection (common cold) as the leading possibilities. Other potential causes include influenza, COVID-19 infection, early or mild community-acquired pneumonia if symptoms worsen or sputum becomes purulent, and acute sinusitis with post-nasal drip contributing to cough and headache. Recommended evaluation includes monitoring vital signs (temperature, respiratory rate, and oxygen saturation), performing lung auscultation, and assessing sputum characteristics. Diagnostic testing such as COVID-19 or influenza testing may be appropriate, with additional laboratory studies (e.g., CBC, CRP) and chest radiography considered if bacterial infection or pneumonia is suspected. Medical evaluation is recommended if symptoms persist for several days, worsen, or are accompanied by high fever, shortness of breath, chest pain, or significant fatigue.",
        "pubmed_keywords": [
            "Acute Bronchitis",
            "Upper Respiratory Tract Infections",
            "Influenza, Human",
            "COVID-19",
            "Community-Acquired Pneumonia",
            "Cough",
            "Fever",
            "Respiratory Tract Infections",
            "Sputum",
            "Chest Radiography"
        ]
    }