"""
RiskSense AI — Project Report Generator
Generates a professional MS Word (.docx) report for the project.
Run: python generate_report.py
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

doc = Document()

# ─── Page Margins ──────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.5)

# ─── Styles Helper ─────────────────────────────────────────────────────────────
def set_font(run, name="Calibri", size=12, bold=False, italic=False, color=None):
    run.font.name  = name
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)

def heading1(text):
    p = doc.add_heading(text, level=1)
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after  = Pt(6)
    run = p.runs[0]
    run.font.name  = "Calibri"
    run.font.size  = Pt(16)
    run.font.bold  = True
    run.font.color.rgb = RGBColor(0x1A, 0x37, 0x6C)
    return p

def heading2(text):
    p = doc.add_heading(text, level=2)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(4)
    run = p.runs[0]
    run.font.name  = "Calibri"
    run.font.size  = Pt(13)
    run.font.bold  = True
    run.font.color.rgb = RGBColor(0x1F, 0x56, 0x9A)
    return p

def heading3(text):
    p = doc.add_heading(text, level=3)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    run = p.runs[0]
    run.font.name  = "Calibri"
    run.font.size  = Pt(12)
    run.font.bold  = True
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
    p.paragraph_format.left_indent  = Cm(1.0)
    p.paragraph_format.space_after  = Pt(6)
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
    # Header row
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
    # Data rows
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
        run = fp.add_run("RiskSense AI — Project Report  |  Confidential")
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
        fp.add_run("  |  Page ")
        fldChar1 = OxmlElement("w:fldChar")
        fldChar1.set(qn("w:fldCharType"), "begin")
        instrText = OxmlElement("w:instrText")
        instrText.text = "PAGE"
        fldChar2 = OxmlElement("w:fldChar")
        fldChar2.set(qn("w:fldCharType"), "end")
        r = OxmlElement("w:r")
        r.append(fldChar1)
        r.append(instrText)
        r.append(fldChar2)
        fp._p.append(r)

# ══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ══════════════════════════════════════════════════════════════════════════════
doc.add_paragraph("\n\n\n")

title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title_p.add_run("RiskSense AI")
tr.font.name  = "Calibri"
tr.font.size  = Pt(32)
tr.font.bold  = True
tr.font.color.rgb = RGBColor(0x1A, 0x37, 0x6C)

subtitle_p = doc.add_paragraph()
subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = subtitle_p.add_run("Agentic Banking Fraud Analytics and Advisory Platform")
sr.font.name  = "Calibri"
sr.font.size  = Pt(16)
sr.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

doc.add_paragraph("\n")

line_p = doc.add_paragraph()
line_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
lr = line_p.add_run("─" * 55)
lr.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

doc.add_paragraph("\n")

for label, val in [
    ("Project Type",    "Machine Learning + Multi-Agent Web Application"),
    ("Domain",         "FinTech / Banking Fraud Detection"),
    ("Technology",     "Python · Flask · scikit-learn · SMOTE · HTML/CSS/JS"),
    ("Date",           datetime.date.today().strftime("%B %d, %Y")),
]:
    lp = doc.add_paragraph()
    lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    bold_run = lp.add_run(f"{label}: ")
    bold_run.font.bold = True
    bold_run.font.size = Pt(12)
    val_run  = lp.add_run(val)
    val_run.font.size  = Pt(12)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# ABSTRACT
# ══════════════════════════════════════════════════════════════════════════════
heading1("Abstract")
body(
    "RiskSense AI is a sophisticated, fully offline agentic web platform designed to detect and "
    "advise on bank loan fraud. Unlike conventional rule-based or single-model approaches, RiskSense "
    "AI employs a three-agent pipeline — Detection Agent, Analytics Agent, and Advisory Agent — "
    "orchestrated by a central coordinator. At the core of the system is a trained ensemble machine "
    "learning model that leverages fourteen applicant-level features including CIBIL score, "
    "debt-to-income ratio, employment status, and loan characteristics to compute a precise fraud "
    "probability for every loan application."
)
body(
    "A key innovation of the platform is its dynamic threshold mechanism, which personalises the "
    "fraud decision boundary based on each applicant's risk profile rather than applying a fixed "
    "universal cutoff. The model was trained on a SMOTE-balanced dataset to eliminate class "
    "imbalance bias, a frequent limitation in fraud detection systems where genuine applications "
    "vastly outnumber fraudulent ones."
)
body(
    "The web application is built on Flask and features a premium glassmorphism UI with multiple "
    "pages: a fraud prediction interface (supporting manual input, synthetic data, or real dataset "
    "records), an interactive analytics dashboard, an agent architecture viewer, and a context-aware "
    "conversational AI advisor. A REST API layer also allows external system integration. "
    "The platform delivers structured, compliance-aware outputs — BLOCK & ESCALATE, MANUAL REVIEW, "
    "or STANDARD APPROVAL PATH — enabling banking officers to make rapid, evidence-backed decisions. "
    "RiskSense AI demonstrates how agentic AI design patterns can be applied to high-stakes financial "
    "workflows without any external API dependencies."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS (Manual)
# ══════════════════════════════════════════════════════════════════════════════
heading1("Table of Contents")
toc_items = [
    ("Chapter 1", "Introduction", "4"),
    ("  1.1", "Background & Problem Statement", "4"),
    ("  1.2", "Project Objectives", "4"),
    ("  1.3", "Scope of the Project", "5"),
    ("  1.4", "Report Organization", "5"),
    ("Chapter 2", "Literature Review", "6"),
    ("  2.1", "Fraud Detection Approaches", "6"),
    ("  2.2", "Class Imbalance & SMOTE", "6"),
    ("  2.3", "Multi-Agent Systems in FinTech", "7"),
    ("Chapter 3", "System Architecture & Design", "7"),
    ("  3.1", "High-Level Architecture", "7"),
    ("  3.2", "Multi-Agent Pipeline Design", "8"),
    ("  3.3", "Dynamic Threshold Mechanism", "8"),
    ("  3.4", "Technology Stack Justification", "9"),
    ("Chapter 4", "Machine Learning Model", "9"),
    ("  4.1", "Dataset Description", "9"),
    ("  4.2", "Feature Engineering & Preprocessing", "10"),
    ("  4.3", "SMOTE Balancing", "10"),
    ("  4.4", "Ensemble Model Training", "10"),
    ("  4.5", "Model Artifacts & Inference", "11"),
    ("Chapter 5", "Agent Implementation", "11"),
    ("  5.1", "Detection Agent", "11"),
    ("  5.2", "Analytics Agent", "12"),
    ("  5.3", "Advisory Agent", "13"),
    ("  5.4", "Orchestrator", "13"),
    ("Chapter 6", "Web Application", "14"),
    ("  6.1", "Flask Backend & API Design", "14"),
    ("  6.2", "Frontend Design", "15"),
    ("  6.3", "Pages & User Flows", "15"),
    ("  6.4", "REST API Documentation", "16"),
    ("Chapter 7", "Results & Discussion", "16"),
    ("Chapter 8", "Conclusion & Future Work", "17"),
    ("References", "", "18"),
    ("Appendix", "Key Code Snippets", "19"),
]
for num, title, page in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{num}  {title}")
    run.font.size = Pt(11)
    if "Chapter" in num or num in ("References", "Appendix"):
        run.font.bold = True
    tab = p.add_run(f"\t{page}")
    tab.font.size = Pt(11)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(15), WD_ALIGN_PARAGRAPH.RIGHT)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 1 — INTRODUCTION
# ══════════════════════════════════════════════════════════════════════════════
heading1("Chapter 1: Introduction")

heading2("1.1 Background & Problem Statement")
body(
    "The Indian banking sector disburses millions of loans annually across segments including "
    "home loans, personal loans, vehicle loans, and education loans. Fraudulent loan applications "
    "represent a significant and growing threat, causing substantial financial losses to lending "
    "institutions and distorting credit allocation in the economy. Traditional fraud detection "
    "approaches relied predominantly on manual review by credit analysts and hard-coded rule "
    "engines. These methods are slow, inconsistent, and increasingly ineffective against "
    "sophisticated fraud patterns that mimic legitimate borrower profiles."
)
body(
    "The CIBIL (Credit Information Bureau India Limited) score is a central instrument in Indian "
    "credit risk assessment, ranging from 300 to 900, with scores above 750 generally considered "
    "excellent. However, CIBIL alone is insufficient to detect fraud — a fraudster may present "
    "a synthesized or stolen identity with a high credit score while the underlying application "
    "contains multiple financial anomalies. A comprehensive fraud detection system must therefore "
    "consider the holistic applicant profile including income, debt obligations, employment "
    "stability, loan-to-income ratios, and behavioural patterns."
)
body(
    "Machine learning methods have demonstrated superior fraud detection capabilities, but most "
    "production deployments present predictions as a single probability value with no interpretable "
    "reasoning or actionable guidance for bank officers. RiskSense AI addresses this gap by "
    "wrapping a high-accuracy ensemble model within a structured multi-agent pipeline that "
    "produces human-readable risk explanations and compliance-ready recommendations."
)

heading2("1.2 Project Objectives")
for obj in [
    "Design and implement a multi-agent AI system for bank loan fraud detection that operates fully offline without external API dependencies.",
    "Train a robust ensemble ML model on a SMOTE-balanced dataset to ensure fair and calibrated fraud probability estimates.",
    "Implement a dynamic fraud classification threshold that adapts to individual applicant risk profiles rather than applying a fixed cutoff.",
    "Build a full-stack web application with a premium UI that supports manual entry, synthetic data, and real dataset-based predictions.",
    "Provide structured, compliance-aware recommendations (BLOCK & ESCALATE / MANUAL REVIEW / STANDARD APPROVAL PATH) to banking officers.",
    "Expose a REST API for integration with external banking systems.",
    "Deliver a context-aware conversational advisor that can explain fraud decisions in natural language.",
]:
    bullet(obj)

heading2("1.3 Scope of the Project")
body(
    "RiskSense AI is scoped as a decision-support platform, not an autonomous approval engine. "
    "The system ingests loan application data, processes it through a three-agent pipeline, and "
    "outputs structured recommendations. Final credit decisions remain with authorized banking "
    "officers. The platform covers:"
)
for item in [
    "Fraud detection for five loan types: Home, Personal, Car, Education, and Business loans.",
    "Analysis of fourteen applicant features covering financial, demographic, and employment dimensions.",
    "Three operational modes: manual form input, synthetic random data generation, and sampling of real dataset records.",
    "A conversational advisor supporting post-prediction queries about risk drivers and recommended actions.",
    "REST API for external system integration (POST /api/analyze and POST /api/chat).",
]:
    bullet(item)

body(
    "Out of scope: real-time database integration, customer-facing portals, regulatory filing "
    "automation, and model retraining pipelines (training is handled separately in the Jupyter notebook)."
)

heading2("1.4 Report Organization")
body(
    "This report is organized as follows: Chapter 2 reviews related literature on fraud detection "
    "and multi-agent systems. Chapter 3 details the system architecture. Chapter 4 covers the "
    "machine learning model. Chapter 5 describes each agent's implementation. Chapter 6 "
    "documents the web application. Chapter 7 presents results and discussion. Chapter 8 "
    "concludes with future work directions."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 2 — LITERATURE REVIEW
# ══════════════════════════════════════════════════════════════════════════════
heading1("Chapter 2: Literature Review")

heading2("2.1 Fraud Detection Approaches")
body(
    "Fraud detection in financial services has evolved through three broad paradigms. "
    "Rule-based systems use expert-defined thresholds (e.g., reject if CIBIL < 550) that are "
    "transparent but brittle and unable to capture complex multivariate fraud patterns. "
    "Statistical models such as logistic regression improved pattern recognition but struggled "
    "with non-linear feature interactions prevalent in fraud data."
)
body(
    "Modern machine learning approaches — particularly ensemble methods such as Random Forests, "
    "Gradient Boosted Trees (XGBoost, LightGBM), and stacked classifiers — have demonstrated "
    "state-of-the-art fraud detection accuracy. These methods aggregate multiple weak learners "
    "to produce robust predictions that generalize well across diverse applicant profiles. "
    "Studies by Bhattacharyya et al. (2011) and West & Bhattacharya (2016) confirmed that "
    "ensemble models consistently outperform single classifiers on imbalanced financial datasets."
)
body(
    "Deep learning methods, including LSTM networks for sequential transaction data and "
    "autoencoders for anomaly detection, have shown promise for transaction-level fraud but "
    "are less interpretable and require substantially more data than tabular loan application "
    "datasets typically provide."
)

heading2("2.2 Class Imbalance & SMOTE")
body(
    "A fundamental challenge in fraud detection is severe class imbalance: fraudulent applications "
    "typically constitute only 1–5% of total loan applications. Training a classifier on such "
    "data without mitigation results in a model that classifies all applications as genuine and "
    "achieves high accuracy but zero fraud recall — a catastrophic outcome for a fraud detection system."
)
body(
    "SMOTE (Synthetic Minority Over-sampling Technique), introduced by Chawla et al. (2002), "
    "addresses this by generating synthetic minority class (fraud) samples through interpolation "
    "between existing minority samples in feature space. Unlike simple oversampling (which "
    "duplicates existing samples and risks overfitting), SMOTE introduces controlled diversity "
    "into the minority class representation, enabling classifiers to learn broader decision "
    "boundaries for fraud detection. RiskSense AI uses the imbalanced-learn library's SMOTE "
    "implementation to produce the balanced training dataset `loan_fraud_smote_balanced_dataset.csv`."
)

heading2("2.3 Multi-Agent Systems in FinTech")
body(
    "Multi-agent systems (MAS) decompose complex tasks into specialized autonomous agents that "
    "collaborate to produce outputs beyond the capability of any single component. In FinTech "
    "applications, MAS architectures have been applied to algorithmic trading (agents monitoring "
    "different market signals), anti-money laundering (separate agents for transaction analysis, "
    "network analysis, and regulatory reporting), and credit risk management."
)
body(
    "The agentic design pattern adopted by RiskSense AI — sequential pipeline with a central "
    "orchestrator — is well-suited to fraud detection because each stage adds a distinct "
    "analytical dimension: raw ML probability (Detection Agent), human-interpretable risk "
    "signals (Analytics Agent), and actionable banking recommendations (Advisory Agent). "
    "This mirrors how skilled fraud analysts actually work in practice: moving from model score "
    "to investigation to recommendation."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 3 — SYSTEM ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
heading1("Chapter 3: System Architecture & Design")

heading2("3.1 High-Level Architecture")
body(
    "RiskSense AI follows a layered architecture consisting of a Presentation Layer (Flask "
    "templates + REST API), an Orchestration Layer (RiskSenseOrchestrator), an Agent Layer "
    "(three specialized agents), and an ML Inference Layer (FraudPredictor + model artifacts). "
    "The data flow for a prediction request is illustrated below:"
)
code_block(
    "User Input (Web Form / API JSON)\n"
    "        ↓\n"
    "Flask Route (/prediction or /api/analyze)\n"
    "        ↓\n"
    "RiskSenseOrchestrator.run_pipeline(form_data)\n"
    "        ↓\n"
    "┌─────────────────────────────────────────────┐\n"
    "│  1. DetectionAgent.score_application()      │\n"
    "│     └─ FraudPredictor.predict_from_form()   │\n"
    "│        └─ Preprocessor → Ensemble Model     │\n"
    "│        └─ Dynamic Threshold Calculation     │\n"
    "│  2. AnalyticsAgent.analyze()                │\n"
    "│     └─ Rule-based risk signal extraction    │\n"
    "│     └─ Composite risk score computation     │\n"
    "│  3. AdvisoryAgent.advise()                  │\n"
    "│     └─ Decision: BLOCK / REVIEW / APPROVE  │\n"
    "│     └─ Prioritized action items             │\n"
    "└─────────────────────────────────────────────┘\n"
    "        ↓\n"
    "AgenticReport (returned to Flask → rendered to HTML or JSON)"
)

heading2("3.2 Multi-Agent Pipeline Design")
body(
    "The pipeline is strictly sequential with information flowing forward between agents. "
    "Each agent produces a typed dataclass report that the next agent consumes:"
)
add_table(
    ["Agent", "Input", "Output Dataclass", "Key Output Fields"],
    [
        ["DetectionAgent", "form_data dict", "DetectionReport", "PredictionResult, confidence_band, summary"],
        ["AnalyticsAgent", "form_data + PredictionResult", "AnalyticsReport", "risk_score, risk_level, signals[]"],
        ["AdvisoryAgent", "form_data + DetectionReport + AnalyticsReport", "AdvisoryReport", "decision, items[], compliance_note"],
        ["Orchestrator", "form_data", "AgenticReport", "All above + timestamp, executive_summary"],
    ],
    col_widths=[3.5, 3.5, 3.5, 5.5]
)

heading2("3.3 Dynamic Threshold Mechanism")
body(
    "A key innovation in RiskSense AI is the profile-adaptive fraud classification threshold. "
    "Instead of classifying every application using a fixed 50% probability cutoff (standard "
    "sklearn default) or even a fixed 40% cutoff, the system computes a personalized threshold "
    "for each applicant based on their risk profile before running the model:"
)
add_table(
    ["Condition", "Threshold Adjustment", "Rationale"],
    [
        ["Base threshold", "40.0%", "Conservative default below standard 50% for fraud sensitivity"],
        ["CIBIL < 500", "−10% (stricter)", "Very poor credit indicates higher fraud/default risk"],
        ["CIBIL > 750", "+10% (lenient)", "Excellent credit warrants relaxed fraud threshold"],
        ["DTI > 0.60", "−5% (stricter)", "High debt burden correlates with stressed/fraudulent applications"],
        ["EMI burden > 50% of income", "−5% (stricter)", "Severe income commitment signals financial distress or misrepresentation"],
        ["Final clamp", "min 20%, max 60%", "Prevents extreme threshold values that could cause all-fraud or all-genuine outcomes"],
    ],
    col_widths=[4.5, 3.5, 8.0]
)
body(
    "This mechanism ensures that high-risk applicant profiles are evaluated with greater scrutiny "
    "(lower threshold = more likely to flag as fraud), while financially strong applicants benefit "
    "from a relaxed threshold that reduces false positives."
)

heading2("3.4 Technology Stack Justification")
add_table(
    ["Component", "Technology", "Version", "Justification"],
    [
        ["Web Framework", "Flask", "3.0.0", "Lightweight Python web framework; minimal overhead for ML serving"],
        ["ML Core", "scikit-learn", "1.6.1", "Industry-standard; ensemble model training and preprocessing"],
        ["Imbalance Handling", "imbalanced-learn", "0.14.2", "SMOTE implementation; seamless sklearn pipeline integration"],
        ["Data Processing", "pandas / numpy", "2.3.1 / 2.0.2", "Efficient tabular data manipulation and numerical operations"],
        ["Model Serialization", "joblib", "1.3.2", "Efficient serialization of large sklearn objects"],
        ["Frontend", "HTML5 / CSS3 / Vanilla JS", "—", "No framework overhead; full control over glassmorphism design"],
        ["Containerization", "Docker", "—", "Reproducible deployment; isolated environment"],
    ],
    col_widths=[3.5, 3.5, 2.5, 7.0]
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 4 — MACHINE LEARNING MODEL
# ══════════════════════════════════════════════════════════════════════════════
heading1("Chapter 4: Machine Learning Model")

heading2("4.1 Dataset Description")
body(
    "The primary dataset, `loan_applications.csv` (~11.9 MB), contains historical loan application "
    "records with a binary target variable `fraud_flag` (1 = Fraud, 0 = Genuine). The dataset "
    "covers five loan product categories and captures fourteen applicant attributes spanning "
    "financial, employment, demographic, and loan structure dimensions. A SMOTE-balanced version "
    "`loan_fraud_smote_balanced_dataset.csv` (~30.2 MB) is used for model training to address "
    "class imbalance."
)

heading2("4.2 Feature Engineering & Preprocessing")
body("The fourteen model input features are described in the table below:")
add_table(
    ["Feature", "Type", "Range / Values", "Description"],
    [
        ["loan_type", "Categorical", "Home/Personal/Car/Education/Business", "Product category of the loan"],
        ["loan_amount_requested", "Float", "₹1,00,000 – ₹50,00,000", "Loan amount applied for (INR)"],
        ["loan_tenure_months", "Integer", "12 – 360 months", "Repayment period in months"],
        ["interest_rate_offered", "Float", "7.0% – 18.0%", "Annual interest rate on the loan"],
        ["purpose_of_loan", "Categorical", "8 categories", "Stated purpose (Business, Education, Medical, etc.)"],
        ["employment_status", "Categorical", "6 categories", "Salaried / Self-Employed / Unemployed / etc."],
        ["monthly_income", "Float", "₹15,000 – ₹2,00,000", "Applicant's monthly income"],
        ["cibil_score", "Integer", "300 – 900", "Indian credit bureau score"],
        ["existing_emis_monthly", "Float", "₹0 – ₹50,000", "Monthly EMI obligations on existing loans"],
        ["debt_to_income_ratio", "Float", "0.10 – 0.90", "Ratio of total debt to gross income"],
        ["property_ownership_status", "Categorical", "Owned/Rented/Jointly", "Property ownership of applicant"],
        ["applicant_age", "Integer", "18 – 70 years", "Age of the primary applicant"],
        ["gender", "Categorical", "Male/Female/Other", "Applicant gender"],
        ["number_of_dependents", "Integer", "0 – 5", "Number of financial dependents"],
    ],
    col_widths=[4.0, 2.5, 4.5, 5.0]
)
body(
    "Categorical features are encoded using the fitted `preprocessor.pkl` artifact, which applies "
    "consistent transformation during both training and inference to prevent data leakage. "
    "Numerical features are scaled appropriately within the preprocessing pipeline."
)

heading2("4.3 SMOTE Balancing")
body(
    "Fraudulent loan applications represent a small minority of all applications. Training on "
    "the raw imbalanced dataset would bias the model towards predicting GENUINE for all inputs, "
    "achieving high accuracy but failing completely at fraud detection — the very task the system "
    "is designed to accomplish."
)
body(
    "The imbalanced-learn library's SMOTE implementation was applied to generate synthetic "
    "fraudulent application records by interpolating between existing fraud samples in the "
    "14-dimensional feature space. The resulting balanced dataset approximately equalizes the "
    "fraud and genuine class distributions, enabling the model to learn robust fraud decision "
    "boundaries. The balanced dataset (30.2 MB vs. raw 11.9 MB) reflects the substantial "
    "volume of synthetic samples generated."
)

heading2("4.4 Ensemble Model Training")
body(
    "The model is trained in `bankloanfraud.ipynb` (Jupyter Notebook) on the SMOTE-balanced "
    "dataset. An ensemble approach combines multiple base learners to produce a final prediction "
    "that is more robust than any individual model. Ensemble methods such as Random Forest "
    "use bagging to train independent decision trees on bootstrapped subsets of the training "
    "data and average their probability outputs — this reduces variance without significantly "
    "increasing bias."
)
body(
    "The trained model is serialized as `loan_fraud_ensemble_model.pkl` (46 MB), reflecting "
    "the complexity of the ensemble (large number of estimators/trees). During inference, "
    "`model.predict_proba(X)[0][1]` is used to extract the continuous fraud probability, "
    "which is then compared against the dynamic threshold to produce the binary FRAUD/GENUINE label."
)

heading2("4.5 Model Artifacts & Inference")
body(
    "Two artifacts are required for production inference:"
)
bullet("loan_fraud_ensemble_model.pkl (46 MB) — The trained ensemble classifier")
bullet("preprocessor.pkl (4.8 KB) — The fitted feature transformer (encodes categoricals, scales numerics)")
body(
    "The `FraudPredictor` class in `ml/predictor.py` loads both artifacts at startup using joblib "
    "and provides three inference methods: `predict_from_form()` for web form input, "
    "`predict_random_dataset_record()` for sampling real dataset records, and "
    "`generate_random_form_data()` for synthetic test data generation."
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 5 — AGENT IMPLEMENTATION
# ══════════════════════════════════════════════════════════════════════════════
heading1("Chapter 5: Agent Implementation")

heading2("5.1 Detection Agent")
body(
    "The Detection Agent (`agents/detection_agent.py`) is the first stage of the pipeline and "
    "is responsible for producing a probabilistic fraud assessment using the trained ML model. "
    "It wraps the `FraudPredictor` and translates raw model output into a structured "
    "`DetectionReport` dataclass."
)
body("The agent classifies the prediction into three confidence bands:")
add_table(
    ["Confidence Band", "Condition", "Status", "Action"],
    [
        ["High Risk", "is_fraud = True (prob ≥ dynamic threshold)", "alert 🔴", "Fraud flagged; escalate"],
        ["Elevated Risk", "prob ≥ 30% but below threshold", "warning 🟡", "Enhanced review recommended"],
        ["Low Risk", "prob < 30%", "success 🟢", "Genuine; standard processing"],
    ],
    col_widths=[3.5, 5.5, 2.5, 4.5]
)
body(
    "The agent supports two modes: `score_application()` for user-submitted form data, "
    "and `score_dataset_record()` for randomly sampling a record from the live dataset "
    "(which also captures the actual fraud label for comparison against the model prediction)."
)

heading2("5.2 Analytics Agent")
body(
    "The Analytics Agent (`agents/analytics_agent.py`) interprets the application features "
    "through a set of domain-expert rules to produce a composite risk score and a list of "
    "named RiskSignals explaining the key risk drivers. This stage makes the ML prediction "
    "interpretable to non-technical banking officers."
)
body("The risk scoring rules are:")
add_table(
    ["Risk Factor", "Condition", "Points Added", "Severity"],
    [
        ["CIBIL Score", "< 550 (below lending band)", "+25", "High"],
        ["CIBIL Score", "550–649 (moderate)", "+12", "Medium"],
        ["Debt-to-Income", "> 0.65 (exceeds prudent limit)", "+22", "High"],
        ["Debt-to-Income", "0.50–0.65 (elevated)", "+10", "Medium"],
        ["Loan-to-Annual-Income", "> 8× annual income", "+18", "High"],
        ["Existing EMIs", "> 50% of monthly income", "+15", "High"],
        ["Employment Status", "Unemployed or Student", "+20", "High"],
        ["Applicant Age", "< 21 or > 65 years", "+8", "Medium"],
        ["Model Probability Boost", "int(probability × 40)", "0–40", "Dynamic"],
    ],
    col_widths=[4.5, 5.0, 2.5, 4.0]
)
body("Risk levels based on final composite score (0–100):")
add_table(
    ["Score Range", "Risk Level", "UI Status"],
    [
        ["0 – 24", "Low", "Success (Green)"],
        ["25 – 44", "Moderate", "Warning (Amber)"],
        ["45 – 69", "High", "Warning (Amber)"],
        ["70 – 100", "Critical", "Alert (Red)"],
    ],
    col_widths=[4.0, 4.0, 4.0]
)

heading2("5.3 Advisory Agent")
body(
    "The Advisory Agent (`agents/advisory_agent.py`) is the final stage of the pipeline, "
    "translating the detection and analytics outputs into actionable banking recommendations. "
    "It produces one of three structured decisions:"
)
add_table(
    ["Decision", "Trigger Condition", "Priority Actions"],
    [
        ["BLOCK & ESCALATE", "Model predicts FRAUD (prob ≥ dynamic threshold)", "P0: Freeze application\nP0: Enhanced Due Diligence (EDD)\nP1: Route to fraud investigation unit\nP1: File STR/SAR per regulatory policy"],
        ["MANUAL REVIEW", "Risk score ≥ 45 OR fraud probability ≥ 30%", "P1: Assign senior credit analyst\nP2: Request income proof & bank statements\nP2: Apply 90-day enhanced monitoring post-disbursement"],
        ["STANDARD APPROVAL PATH", "Risk score < 45 AND probability < 30%", "P2: Standard KYC and credit underwriting\nP3: Routine portfolio monitoring"],
    ],
    col_widths=[4.0, 4.5, 7.5]
)
body(
    "All advisory outputs include a mandatory compliance note: "
    "'Advisory generated by RiskSense AI agent pipeline. Final disposition remains with "
    "authorized bank officers; this is decision support, not autonomous approval.' "
    "This ensures the platform operates within appropriate regulatory boundaries."
)
body(
    "Additionally, the top two high-severity signals from the Analytics Agent are appended "
    "as P2-priority mitigation actions in all scenarios, ensuring specific financial risk "
    "factors are always surfaced to reviewing officers."
)

heading2("5.4 Orchestrator")
body(
    "The `RiskSenseOrchestrator` (`agents/orchestrator.py`) coordinates the three agents "
    "and manages the overall workflow. It exposes two primary pipeline methods:"
)
bullet("run_pipeline(form_data): For manual and synthetic form submissions. Runs all three agents sequentially and compiles the final AgenticReport.")
bullet("run_dataset_sample(): Randomly selects a real record from loan_applications.csv, runs the full pipeline, and includes the actual fraud label for model performance comparison.")
body(
    "The orchestrator also implements `chat_response()`, a local heuristic conversational "
    "engine for the Advisor page. Using keyword matching on user queries, it generates "
    "context-aware natural language responses explaining risk levels, recommended actions, "
    "and pipeline behaviour — without requiring any external LLM API."
)
body("Each pipeline execution generates a timestamped AgenticReport containing:")
for field in [
    "platform: Platform name string",
    "timestamp: UTC timestamp of the analysis",
    "application_summary: Key application fields (loan type, amount, CIBIL, DTI, employment, income)",
    "detection: Full DetectionReport",
    "analytics: Full AnalyticsReport with all RiskSignals",
    "advisory: Full AdvisoryReport with all AdvisoryItems",
    "workflow_steps: List of AgentStep objects recording each agent's contribution",
    "executive_summary: One-line summary string for display",
]:
    bullet(field)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 6 — WEB APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
heading1("Chapter 6: Web Application")

heading2("6.1 Flask Backend & API Design")
body(
    "The Flask application (`app.py`) initializes the `FraudPredictor` and "
    "`RiskSenseOrchestrator` at startup (loading ML artifacts into memory once) and "
    "serves both HTML pages and REST API endpoints. The application runs on all network "
    "interfaces (0.0.0.0:5000), making it accessible across local networks. Debug mode "
    "is controlled via the `FLASK_DEBUG` environment variable."
)
body(
    "Custom error handlers for 404 (Not Found) and 500 (Internal Server Error) render "
    "styled HTML error pages consistent with the platform's design system, ensuring a "
    "professional user experience even during failure scenarios."
)

heading2("6.2 Frontend Design")
body(
    "The frontend employs a glassmorphism design language — a modern aesthetic characterized "
    "by frosted-glass card surfaces, translucent overlays, subtle backdrop blur filters, "
    "and vibrant gradient backgrounds. This creates a premium, futuristic visual identity "
    "appropriate for an AI-powered financial analytics platform."
)
body("Key design elements include:")
for item in [
    "Rich dark-mode gradient backgrounds (deep navy to midnight blue)",
    "Semi-transparent card components with backdrop-filter: blur() for glassmorphism effect",
    "Accent colors using electric blue and cyan gradients for interactive elements",
    "Smooth CSS micro-animations for page transitions and result reveals",
    "Color-coded status indicators: green (genuine/low risk), amber (elevated/moderate), red (fraud/critical)",
    "Google Fonts integration for premium typography (Calibri-equivalent web fonts)",
]:
    bullet(item)

heading2("6.3 Pages & User Flows")
add_table(
    ["URL Route", "Page", "Description & User Flow"],
    [
        ["/", "Home", "Landing page with platform overview and navigation to core features."],
        ["/prediction", "Fraud Analysis", "Core page with 3 modes: (1) Fill 14 fields manually → Submit → View agentic report. (2) Click 'Fill Random' → Auto-populate form with synthetic data. (3) Click 'Load Dataset Record' → Loads real application with actual fraud label for comparison."],
        ["/dashboard", "Analytics Dashboard", "Visual analytics dashboard showing prediction statistics and risk distributions."],
        ["/agents", "Agent Architecture", "Interactive visualization of the three-agent pipeline design and agent responsibilities."],
        ["/advisor", "AI Advisor", "Context-aware conversational interface. After prediction, user can carry application context to chat with the advisor about risk drivers and recommended actions."],
        ["/about", "About", "Platform overview, technology stack description, and compliance information."],
        ["/compare", "Compare", "Side-by-side comparison view for evaluating multiple application scenarios."],
    ],
    col_widths=[2.5, 3.0, 10.5]
)

heading2("6.4 REST API Documentation")
add_table(
    ["Endpoint", "Method", "Input", "Output"],
    [
        ["POST /api/analyze", "POST", "JSON: loan_type, loan_amount, tenure, interest, purpose (+ other fields)", "JSON: prediction {label, probability, is_fraud}, analytics {risk_score, risk_level, signals[]}, advisory {decision, items[]}, executive_summary"],
        ["POST /api/chat", "POST", "JSON: message (string), application_data (optional form_data object)", "JSON: {reply: string} — natural language advisory response"],
        ["GET /api/dataset/random", "GET", "None", "JSON: {record_index, form_data} — a randomly selected real dataset record"],
    ],
    col_widths=[3.5, 2.0, 5.0, 5.5]
)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 7 — SCREENSHOTS
# ══════════════════════════════════════════════════════════════════════════════
heading1("Chapter 7: Application Screenshots")
body(
    "The following screenshots demonstrate the RiskSense AI platform in operation, "
    "showcasing the premium glassmorphism design, multi-page layout, and complete "
    "fraud analysis pipeline from data entry through to agentic recommendation."
)

import os

SCREENSHOTS_DIR = r"C:\Users\jayag\Downloads\Copy of bankloanfraud-ai\screenshots"

def add_screenshot(filename, caption):
    path = os.path.join(SCREENSHOTS_DIR, filename)
    if os.path.exists(path):
        try:
            doc.add_picture(path, width=Inches(6.0))
            last_para = doc.paragraphs[-1]
            last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
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

heading2("7.1 Home Page")
body("The landing page greets users with a neural network particle animation background, "
     "the platform title, and quick navigation to the Fraud Analysis and AI Advisor modules.")
add_screenshot("home.png", "RiskSense AI — Home Page with Neural Network Animation Background")

heading2("7.2 Fraud Analysis — Form Input")
body("The Prediction page presents a multi-step form with loan details, applicant information, "
     "and a real-time risk estimator bar that updates as users fill in the fields.")
add_screenshot("prediction.png", "Fraud Analysis Page — Loan Application Form with Live Risk Bar")

heading2("7.3 Fraud Analysis — Agentic Pipeline Result")
body("After submitting an application, the system displays a full Agentic Report: Executive Summary, "
     "Detection Agent output (fraud probability, confidence band, threshold), Agent Workflow Trace, "
     "Analytics Agent Risk Signals, and Advisory Agent Recommendations.")
add_screenshot("prediction_result.png", "Fraud Analysis — Complete Agentic Pipeline Result with Detection, Analytics & Advisory Outputs")

heading2("7.4 Analytics Dashboard")
body("The Dashboard page provides a visual overview of the platform's analytics capabilities "
     "and key metrics relevant to fraud detection performance.")
add_screenshot("dashboard.png", "Analytics Dashboard — Platform Metrics and Risk Overview")

heading2("7.5 Agent Architecture Page")
body("The Agents page presents an interactive visualization of the three-agent pipeline, "
     "explaining each agent's role, inputs, and outputs in the fraud detection workflow.")
add_screenshot("agents.png", "Agent Architecture — Three-Agent Pipeline Visualization")

heading2("7.6 AI Advisor")
body("The Advisor page provides a conversational interface where users can ask natural-language "
     "questions about fraud risk, risk drivers, and recommended banking actions — with full "
     "context-linking to recent predictions.")
add_screenshot("advisor.png", "AI Advisor — Context-Aware Conversational Advisory Interface")

heading2("7.7 About Page")
body("The About page documents the platform's purpose, technology stack, agent architecture "
     "overview, and compliance disclaimer.")
add_screenshot("about.png", "About Page — Platform Overview and Technology Description")

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 8 — RESULTS & DISCUSSION
# ══════════════════════════════════════════════════════════════════════════════
heading1("Chapter 8: Results & Discussion")

heading2("7.1 System Behaviour")
body(
    "RiskSense AI successfully integrates a trained ensemble model within a structured multi-agent "
    "framework to produce rich, actionable fraud analysis outputs. The system demonstrates several "
    "notable behavioural characteristics:"
)
bullet("Decision Quality: The dynamic threshold mechanism adapts the fraud decision boundary to applicant risk profiles, reducing false positives for financially strong applicants (high CIBIL, low DTI) while maintaining high sensitivity for high-risk profiles (low CIBIL, high DTI, high EMI burden).")
bullet("Risk Explainability: The Analytics Agent's rule-based signal extraction provides human-interpretable explanations for every prediction, bridging the 'black box' gap that is a common criticism of ensemble ML models in high-stakes applications.")
bullet("Compliance Awareness: The Advisory Agent consistently attaches compliance notes to all outputs, ensuring users understand that RiskSense AI is a decision support tool, not an autonomous decision maker — an important regulatory and ethical consideration.")
bullet("Three-Mode Verification: The ability to load real dataset records with known fraud labels allows banking officers and data scientists to directly observe model predictions against ground truth, providing an in-application model validation capability.")

heading2("7.2 Advantages of the Agentic Approach")
body(
    "The three-agent pipeline offers structural advantages over monolithic fraud scoring systems:"
)
bullet("Modularity: Each agent can be independently upgraded without affecting others. For example, the Analytics Agent's risk rules can be refined by domain experts without retraining the ML model.")
bullet("Transparency: The workflow_steps array in every AgenticReport captures each agent's contribution, providing a complete audit trail of how a decision was reached.")
bullet("Extensibility: A fourth agent (e.g., a Document Verification Agent or a Network Fraud Agent) can be inserted into the pipeline by the Orchestrator without architectural changes to existing agents.")
bullet("Offline Operation: The entire pipeline operates without external API calls, ensuring zero latency from network requests, complete privacy of applicant data, and reliable operation in air-gapped banking environments.")

heading2("7.3 Limitations")
body(
    "The current implementation has several known limitations that future work should address:"
)
bullet("Model Interpretability: While the Analytics Agent provides rule-based explanations, the ensemble model's internal feature importance is not surfaced to users. SHAP (SHapley Additive exPlanations) values would provide model-native explanations.")
bullet("Static Training: The model is trained once from the notebook and does not support online learning or periodic retraining from new data without manual intervention.")
bullet("Conversational Depth: The Advisor's `chat_response()` uses keyword matching rather than true natural language understanding. Integration with a local LLM (e.g., Ollama + Llama 3) would significantly enhance conversational quality.")
bullet("No Authentication: The web application currently lacks user authentication, making it unsuitable for direct deployment in a multi-user banking environment without an authentication layer.")

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER 9 — CONCLUSION & FUTURE WORK
# ══════════════════════════════════════════════════════════════════════════════
heading1("Chapter 9: Conclusion & Future Work")

heading2("8.1 Conclusion")
body(
    "RiskSense AI successfully demonstrates how agentic AI design patterns can be applied "
    "to bank loan fraud detection to produce a system that is simultaneously accurate, "
    "interpretable, and actionable. By wrapping a SMOTE-balanced ensemble model within "
    "a three-agent pipeline, the platform bridges the gap between raw ML output and "
    "practical banking workflow — a gap that prevents many high-accuracy fraud models "
    "from achieving real-world adoption."
)
body(
    "The dynamic threshold mechanism, a novel contribution of this project, addresses the "
    "fundamental inadequacy of fixed classification cutoffs for heterogeneous applicant "
    "populations. By personalizing the fraud decision boundary based on each applicant's "
    "credit and financial profile, the system achieves better calibration across the "
    "full spectrum of applicant risk levels."
)
body(
    "The full-stack web application, with its premium glassmorphism design, multiple "
    "prediction modes, REST API, and context-aware conversational advisor, demonstrates "
    "that AI-powered fraud detection tools can offer a professional, user-friendly "
    "experience comparable to commercial FinTech products."
)

heading2("8.2 Future Work")
body("Several enhancements are planned for future iterations of RiskSense AI:")
for item in [
    "SHAP Integration: Add SHAP (SHapley Additive exPlanations) to surface model-native feature importance alongside the rule-based Analytics Agent explanations, providing dual-layer interpretability.",
    "Local LLM Integration: Replace the keyword-matching chat_response() with a locally hosted LLM (e.g., Ollama with Llama 3 or Mistral) to deliver true natural language advisory conversations without external API dependencies.",
    "Real-Time Database Integration: Connect to a live loan application database (PostgreSQL or MongoDB) for real-time prediction on incoming applications rather than static dataset sampling.",
    "Model Retraining Pipeline: Implement an automated retraining trigger when model performance metrics degrade, using newly labelled application data to keep the ensemble current.",
    "User Authentication & Roles: Add Flask-Login or JWT-based authentication with role differentiation (Analyst, Supervisor, Compliance Officer) to control access to sensitive prediction outputs.",
    "Continuous Monitoring Dashboard: Extend the analytics dashboard with model performance tracking over time — including precision, recall, F1-score, and AUC — to detect model drift.",
    "Document Verification Agent: Add a fourth agent that cross-references extracted document metadata (income proof, identity documents) with application-stated values to detect document fraud.",
    "Mobile-Responsive Design: Optimize the glassmorphism UI for mobile and tablet viewports to support field officer use cases.",
]:
    bullet(item)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# REFERENCES
# ══════════════════════════════════════════════════════════════════════════════
heading1("References")

refs = [
    "[1] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, \"SMOTE: Synthetic Minority Over-sampling Technique,\" Journal of Artificial Intelligence Research, vol. 16, pp. 321–357, 2002.",
    "[2] S. Bhattacharyya, S. Jha, K. Tharakunnel, and J. C. Westland, \"Data mining for credit card fraud: A comparative study,\" Decision Support Systems, vol. 50, no. 3, pp. 602–613, 2011.",
    "[3] J. West and M. Bhattacharya, \"Intelligent financial fraud detection: A comprehensive review,\" Computers & Security, vol. 57, pp. 47–66, 2016.",
    "[4] T. Chen and C. Guestrin, \"XGBoost: A Scalable Tree Boosting System,\" in Proc. 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2016, pp. 785–794.",
    "[5] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
    "[6] S. J. Russell and P. Norvig, Artificial Intelligence: A Modern Approach, 4th ed. Hoboken, NJ: Pearson, 2021, ch. 2 (Intelligent Agents).",
    "[7] Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
    "[8] M. Lundberg and S. I. Lee, \"A unified approach to interpreting model predictions,\" in Proc. Advances in Neural Information Processing Systems (NeurIPS), 2017.",
    "[9] G. Paleologo, A. Elisseeff, and G. Antonini, \"Subagging for Credit Scoring Models,\" European Journal of Operational Research, vol. 201, no. 2, pp. 490–499, 2010.",
    "[10] Reserve Bank of India, \"Master Directions on Know Your Customer (KYC),\" RBI/2015-16/42, 2023. [Online]. Available: https://www.rbi.org.in",
]
for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent    = Cm(0.8)
    p.paragraph_format.first_line_indent = Cm(-0.8)
    p.paragraph_format.space_after   = Pt(4)
    run = p.add_run(ref)
    run.font.size = Pt(10)

page_break()

# ══════════════════════════════════════════════════════════════════════════════
# APPENDIX
# ══════════════════════════════════════════════════════════════════════════════
heading1("Appendix: Key Code Snippets")

heading2("A.1 Dynamic Threshold Calculation")
body(
    "The following function computes a personalized fraud threshold for each applicant "
    "before running the ensemble model (from ml/predictor.py):"
)
code_block(
    "def calculate_dynamic_threshold(form_data: dict) -> float:\n"
    "    BASE_FRAUD_THRESHOLD = 0.40\n"
    "    threshold = BASE_FRAUD_THRESHOLD\n"
    "\n"
    "    cibil    = int(float(form_data.get('cibil', 600)))\n"
    "    dti      = float(form_data.get('dti', 0.4))\n"
    "    emis     = float(form_data.get('emis', 0))\n"
    "    income   = float(form_data.get('income', 1))\n"
    "    emi_burden = emis / income if income > 0 else 0\n"
    "\n"
    "    if cibil < 500:    threshold -= 0.10  # Very poor credit → stricter\n"
    "    elif cibil > 750:  threshold += 0.10  # Excellent credit → lenient\n"
    "    if dti > 0.6:      threshold -= 0.05  # High debt burden → stricter\n"
    "    if emi_burden > 0.5: threshold -= 0.05  # EMI overload → stricter\n"
    "\n"
    "    return max(0.20, min(0.60, threshold))  # Clamp: 20% to 60%"
)

heading2("A.2 Agent Pipeline Call Sequence")
body(
    "The orchestrator's run_pipeline() method coordinates all three agents "
    "(from agents/orchestrator.py):"
)
code_block(
    "def run_pipeline(self, form_data: dict) -> AgenticReport:\n"
    "    # Stage 1: ML Detection\n"
    "    detection = self.detection_agent.score_application(form_data)\n"
    "\n"
    "    # Stage 2: Feature Risk Analytics\n"
    "    analytics = self.analytics_agent.analyze(form_data, detection.prediction)\n"
    "\n"
    "    # Stage 3: Advisory & Compliance\n"
    "    advisory = self.advisory_agent.advise(form_data, detection, analytics)\n"
    "\n"
    "    # Compile final agentic report\n"
    "    executive = (\n"
    "        f\"{advisory.decision} — {detection.prediction.label} at \"\n"
    "        f\"{detection.prediction.probability_display} fraud probability. \"\n"
    "        f\"Feature risk: {analytics.risk_level} ({analytics.risk_score}/100).\"\n"
    "    )\n"
    "    return AgenticReport(\n"
    "        platform=self.PLATFORM_NAME,\n"
    "        timestamp=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),\n"
    "        detection=detection, analytics=analytics, advisory=advisory,\n"
    "        executive_summary=executive\n"
    "    )"
)

heading2("A.3 Analytics Agent Risk Scoring (Core Logic)")
code_block(
    "# CIBIL Score checks\n"
    "if cibil < 550:  score += 25  # High severity\n"
    "elif cibil < 650: score += 12  # Medium severity\n"
    "\n"
    "# Debt-to-Income Ratio checks\n"
    "if dti > 0.65:  score += 22   # High severity\n"
    "elif dti > 0.5: score += 10   # Medium severity\n"
    "\n"
    "# Loan-to-Annual-Income check\n"
    "loan_to_income = loan_amount / max(income * 12, 1)\n"
    "if loan_to_income > 8: score += 18  # High severity\n"
    "\n"
    "# EMI Burden check\n"
    "if emis > income * 0.5: score += 15  # High severity\n"
    "\n"
    "# Employment Status check\n"
    "if employment in ('Unemployed', 'Student'): score += 20  # High severity\n"
    "\n"
    "# Model probability boost (ties ML output to risk score)\n"
    "score = min(100, score + int(prediction.probability * 40))"
)

# ─── Footer ────────────────────────────────────────────────────────────────────
add_footer()

# ─── Save ──────────────────────────────────────────────────────────────────────
output_path = "RiskSense_AI_Project_Report_with_Screenshots.docx"
doc.save(output_path)
print(f"[SUCCESS] Report saved: {output_path}")
