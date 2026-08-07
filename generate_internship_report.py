"""
RiskSense AI — Internship Evaluation Report Generator
Generates a comprehensive MS Word (.docx) report covering the original
platform plus this session's work: security hardening, testing/CI, the
PyTorch autoencoder anomaly detector, and the honest model evaluation.
Run: python generate_internship_report.py
"""

import os
import datetime

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# ─── Page Margins ───────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.5)


# ─── Style Helpers ──────────────────────────────────────────────────────────
def set_font(run, name="Calibri", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)


def heading1(text):
    p = doc.add_heading(text, level=1)
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    run = p.runs[0]
    run.font.name = "Calibri"
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1A, 0x37, 0x6C)
    return p


def heading2(text):
    p = doc.add_heading(text, level=2)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.runs[0]
    run.font.name = "Calibri"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1F, 0x56, 0x9A)
    return p


def heading3(text):
    p = doc.add_heading(text, level=3)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    run = p.runs[0]
    run.font.name = "Calibri"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
    return p


def body(text, bold=False, italic=False, indent=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    if indent:
        p.paragraph_format.left_indent = Cm(0.8)
    run = p.add_run(text)
    set_font(run, bold=bold, italic=italic)
    return p


def callout(text, color=(0xB8, 0x3B, 0x1C)):
    """Highlighted paragraph for important findings/warnings."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.left_indent = Cm(0.5)
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), "FDECEA")
    p._p.get_or_add_pPr().append(shading)
    run = p.add_run(text)
    set_font(run, bold=True, color=color)
    return p


def bullet(text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    if level:
        p.paragraph_format.left_indent = Cm(1.2 * (level + 1))
    run = p.add_run(text)
    set_font(run)
    return p


def code_block(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.space_after = Pt(6)
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), "F2F2F2")
    p._p.get_or_add_pPr().append(shading)
    run = p.add_run(text)
    run.font.name = "Courier New"
    run.font.size = Pt(9)
    return p


def add_table(headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = hdr_cells[i].paragraphs[0].runs[0]
        run.font.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shading = OxmlElement("w:shd")
        shading.set(qn("w:val"), "clear")
        shading.set(qn("w:color"), "auto")
        shading.set(qn("w:fill"), "1A376C")
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading)
    for r_idx, row in enumerate(rows):
        cells = table.rows[r_idx + 1].cells
        fill = "EBF3FB" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(row):
            cells[c_idx].text = str(val)
            cells[c_idx].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = cells[c_idx].paragraphs[0].runs[0]
            run.font.size = Pt(9.5)
            shading = OxmlElement("w:shd")
            shading.set(qn("w:val"), "clear")
            shading.set(qn("w:color"), "auto")
            shading.set(qn("w:fill"), fill)
            cells[c_idx]._tc.get_or_add_tcPr().append(shading)
    if col_widths:
        for i, width in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(width)
    doc.add_paragraph()
    return table


def page_break():
    doc.add_page_break()


def add_footer():
    for section in doc.sections:
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = fp.add_run("RiskSense AI — Internship Evaluation Report  |  Confidential")
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
        fp.add_run("  |  Page ")
        fld1 = OxmlElement("w:fldChar")
        fld1.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.text = "PAGE"
        fld2 = OxmlElement("w:fldChar")
        fld2.set(qn("w:fldCharType"), "end")
        r = OxmlElement("w:r")
        r.append(fld1)
        r.append(instr)
        r.append(fld2)
        fp._p.append(r)


SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")


def add_screenshot(filename, caption):
    path = os.path.join(SCREENSHOTS_DIR, filename)
    if os.path.exists(path):
        try:
            doc.add_picture(path, width=Inches(6.0))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception as e:
            body(f"[Screenshot: {caption} — could not embed: {e}]", italic=True)
    else:
        body(f"[Screenshot not found: {filename}]", italic=True)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(14)
    r = cap.add_run(f"Figure: {caption}")
    r.font.italic = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0x60, 0x60, 0x60)


# ══════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ══════════════════════════════════════════════════════════════════════════
doc.add_paragraph("\n\n\n")
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title_p.add_run("RiskSense AI")
tr.font.name, tr.font.size, tr.font.bold = "Calibri", Pt(32), True
tr.font.color.rgb = RGBColor(0x1A, 0x37, 0x6C)

subtitle_p = doc.add_paragraph()
subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = subtitle_p.add_run("Agentic Banking Fraud Analytics and Advisory Platform")
sr.font.name, sr.font.size = "Calibri", Pt(16)
sr.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

sub2_p = doc.add_paragraph()
sub2_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr2 = sub2_p.add_run("Summer Internship Evaluation Report")
sr2.font.name, sr2.font.size, sr2.font.italic = "Calibri", Pt(13), True
sr2.font.color.rgb = RGBColor(0x50, 0x50, 0x50)

doc.add_paragraph("\n")
line_p = doc.add_paragraph()
line_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
lr = line_p.add_run("─" * 55)
lr.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
doc.add_paragraph("\n")

for label, val in [
    ("Project Type", "Multi-Agent ML/DL Web Application"),
    ("Domain", "FinTech / Banking Fraud Detection"),
    ("Technology", "Python, Flask, scikit-learn, PyTorch, SMOTE"),
    ("Date", datetime.date.today().strftime("%B %d, %Y")),
]:
    lp = doc.add_paragraph()
    lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    b = lp.add_run(f"{label}: ")
    b.font.bold = True
    b.font.size = Pt(12)
    v = lp.add_run(val)
    v.font.size = Pt(12)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# ABSTRACT
# ══════════════════════════════════════════════════════════════════════════
heading1("Abstract")
body(
    "RiskSense AI is an agentic banking fraud analytics and advisory platform developed to "
    "support loan-underwriting teams in identifying and responding to fraudulent loan "
    "applications. The system combines a supervised ensemble classifier with an unsupervised "
    "deep learning anomaly detector within a coordinated multi-agent architecture, moving "
    "beyond a single fraud-probability score toward an explainable, action-oriented "
    "decision-support pipeline."
)
body(
    "At its core, a Random Forest ensemble — trained on a SMOTE-balanced dataset of 50,000 "
    "historical loan applications — estimates fraud probability against a dynamically adjusted "
    "threshold that tightens or relaxes based on applicant-specific risk factors such as credit "
    "score, debt-to-income ratio, and EMI burden. Complementing this supervised model, a "
    "PyTorch-based tabular autoencoder is trained exclusively on genuine applications to learn "
    "the manifold of normal applicant behaviour; applications that reconstruct poorly against "
    "this learned profile are flagged as anomalous, targeting fraud patterns a purely supervised "
    "model structurally cannot learn from labelled examples alone."
)
body(
    "These signals feed a three-agent pipeline — Detection, Analytics, and Advisory — "
    "orchestrated to transform a raw model score into a structured risk narrative and a "
    "concrete banking recommendation (standard approval, manual review, or block-and-escalate "
    "with compliance guidance). The platform is exposed through a Flask web application "
    "supporting individual and batch application screening, portfolio-level risk dashboards, "
    "and a conversational advisor, alongside a documented REST API."
)
body(
    "Beyond feature delivery, this phase of the internship focused on production-readiness and "
    "methodological rigor: automated testing, continuous integration, containerized deployment, "
    "secure secrets management, and — most significantly — a critical evaluation exercise that "
    "uncovered a pre-existing methodology flaw (the production model was never evaluated on "
    "held-out data) and a live feature-scale bug (a mismatch between the training data's "
    "debt-to-income scale and the scale the application actually collects from users). These "
    "findings, and the evaluation discipline used to surface them, are documented in full in "
    "Chapter 8."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════════
heading1("Table of Contents")
toc_items = [
    ("Chapter 1", "Introduction", "4"),
    ("Chapter 2", "System Architecture & Design", "5"),
    ("Chapter 3", "Machine Learning: Supervised Fraud Model", "6"),
    ("Chapter 4", "Deep Learning: Autoencoder Anomaly Detector", "7"),
    ("Chapter 5", "Agent Implementation", "8"),
    ("Chapter 6", "Web Application & REST API", "9"),
    ("Chapter 7", "Software Engineering Practices", "10"),
    ("Chapter 8", "Model Evaluation & Critical Findings", "11"),
    ("Chapter 9", "Application Screenshots", "13"),
    ("Chapter 10", "Results & Discussion", "14"),
    ("Chapter 11", "Limitations & Future Work", "15"),
    ("Chapter 12", "Conclusion", "16"),
    ("References", "", "17"),
    ("Appendix", "Key Code Snippets", "18"),
]
for num, title, pg in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{num}  {title}")
    run.font.size = Pt(11)
    run.font.bold = True
    tab = p.add_run(f"\t{pg}")
    tab.font.size = Pt(11)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(15), WD_ALIGN_PARAGRAPH.RIGHT)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 1 — INTRODUCTION
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 1: Introduction")

heading2("1.1 Background & Problem Statement")
body(
    "Lending institutions disburse loans across multiple product lines — home, personal, "
    "vehicle, education, and business loans — and fraudulent applications represent a "
    "persistent and costly risk. Traditional fraud review relies on manual analyst judgement "
    "and static rule engines, both of which are slow to apply consistently at scale and brittle "
    "against fraud patterns that mimic legitimate applicant profiles."
)
body(
    "Machine learning models can detect fraud patterns at scale, but production deployments "
    "commonly present a single probability score with no interpretable reasoning and no "
    "actionable next step for the reviewing officer. RiskSense AI addresses this gap with a "
    "multi-agent pipeline that produces a probability, a human-readable risk narrative, and a "
    "concrete banking recommendation for every application."
)

heading2("1.2 Project Objectives")
for obj in [
    "Design and implement a multi-agent AI system for bank loan fraud detection that operates fully offline.",
    "Train a supervised ensemble ML model on a SMOTE-balanced dataset to produce fraud probability estimates.",
    "Implement a dynamic fraud classification threshold that adapts to individual applicant risk profiles.",
    "Add a genuine deep learning component (unsupervised anomaly detection) to complement the supervised model, targeting fraud patterns unseen in labelled training data.",
    "Build a full-stack web application supporting manual entry, synthetic data, and real dataset-based predictions, plus batch screening.",
    "Harden the platform for production use: remove insecure defaults, add automated tests and CI, containerize deployment.",
    "Critically evaluate both models against held-out ground truth, rather than accepting reported training-set performance at face value.",
]:
    bullet(obj)

heading2("1.3 Scope")
body(
    "RiskSense AI is a decision-support platform, not an autonomous approval engine — final "
    "credit decisions remain with authorized banking officers. In scope: fraud detection across "
    "five loan types; a three-agent analysis pipeline; manual, synthetic, and dataset-sampled "
    "prediction modes; batch screening; a conversational advisor; a REST API; and, from this "
    "phase of work, an unsupervised deep learning anomaly detector plus a rigorous evaluation "
    "of both models against held-out data. Out of scope: real-time database integration, "
    "customer-facing portals, and automated regulatory filing."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 2 — SYSTEM ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 2: System Architecture & Design")

heading2("2.1 High-Level Architecture")
body(
    "The platform is layered into a Presentation Layer (Flask templates + REST API), an "
    "Orchestration Layer (RiskSenseOrchestrator), an Agent Layer (three specialized agents), "
    "and an ML Inference Layer (FraudPredictor, AnomalyDetector, and their model artifacts)."
)
code_block(
    "User Input (Web Form / API JSON)\n"
    "        |\n"
    "Flask Route (/prediction, /api/analyze, /api/batch)\n"
    "        |\n"
    "RiskSenseOrchestrator.run_pipeline(form_data)\n"
    "        |\n"
    "+-----------------------------------------------------+\n"
    "|  1. DetectionAgent.score_application()               |\n"
    "|     -> FraudPredictor: RandomForest probability       |\n"
    "|     -> AnomalyDetector: autoencoder reconstruction    |\n"
    "|        error vs. learned genuine-profile threshold   |\n"
    "|     -> Dynamic threshold calculation                  |\n"
    "|  2. AnalyticsAgent.analyze()                          |\n"
    "|     -> Rule-based risk signal extraction               |\n"
    "|     -> Deep Anomaly Signal (if flagged)                |\n"
    "|     -> Composite risk score computation                |\n"
    "|  3. AdvisoryAgent.advise()                             |\n"
    "|     -> Decision: BLOCK / REVIEW / APPROVE               |\n"
    "|     -> Prioritized action items                         |\n"
    "+-----------------------------------------------------+\n"
    "        |\n"
    "AgenticReport -> rendered to HTML or JSON"
)

heading2("2.2 Dynamic Threshold Mechanism")
add_table(
    ["Condition", "Threshold Adjustment", "Rationale"],
    [
        ["Base threshold", "40.0%", "Conservative default below the standard 50% cutoff"],
        ["CIBIL < 500", "-10% (stricter)", "Very poor credit indicates higher fraud/default risk"],
        ["CIBIL > 750", "+10% (lenient)", "Excellent credit warrants a relaxed threshold"],
        ["DTI > 0.60", "-5% (stricter)", "High debt burden correlates with distressed applications"],
        ["EMI burden > 50% of income", "-5% (stricter)", "Severe income commitment signals distress"],
        ["Final clamp", "min 20%, max 60%", "Prevents extreme threshold values"],
    ],
    col_widths=[4.5, 3.5, 8.0],
)

heading2("2.3 Technology Stack")
add_table(
    ["Component", "Technology", "Purpose"],
    [
        ["Web Framework", "Flask 3.0", "Application server, HTML rendering, REST API"],
        ["Production Server", "Gunicorn", "Multi-worker WSGI server for containerized deployment"],
        ["Supervised ML", "scikit-learn (RandomForest)", "Fraud probability classification"],
        ["Deep Learning", "PyTorch", "Unsupervised autoencoder for anomaly detection"],
        ["Class Balancing", "imbalanced-learn (SMOTE)", "Synthetic minority oversampling for training"],
        ["Data Processing", "pandas / numpy", "Tabular data manipulation"],
        ["Testing", "pytest", "Unit and integration tests"],
        ["CI/CD", "GitHub Actions", "Automated test execution on push/PR"],
        ["Containerization", "Docker", "Reproducible, isolated deployment"],
    ],
    col_widths=[3.5, 5.5, 7.0],
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 3 — SUPERVISED MODEL
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 3: Machine Learning — Supervised Fraud Model")

heading2("3.1 Dataset")
body(
    "The primary dataset, loan_applications.csv, contains 50,000 historical loan application "
    "records with a binary target fraud_flag (1 = Fraud, 0 = Genuine): 48,974 genuine records "
    "and 1,026 fraud records (~2.1% fraud rate), spanning five loan product categories and "
    "fourteen applicant attributes across financial, employment, and demographic dimensions."
)

heading2("3.2 Preprocessing & Class Balancing")
body(
    "Numeric features are standardized (StandardScaler) and categorical features one-hot "
    "encoded (OneHotEncoder) via a fitted ColumnTransformer (preprocessor.pkl), applied "
    "identically at training and inference time. Because fraud is a small minority of "
    "applications, SMOTE (Synthetic Minority Over-sampling Technique) generates synthetic "
    "minority-class samples via interpolation, preventing the model from trivially predicting "
    "\"genuine\" for every application."
)

heading2("3.3 Model Training")
body(
    "A RandomForestClassifier (100 estimators) is trained in train.py on the SMOTE-balanced "
    "feature set and serialized as loan_fraud_ensemble_model.pkl. At inference, "
    "model.predict_proba(X)[0][1] yields the continuous fraud probability, compared against "
    "the dynamic threshold (Section 2.2) to produce the binary FRAUD/GENUINE label."
)
callout(
    "Important: train.py trains on 100% of the dataset with no held-out test split. The model's "
    "true generalization performance was not measured until the evaluation exercise in Chapter "
    "8 — see that chapter before treating any accuracy figure from this model as validated."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 4 — DEEP LEARNING COMPONENT
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 4: Deep Learning — Autoencoder Anomaly Detector")

heading2("4.1 Motivation")
body(
    "The RandomForest is a supervised classifier: it can only recognize fraud patterns that "
    "resemble the 1,026 labelled fraud examples it was trained on. Any fraud typology that "
    "doesn't statistically resemble those examples can pass through with a low probability "
    "score, regardless of how unusual the application actually is. To address this structural "
    "limitation, a PyTorch tabular autoencoder was added as a second, independent detection "
    "signal, trained without any fraud labels at all."
)

heading2("4.2 Architecture")
body(
    "TabularAutoencoder (ml/autoencoder_model.py) is a fully connected encoder-decoder network "
    "operating on the same 28-dimensional feature representation produced by the fitted "
    "preprocessor:"
)
add_table(
    ["Layer", "Shape", "Activation"],
    [
        ["Encoder Linear 1", "28 -> 16", "ReLU"],
        ["Encoder Linear 2 (bottleneck)", "16 -> 8", "ReLU"],
        ["Decoder Linear 1", "8 -> 16", "ReLU"],
        ["Decoder Linear 2 (output)", "16 -> 28", "Linear (reconstruction)"],
    ],
    col_widths=[6.0, 5.0, 4.5],
)

heading2("4.3 Training Methodology")
body(
    "train_autoencoder.py trains exclusively on the 48,974 genuine applications — fraud rows "
    "are entirely excluded from this model's training. A 90/10 train/validation split (seeded, "
    "reproducible) is applied to the genuine records. The network is trained for 30 epochs "
    "(Adam optimizer, learning rate 1e-3, batch size 256, MSE reconstruction loss). The anomaly "
    "threshold is set at the 97.5th percentile of reconstruction error on the held-out "
    "validation split of genuine records — i.e., the threshold is calibrated to flag the most "
    "unusual 2.5% of genuine profiles as a false-positive ceiling, and anything beyond that "
    "range as anomalous."
)

heading2("4.4 Inference & Pipeline Integration")
body(
    "AnomalyDetector (ml/anomaly_detector.py) loads the trained weights and reuses the "
    "supervised model's fitted preprocessor for consistent feature encoding. It exposes "
    "score(form_data) for live form submissions and score_row(row) for dataset-sampled "
    "records. The DetectionAgent attaches the resulting AnomalyResult to its report; the "
    "AnalyticsAgent adds a \"Deep Anomaly Signal\" (contributing +15 to the composite risk "
    "score) whenever reconstruction error exceeds the trained threshold. If the trained "
    "artifacts are absent, the detector loads as None and the rest of the pipeline runs "
    "unaffected — the deep learning layer is additive, not a hard dependency."
)

heading2("4.5 Deployment Consideration")
body(
    "torch is pinned to the CPU-only wheel index in requirements.txt "
    "(--index-url https://download.pytorch.org/whl/cpu) so that CI runs and container builds do "
    "not pull multi-gigabyte CUDA packages unnecessarily, since this model is small enough to "
    "train and run on CPU in seconds."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 5 — AGENT IMPLEMENTATION
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 5: Agent Implementation")

heading2("5.1 Detection Agent")
body(
    "agents/detection_agent.py wraps both FraudPredictor (RandomForest) and the optional "
    "AnomalyDetector (autoencoder), producing a DetectionReport with the model's probability, "
    "a confidence band, and — when available — the anomaly result."
)
add_table(
    ["Confidence Band", "Condition", "Status"],
    [
        ["High Risk", "is_fraud = True (probability >= dynamic threshold)", "alert"],
        ["Elevated Risk", "probability >= 30% but below threshold", "warning"],
        ["Low Risk", "probability < 30%", "success"],
    ],
    col_widths=[4.0, 8.0, 4.0],
)

heading2("5.2 Analytics Agent")
body(
    "agents/analytics_agent.py interprets application features via domain-expert rules "
    "(CIBIL, DTI, loan-to-income, EMI burden, employment, age) to produce a composite 0-100 "
    "risk score and a list of named RiskSignals, now including the Deep Anomaly Signal "
    "contributed by the autoencoder when triggered."
)

heading2("5.3 Advisory Agent")
body(
    "agents/advisory_agent.py translates detection and analytics outputs into one of three "
    "structured banking decisions — BLOCK & ESCALATE, MANUAL REVIEW, or STANDARD APPROVAL PATH "
    "— each with prioritized action items and a mandatory compliance note clarifying that this "
    "is decision support, not autonomous approval."
)

heading2("5.4 Orchestrator")
body(
    "agents/orchestrator.py constructs the AnomalyDetector once at startup (loading trained "
    "weights if present) and wires it into the DetectionAgent, then coordinates the sequential "
    "Detection -> Analytics -> Advisory pipeline via run_pipeline() and run_dataset_sample(), "
    "compiling the final AgenticReport."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 6 — WEB APPLICATION
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 6: Web Application & REST API")

heading2("6.1 Pages")
add_table(
    ["Route", "Page"],
    [
        ["/", "Home"],
        ["/prediction", "Fraud analysis (manual, random-fill, or dataset-sampled)"],
        ["/batch", "Batch screening (up to 500 applications per request)"],
        ["/cases", "Case management (localStorage-backed)"],
        ["/dashboard", "Analytics dashboard"],
        ["/agents", "Agent architecture visualization"],
        ["/advisor", "Conversational advisor"],
        ["/compare", "Side-by-side scenario comparison"],
        ["/about", "Platform overview"],
    ],
    col_widths=[4.0, 12.0],
)

heading2("6.2 REST API")
add_table(
    ["Endpoint", "Purpose"],
    [
        ["POST /api/analyze", "Full agentic pipeline result for a single application, including anomaly detail"],
        ["POST /api/batch", "Batch-screens an array of applications, returns per-row anomaly flag and aggregate exposure"],
        ["POST /api/chat", "Advisor chat endpoint"],
        ["GET /api/dataset/random", "Returns a randomly sampled real dataset record"],
        ["GET /api/health", "System/model status, including deep_anomaly_detector availability"],
    ],
    col_widths=[4.5, 11.5],
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 7 — SOFTWARE ENGINEERING PRACTICES
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 7: Software Engineering Practices")
body(
    "This phase of the internship focused as much on production-readiness as on new features. "
    "The following practices were audited and, where missing, implemented."
)

heading2("7.1 Security Hardening")
bullet(
    "Removed a hardcoded Flask session secret key fallback that used a fixed, source-visible "
    "string — forgeable if deployed without setting the environment variable. The application "
    "now auto-generates a random per-process key when unset, logging a warning rather than "
    "silently using a predictable default; a stable key is still required for multi-worker "
    "(gunicorn) deployments, since each worker would otherwise mint its own key and break "
    "session validation across workers."
)
bullet("Added .gitignore and .env.example to prevent accidental secret/artifact commits and document required configuration.")
bullet("Replaced bare except: clauses in the prediction pipeline with specific exception types so unrelated bugs are not silently swallowed.")

heading2("7.2 Testing & Continuous Integration")
bullet("Added a pytest suite (17 tests) covering the dynamic threshold logic, analytics risk scoring, the anomaly detector, and Flask API endpoints.")
bullet("Added a GitHub Actions workflow that installs dependencies and runs the full test suite on every push and pull request to main.")

heading2("7.3 Deployment")
bullet("The Docker image now runs the application via Gunicorn (4 workers) instead of Flask's single-threaded development server.")
bullet("torch is pinned to the CPU-only PyPI index so CI and container builds avoid multi-gigabyte CUDA downloads.")

heading2("7.4 Fixed a Dead Feature")
bullet(
    "The Case Management page (templates/cases.html, static/js/cases.js) was fully built but "
    "had no Flask route pointing to it. Added the /cases route and a navigation link, "
    "restoring a previously inaccessible feature."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 8 — MODEL EVALUATION & CRITICAL FINDINGS
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 8: Model Evaluation & Critical Findings")
body(
    "This chapter is the most consequential part of this phase of work. Rather than accepting "
    "the platform's reported model performance at face value, both models were evaluated "
    "against held-out ground truth. The results overturn the platform's implicit performance "
    "claims and surface two concrete defects."
)

heading2("8.1 Finding 1 — The Production RandomForest Was Never Evaluated on Held-Out Data")
body(
    "train.py fits the preprocessor, applies SMOTE, and trains the RandomForest on 100% of the "
    "dataset — there is no train/test split anywhere in the training pipeline. Scoring the "
    "committed model on the same data it was trained on yields a perfect result:"
)
add_table(
    ["Metric", "Value"],
    [["ROC-AUC", "1.0000"], ["Precision", "1.0000"], ["Recall", "1.0000"], ["F1", "1.0000"]],
    col_widths=[6.0, 6.0],
)
body(
    "With unlimited-depth trees, a RandomForest of 100 estimators can memorize its training "
    "set almost exactly; a perfect in-sample score is not evidence of a good model. An "
    "identical RandomForest was retrained on an 80/20 stratified split, evaluated only on the "
    "held-out 20% it never trained on:"
)
add_table(
    ["Metric", "Value"],
    [["Honest test ROC-AUC (unseen data)", "0.5847"]],
    col_widths=[6.0, 6.0],
)
callout(
    "0.5847 AUC is barely better than a coin flip (0.5 = random). This is the real headline "
    "result: on this dataset, fraud does not appear to be strongly predictable from the given "
    "applicant features by a RandomForest of this configuration."
)

heading2("8.2 Root Cause — Confirmed Directly")
body(
    "Per-feature averages between fraud and genuine rows are nearly identical (CIBIL 699.1 vs. "
    "699.5; monthly income Rs.50,852 vs. Rs.50,523; DTI 8.57 vs. 8.95), and every categorical "
    "feature's fraud rate is flat at roughly 2% regardless of category (loan type, purpose, "
    "employment status, property ownership, gender all vary by under one percentage point). "
    "There is no meaningful univariate signal for fraud_flag in this dataset's feature set."
)

heading2("8.3 Finding 2 — Autoencoder Anomaly Detector Evaluation")
body(
    "The autoencoder trains only on genuine applications, so scoring it on genuine rows it "
    "trained on would inflate its apparent performance. Evaluation therefore used only the "
    "held-out 10% validation split of genuine records (4,897 rows, never seen during training) "
    "plus all 1,026 labelled fraud records (never seen by this model at all):"
)
add_table(
    ["Metric", "RandomForest (as deployed, trained-data eval)", "RandomForest (honest, held-out)", "Autoencoder (held-out)"],
    [
        ["ROC-AUC", "1.0000", "0.5847", "0.4947"],
        ["Precision", "1.0000", "n/a", "0.2013"],
        ["Recall", "1.0000", "n/a", "0.0302"],
        ["F1", "1.0000", "n/a", "0.0525"],
    ],
    col_widths=[3.0, 4.5, 3.5, 3.5],
)
body(
    "At AUC 0.4947, the autoencoder is statistically indistinguishable from random guessing on "
    "this dataset — consistent with the root-cause finding in Section 8.2: if the features "
    "carry essentially no fraud signal, no model architecture (supervised or unsupervised) can "
    "extract signal that is not present in the data."
)

heading2("8.4 Finding 3 — A Live Feature-Scale Bug")
body(
    "debt_to_income_ratio in the training CSV ranges from 0 to 102 (mean 8.57, std 9.59) — not "
    "a 0-1 fraction. However, the web form prompts users with placeholder=\"e.g. 0.35\", and "
    "both calculate_dynamic_threshold() and AnalyticsAgent.analyze() apply rules such as "
    "dti > 0.6 assuming a 0-1 scale; the synthetic \"Fill Random\" data generator likewise "
    "produces DTI in the 0.1-0.9 range."
)
callout(
    "Every prediction submitted through the UI as intended (a 0-1 fraction) is scored by a "
    "model that was fit entirely on DTI values in the 0-102 range. This is a live, unambiguous "
    "defect, independent of the weak-signal finding above, and would need fixing regardless of "
    "the dataset's overall predictive ceiling."
)

heading2("8.5 Why This Matters for Evaluation")
body(
    "Presenting an inflated in-sample accuracy figure would have been the easier, more "
    "flattering outcome. Instead, applying standard train/test discipline surfaced a "
    "methodology flaw in the pre-existing training pipeline, a genuine absence of predictive "
    "signal in the underlying dataset, and a concrete, fixable input-scale bug affecting every "
    "live prediction. This is the intended purpose of a rigorous evaluation phase: to establish "
    "what a system actually does, rather than what its unvalidated outputs appear to claim."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 9 — SCREENSHOTS
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 9: Application Screenshots")
body("The following screenshots demonstrate the platform's page layout and prediction workflow.")

heading2("9.1 Home Page")
add_screenshot("home.png", "RiskSense AI — Home Page")

heading2("9.2 Fraud Analysis — Form Input")
add_screenshot("prediction.png", "Fraud Analysis Page — Loan Application Form")

heading2("9.3 Fraud Analysis — Agentic Pipeline Result")
add_screenshot("prediction_result.png", "Complete Agentic Pipeline Result")

heading2("9.4 Analytics Dashboard")
add_screenshot("dashboard.png", "Analytics Dashboard")

heading2("9.5 Agent Architecture Page")
add_screenshot("agents.png", "Agent Architecture Visualization")

heading2("9.6 AI Advisor")
add_screenshot("advisor.png", "AI Advisor — Conversational Interface")

heading2("9.7 About Page")
add_screenshot("about.png", "About Page")

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 10 — RESULTS & DISCUSSION
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 10: Results & Discussion")

heading2("10.1 What Was Delivered")
bullet("A working multi-agent fraud analysis pipeline with a web UI, batch screening, and a documented REST API.")
bullet("A genuine deep learning component (unsupervised autoencoder) integrated end-to-end into the detection and analytics stages, verified to trigger correctly on out-of-distribution input.")
bullet("Removal of a real security defect (hardcoded session secret) and two silent-failure bugs (bare except clauses).")
bullet("An automated test suite and CI pipeline where none existed before.")
bullet("A rigorous evaluation exercise that reversed the project's implicit performance narrative from \"the model works\" to \"the model was never validated, and once validated, performs near chance-level on this dataset\" — plus a concrete, actionable bug (the DTI scale mismatch) that explains part of why.")

heading2("10.2 Advantages of the Agentic Approach")
bullet("Modularity: each agent can be upgraded independently (e.g., analytics rules refined without retraining the model).")
bullet("Transparency: every AgenticReport records a full workflow_steps audit trail.")
bullet("Extensibility: the autoencoder was added as a new signal source without changing the Advisory Agent or any template.")
bullet("Offline operation: the entire pipeline runs without external API calls.")

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 11 — LIMITATIONS & FUTURE WORK
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 11: Limitations & Future Work")

heading2("11.1 Known Limitations")
bullet("Model performance: as documented in Chapter 8, neither model currently demonstrates meaningful fraud discrimination on held-out data for this dataset.")
bullet("The DTI scale mismatch (Section 8.4) affects every live prediction submitted through the intended UI workflow and has not yet been fixed.")
bullet("No real authentication: the /login route captures a role but does not enforce access control on any route.")
bullet("Case data persists only in browser localStorage — no backend database or audit trail.")
bullet("The conversational advisor uses keyword matching, not a true language model.")
bullet("/api/batch processes applications synchronously in a loop rather than vectorized/batched inference.")

heading2("11.2 Recommended Next Steps, in Priority Order")
for item in [
    "Fix the DTI scale mismatch — either rescale the training data to the 0-1 fraction the app uses everywhere else, or change the app's input/threshold logic to match the training data's actual scale.",
    "Add a proper train/test split to train.py and document the model's real, held-out performance as its official reported accuracy.",
    "Investigate whether additional or different features (not present in this dataset) would carry more fraud signal, since the current feature set shows near-zero univariate correlation with the label.",
    "Implement real session-based authentication with route guards.",
    "Persist case data in a backend database with an audit trail.",
    "Replace the keyword-matching advisor with SHAP-based model explanations and/or a local LLM.",
]:
    bullet(item)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# CHAPTER 12 — CONCLUSION
# ══════════════════════════════════════════════════════════════════════════
heading1("Chapter 12: Conclusion")
body(
    "This phase of the RiskSense AI internship extended a working multi-agent fraud analytics "
    "platform with a genuine deep learning component, hardened it for production use, and — "
    "most importantly — subjected the entire system to a rigorous, honest evaluation rather "
    "than accepting its outputs at face value. That evaluation is the most valuable outcome of "
    "this phase: it caught a training methodology flaw that made the production model appear "
    "far more capable than it actually is, and identified a concrete live bug affecting every "
    "real prediction the application serves."
)
body(
    "The engineering discipline demonstrated here — automated testing, CI, secure defaults, and "
    "especially a proper train/test evaluation methodology — is the difference between a demo "
    "that looks impressive and a system whose claims can be trusted. The recommended next steps "
    "in Chapter 11 outline a clear path from the current state to a genuinely validated, "
    "production-credible fraud detection platform."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# REFERENCES
# ══════════════════════════════════════════════════════════════════════════
heading1("References")
refs = [
    "[1] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, \"SMOTE: Synthetic Minority Over-sampling Technique,\" Journal of Artificial Intelligence Research, vol. 16, pp. 321-357, 2002.",
    "[2] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, pp. 5-32, 2001.",
    "[3] D. P. Kingma and J. Ba, \"Adam: A Method for Stochastic Optimization,\" in Proc. International Conference on Learning Representations (ICLR), 2015.",
    "[4] C. Zhou and R. C. Paffenroth, \"Anomaly Detection with Robust Deep Autoencoders,\" in Proc. 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2017, pp. 665-674.",
    "[5] Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.",
    "[6] A. Paszke et al., \"PyTorch: An Imperative Style, High-Performance Deep Learning Library,\" in Proc. Advances in Neural Information Processing Systems (NeurIPS), 2019.",
    "[7] S. Bhattacharyya, S. Jha, K. Tharakunnel, and J. C. Westland, \"Data mining for credit card fraud: A comparative study,\" Decision Support Systems, vol. 50, no. 3, pp. 602-613, 2011.",
]
for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.first_line_indent = Cm(-0.8)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(ref)
    run.font.size = Pt(10)

page_break()

# ══════════════════════════════════════════════════════════════════════════
# APPENDIX
# ══════════════════════════════════════════════════════════════════════════
heading1("Appendix: Key Code Snippets")

heading2("A.1 Tabular Autoencoder (ml/autoencoder_model.py)")
code_block(
    "class TabularAutoencoder(nn.Module):\n"
    "    def __init__(self, input_dim, bottleneck_dim=8):\n"
    "        super().__init__()\n"
    "        self.encoder = nn.Sequential(\n"
    "            nn.Linear(input_dim, 16), nn.ReLU(),\n"
    "            nn.Linear(16, bottleneck_dim), nn.ReLU(),\n"
    "        )\n"
    "        self.decoder = nn.Sequential(\n"
    "            nn.Linear(bottleneck_dim, 16), nn.ReLU(),\n"
    "            nn.Linear(16, input_dim),\n"
    "        )\n"
    "\n"
    "    def forward(self, x):\n"
    "        return self.decoder(self.encoder(x))"
)

heading2("A.2 Anomaly Scoring (ml/anomaly_detector.py)")
code_block(
    "def _score_dataframe(self, row_df):\n"
    "    features = self.predictor.preprocessor.transform(row_df).astype('float32')\n"
    "    with torch.no_grad():\n"
    "        tensor = torch.from_numpy(features)\n"
    "        reconstruction = self.model(tensor)\n"
    "        error = float(((reconstruction - tensor) ** 2).mean().item())\n"
    "    return AnomalyResult(\n"
    "        reconstruction_error=error,\n"
    "        threshold=self.threshold,\n"
    "        is_anomaly=error > self.threshold,\n"
    "    )"
)

heading2("A.3 Dynamic Threshold Calculation (ml/predictor.py)")
code_block(
    "def calculate_dynamic_threshold(form_data: dict) -> float:\n"
    "    BASE_FRAUD_THRESHOLD = 0.40\n"
    "    threshold = BASE_FRAUD_THRESHOLD\n"
    "    cibil = int(float(form_data.get('cibil', 600)))\n"
    "    dti = float(form_data.get('dti', 0.4))\n"
    "    emis = float(form_data.get('emis', 0))\n"
    "    income = float(form_data.get('income', 1))\n"
    "    emi_burden = emis / income if income > 0 else 0\n"
    "\n"
    "    if cibil < 500: threshold -= 0.10\n"
    "    elif cibil > 750: threshold += 0.10\n"
    "    if dti > 0.6: threshold -= 0.05\n"
    "    if emi_burden > 0.5: threshold -= 0.05\n"
    "\n"
    "    return max(0.20, min(0.60, threshold))"
)

heading2("A.4 Honest Evaluation — Held-Out Split (evaluate_anomaly_detector.py)")
code_block(
    "def build_eval_set(df):\n"
    "    genuine = df[df['fraud_flag'] == 0]\n"
    "    fraud = df[df['fraud_flag'] == 1]\n"
    "    rng = np.random.default_rng(42)\n"
    "    indices = rng.permutation(len(genuine))\n"
    "    val_size = int(len(indices) * 0.1)\n"
    "    held_out_genuine = genuine.iloc[indices[:val_size]]\n"
    "    return pd.concat([held_out_genuine, fraud], ignore_index=True)\n"
    "    # -> evaluate only on rows never seen during training"
)

# ─── Footer & Save ───────────────────────────────────────────────────────
add_footer()
output_path = "RiskSense_AI_Internship_Report.docx"
doc.save(output_path)
print(f"[SUCCESS] Report saved: {output_path}")
