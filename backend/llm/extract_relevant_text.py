from sentence_transformers import SentenceTransformer, util
import numpy as np

THRESHOLD = 0.5
model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

def split_into_chunks(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def get_relevant_chunks(ai_diagnosis, papers_list):  # papers_list = list of dicts
    all_chunks = []
    paper_indices = []

    for paper_idx, paper in enumerate(papers_list):
        chunks = split_into_chunks(paper["text"])  # <-- paper["text"] αντί για papers_list["text"]
        all_chunks.extend(chunks)
        paper_indices.extend([paper_idx] * len(chunks))

    chunk_embeddings = model.encode(all_chunks, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
    diagnosis_embedding = model.encode(ai_diagnosis, convert_to_numpy=True)

    scores = util.cos_sim(diagnosis_embedding, chunk_embeddings)[0].numpy()

    chunk_map = {i: [] for i in range(len(papers_list))}
    for i, (chunk, score) in enumerate(zip(all_chunks, scores)):
        if score >= THRESHOLD:
            chunk_map[paper_indices[i]].append(chunk)

    # Επιστρέφει list of dicts, μόνο όσα έχουν chunks
    results = []
    for paper_idx, chunks in chunk_map.items():
        if not chunks:
            continue
        paper = papers_list[paper_idx]
        results.append({
            "url":      paper["url"],
            "title":    paper["title"],
            "citation": paper["citation"],
            "text":     chunks,  # list of strings
        })

    return results

# το results επιστρέφει:
#{
#    0: ["chunk κειμένου από paper 1", "άλλο chunk από paper 1"],  # paper 1
 #   1: [],                                                          # paper 2 (κανένα σχετικό chunk)
  #  2: ["chunk κειμένου από paper 3"]                              # paper 3
#}


if __name__ == "__main__":
    ai_diagnosis = """The patient presents with signs of chronic inflammation, including elevated CRP levels 
    and persistent fatigue. Laboratory results indicate increased ESR and white blood cell count. 
    The patient reports recurring joint pain, particularly in the knees and wrists, consistent with 
    inflammatory arthritis. Given the symptom duration of over 6 months and the pattern of affected joints, 
    rheumatoid arthritis is the primary suspected diagnosis. Secondary possibilities include systemic lupus 
    erythematosus (SLE) or psoriatic arthritis. Anti-CCP antibodies were found positive, which strongly 
    supports the rheumatoid arthritis diagnosis. Treatment recommendations include initiation of DMARDs, 
    specifically methotrexate, alongside NSAIDs for symptom relief. Referral to a rheumatologist is advised 
    for further evaluation and long-term management."""
    
    paper_context = [
    {
        "url": "https://pubmed.ncbi.nlm.nih.gov/1/",
        "title": "Rheumatoid Arthritis Paper",
        "citation": "Author, A. (2020). Title. Journal.",
        "text": """
        Rheumatoid arthritis (RA) is a chronic systemic inflammatory disorder that primarily affects the joints. 
        It is characterized by synovial inflammation, which leads to cartilage and bone destruction over time. 
        The exact etiology of RA remains unclear, but both genetic and environmental factors are believed to play 
        a significant role in its development.

        Epidemiological studies suggest that RA affects approximately 1% of the global population, with women 
        being two to three times more likely to develop the condition than men. The onset typically occurs between 
        the ages of 40 and 60, although RA can develop at any age.

        The pathophysiology of RA involves a complex interplay between the innate and adaptive immune systems. 
        Activated T cells, B cells, and macrophages infiltrate the synovial tissue, releasing pro-inflammatory 
        cytokines such as TNF-α, IL-1, and IL-6. These cytokines drive the inflammatory cascade, resulting in 
        synovial hyperplasia and pannus formation, which ultimately erodes joint cartilage and bone.

        Diagnosis of RA is based on clinical evaluation, laboratory findings, and imaging studies. The 2010 ACR/EULAR 
        classification criteria are widely used and include assessments of joint involvement, serology (RF and anti-CCP 
        antibodies), acute-phase reactants (CRP and ESR), and symptom duration. A score of 6 or more out of 10 
        is required for a definitive diagnosis of RA.

        Anti-cyclic citrullinated peptide (anti-CCP) antibodies are highly specific for RA, with a specificity 
        exceeding 95%. Their presence is associated with more aggressive disease and greater joint damage over time. 
        Rheumatoid factor (RF), although less specific, is also commonly used in the diagnostic workup.

        Treatment of RA aims to reduce inflammation, relieve symptoms, prevent joint damage, and improve quality of life. 
        Disease-modifying antirheumatic drugs (DMARDs) are the cornerstone of RA therapy. Methotrexate is the most 
        commonly prescribed DMARD and is often used as the first-line agent due to its efficacy and relatively 
        favorable safety profile.

        Biologic agents, including TNF inhibitors (etanercept, adalimumab, infliximab), IL-6 receptor antagonists 
        (tocilizumab), and B-cell depleting agents (rituximab), have revolutionized the management of RA in patients 
        who do not respond adequately to conventional DMARDs. Treat-to-target strategies, aiming for remission or 
        low disease activity, have significantly improved long-term outcomes.

        Nonsteroidal anti-inflammatory drugs (NSAIDs) and corticosteroids are used as adjunctive therapies to manage 
        pain and inflammation, particularly during disease flares. However, long-term use of corticosteroids is 
        associated with significant side effects and should be minimized.

        Systemic lupus erythematosus (SLE) is another chronic autoimmune disease that can mimic RA in its early stages. 
        SLE is characterized by the production of autoantibodies, particularly anti-dsDNA and anti-Smith antibodies, 
        and can affect multiple organ systems including the skin, kidneys, heart, and nervous system. Differentiating 
        SLE from RA is critical for appropriate management.

        Psoriatic arthritis (PsA) is an inflammatory arthritis associated with psoriasis. It can present with 
        peripheral joint involvement similar to RA, but typically also includes axial involvement, dactylitis, 
        and enthesitis. Unlike RA, PsA is usually seronegative for RF and anti-CCP antibodies.

        Early and accurate diagnosis of inflammatory arthritis is essential to prevent irreversible joint damage 
        and disability. Delays in diagnosis and treatment initiation are associated with worse structural and 
        functional outcomes. Rheumatologists play a central role in the evaluation and long-term management of 
        patients with RA and related conditions.
        """}, {
        "url": "https://pubmed.ncbi.nlm.nih.gov/2/",
        "title": "Rheumatoid Arthritis Paper",
        "citation": "Author, A. (2020). Title. Journal.",
        "text": """
        Ankylosing spondylitis (AS) is a chronic inflammatory arthritis that primarily affects the axial skeleton, 
        including the sacroiliac joints and spine. It belongs to the broader family of spondyloarthropathies (SpA) 
        and is characterized by progressive spinal fusion, resulting in reduced mobility and significant functional 
        impairment over time.

        Epidemiological data indicate that AS affects approximately 0.1–0.5% of the general population. Unlike 
        rheumatoid arthritis, AS shows a male predominance, with men being two to three times more commonly affected 
        than women. Onset typically occurs in late adolescence or early adulthood, usually before the age of 45, 
        making it one of the leading causes of inflammatory back pain in young individuals.

        The pathophysiology of AS involves dysregulation of both the innate and adaptive immune systems, with a 
        central role played by the IL-17/IL-23 axis and TNF-α signaling pathways. Inflammation begins at the 
        entheses — the sites where tendons and ligaments attach to bone — and progresses to involve the sacroiliac 
        joints and vertebral column. Chronic inflammation leads to new bone formation, syndesmophyte development, 
        and ultimately bamboo spine, the hallmark radiographic finding of advanced disease.

        A strong genetic association exists between AS and the HLA-B27 allele, which is present in approximately 
        90% of patients with AS in Western populations, compared with 6–9% in the general population. Despite this 
        strong association, HLA-B27 alone is not sufficient to cause disease, and its precise pathogenic role 
        remains under investigation. Other genetic loci, including ERAP1 and IL23R, have also been implicated.

        Diagnosis of AS is based on the modified New York criteria, which require radiographic evidence of 
        sacroiliitis combined with clinical features such as inflammatory back pain, limited lumbar spine motion, 
        or reduced chest expansion. The Assessment of SpondyloArthritis international Society (ASAS) criteria 
        additionally allow for a classification of non-radiographic axial SpA (nr-axSpA), recognizing early disease 
        stages where sacroiliitis may be detected only by MRI.

        Inflammatory back pain is the cardinal symptom of AS and is distinguished from mechanical back pain by 
        several features: insidious onset, duration of more than three months, improvement with exercise but not 
        with rest, nocturnal worsening, and morning stiffness lasting more than 30 minutes. Peripheral manifestations, 
        including asymmetric oligoarthritis, enthesitis, and dactylitis, occur in a subset of patients.

        Extra-articular manifestations are common in AS and significantly affect disease burden. Acute anterior 
        uveitis occurs in up to 40% of patients and may precede joint symptoms. Inflammatory bowel disease, 
        particularly Crohn's disease and ulcerative colitis, is observed in approximately 5–10% of cases. 
        Cardiac and pulmonary involvement, though less frequent, may occur in long-standing disease.

        Treatment of AS aims to reduce pain and stiffness, maintain spinal mobility, prevent structural damage, 
        and preserve quality of life. NSAIDs remain the first-line pharmacological therapy and, when taken 
        continuously, may also have a disease-modifying effect by retarding radiographic progression. Physical 
        therapy and regular exercise are integral components of management.

        Biologic agents have transformed the management of patients with active AS who fail NSAID therapy. 
        TNF inhibitors (etanercept, adalimumab, certolizumab pegol) and IL-17A inhibitors (secukinumab, 
        ixekizumab) have demonstrated significant efficacy in reducing inflammation, improving symptoms, and 
        retarding radiographic progression. Unlike in RA, conventional DMARDs such as methotrexate have limited 
        efficacy for axial disease in AS.

        Monitoring disease activity in AS relies on validated tools such as the Bath Ankylosing Spondylitis 
        Disease Activity Index (BASDAI) and the Ankylosing Spondylitis Disease Activity Score (ASDAS), which 
        incorporate patient-reported outcomes and acute-phase reactants. Imaging, including plain radiography 
        and MRI, is used to assess structural progression and detect active sacroiliac joint inflammation, 
        respectively. A treat-to-target approach targeting remission or low disease activity is increasingly 
        adopted in clinical practice.
        """}, {
        "url": "https://pubmed.ncbi.nlm.nih.gov/3/",
        "title": "Rheumatoid Arthritis Paper",
        "citation": "Author, A. (2020). Title. Journal.",
        "text": 
        """
        Gout is the most prevalent form of inflammatory arthritis, caused by the deposition of monosodium urate 
        (MSU) crystals in joints and soft tissues as a consequence of sustained hyperuricemia. Crystal arthropathies 
        also include calcium pyrophosphate deposition disease (CPPD) and basic calcium phosphate deposition, each 
        with distinct pathophysiological mechanisms and clinical presentations.

        Epidemiological studies indicate that gout affects approximately 1–4% of the general population in Western 
        countries, with prevalence rising steadily over recent decades. The condition predominantly affects men, 
        with a male-to-female ratio of approximately 4:1, though this disparity narrows significantly after menopause 
        due to the uricosuric effect of estrogen. Gout is rare before the age of 30 in men and before menopause in 
        women, with peak incidence occurring in the fifth and sixth decades of life.

        The pathophysiology of gout begins with hyperuricemia, defined as a serum uric acid level exceeding 
        6.8 mg/dL, the saturation threshold at which MSU crystals precipitate in biological fluids. Sustained 
        hyperuricemia leads to crystal deposition in synovial joints, periarticular tissues, and the renal 
        collecting system. Upon crystal phagocytosis by synovial macrophages and neutrophils, activation of the 
        NLRP3 inflammasome triggers IL-1β release, initiating the acute inflammatory cascade responsible for the 
        clinical manifestations of a gout flare.

        Risk factors for hyperuricemia and gout include dietary purine intake (red meat, organ meats, shellfish), 
        fructose-rich beverages, alcohol consumption (particularly beer), obesity, chronic kidney disease, 
        hypertension, and use of medications such as diuretics and low-dose aspirin. Genetic factors, including 
        variants in urate transporter genes (SLC2A9, ABCG2), also contribute substantially to uric acid levels 
        and gout susceptibility.

        Acute gout classically presents as sudden-onset, severe monoarticular arthritis, most commonly affecting 
        the first metatarsophalangeal joint (podagra). The affected joint becomes intensely erythematous, swollen, 
        warm, and exquisitely tender, often reaching maximal severity within 12–24 hours. Attacks are self-limiting, 
        typically resolving within 7–14 days without treatment. Fever and elevated inflammatory markers are 
        frequently observed during acute flares.

        Diagnosis of gout is definitively established by identification of negatively birefringent, needle-shaped 
        MSU crystals on polarized light microscopy of synovial fluid or tophus aspirate. In the absence of 
        arthrocentesis, the 2015 ACR/EULAR classification criteria incorporate clinical, laboratory, and imaging 
        findings to classify gout with high sensitivity and specificity. Dual-energy CT (DECT) and musculoskeletal 
        ultrasound have emerged as valuable imaging modalities for crystal detection and disease burden assessment.

        Chronic tophaceous gout develops in patients with longstanding untreated hyperuricemia and is characterized 
        by the formation of tophi — aggregates of MSU crystals surrounded by a granulomatous inflammatory reaction. 
        Tophi commonly deposit in the helix of the ear, olecranon bursa, Achilles tendon, and periarticular tissues, 
        and may cause joint destruction, functional impairment, and carpal tunnel syndrome. Uric acid nephrolithiasis 
        and gouty nephropathy represent important renal complications of chronic hyperuricemia.

        Management of acute gout flares relies on prompt anti-inflammatory therapy with colchicine, NSAIDs, or 
        corticosteroids. Colchicine, when administered within the first 12–24 hours of flare onset, is highly 
        effective and is preferred in patients without renal impairment. IL-1 inhibitors (anakinra, canakinumab) 
        represent an emerging option for refractory or contraindicated cases.

        Urate-lowering therapy (ULT) is the cornerstone of long-term gout management and is indicated in patients 
        with recurrent flares, tophi, uric acid nephrolithiasis, or chronic gouty arthropathy. Allopurinol, 
        a xanthine oxidase inhibitor, is the most widely used first-line ULT agent, with febuxostat as an 
        alternative. The target serum uric acid level is below 6 mg/dL, or below 5 mg/dL in patients with tophi. 
        ULT initiation should be accompanied by flare prophylaxis with low-dose colchicine or NSAIDs for at least 
        3–6 months to prevent mobilization flares.

        Calcium pyrophosphate deposition disease (CPPD) represents a distinct crystal arthropathy caused by 
        deposition of calcium pyrophosphate dihydrate crystals, predominantly in fibrocartilage and hyaline 
        cartilage. It may present as acute CPP crystal arthritis (pseudogout), chronic CPP inflammatory arthritis, 
        or be an incidental radiographic finding (chondrocalcinosis). CPPD is strongly associated with aging, 
        osteoarthritis, and metabolic disorders including hyperparathyroidism, hemochromatosis, and hypomagnesemia. 
        Unlike gout, no established crystal-depleting therapy currently exists for CPPD, and management remains 
        largely symptomatic.
        """}
    ]
   
    relevant_chunks = get_relevant_chunks(ai_diagnosis, paper_context)

    for paper in relevant_chunks:
        print(f"\n=== {paper['title']}: {len(paper['text'])} σχετικά αποσπάσματα ===\n")
        for chunk in paper["text"]:
            print(chunk)
            print("---")