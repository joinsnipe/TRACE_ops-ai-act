<div align="center">
  <img src="../trace_logo.png" width="120" alt="TRACE Logo">
  <h1>TRACE™ AI Act Risk Scanner</h1>
  <p><b>Open-source technical scanner for early EU AI Act and GDPR risk signals.</b></p>
  <p><i>A first-pass technical triage layer to analyze your architecture without exposing source code.</i></p>
</div>

---

> **Disclaimer**: This tool does not provide legal advice and does not certify compliance with Regulation (EU) 2024/1689, GDPR or any other legal framework. It identifies technical risk signals that may require legal, technical and operational review. Final classification depends on intended purpose, deployment context, affected persons, operator role, data processing, safeguards and applicable national/EU law. Generated reports may contain filenames, symbols or code snippets. Review and redact reports before sharing them externally.

---

## 🏛️ What is this?

TRACE AI Act Risk Scanner analyzes source code and lightweight configuration files to detect technical signals that may require review under **Regulation (EU) 2024/1689 (the EU Artificial Intelligence Act)** and the **GDPR**.

It is designed strictly as an **early-warning technical triage layer**, not as a legal opinion.

## 🛡️ The Zero-Trust Guarantee

In regulatory audits, handing over your proprietary source code is a massive security risk. 
That's why **we don't need it.**

This script runs **LOCALLY** on your servers. It uses Abstract Syntax Tree (AST) parsing to detect structural patterns (like `detect_mood`, `score_candidate_auto`, or `personal_data`) and generates a clean technical report.

- ✅ **LOCAL**: runs on your machine or CI environment.
- ✅ **NO NETWORK**: does not send source code to external services.
- ✅ **REDACTED OUTPUT**: designed to avoid exposing secrets in reports.
- ⚠️ **REVIEW REPORTS**: generated reports may contain filenames, symbols or snippets; review before sharing externally.

## ⚖️ What it detects

The scanner looks for early signals related to:

**Potential Article 5 Prohibited Practices (ARTICLE_5_REVIEW_REQUIRED):**
- Remote Biometric Identification (RBI)
- Biometric Emotion Recognition
- Biometric Categorization (Race, Political, Sexual Orientation)
- Predictive Policing
- Social Scoring
- Subliminal Manipulation

**Potential High-Risk Systems (HIGH_RISK_REVIEW):**
- Critical Infrastructure (Digital and Physical)
- Education Admission and Proctoring
- Workplace Management and Automated Rejection
- Credit Scoring
- Democratic Processes

**Transparency & Data Protection (TRANSPARENCY_REVIEW & DATA_PROTECTION_REVIEW):**
- Synthetic Media / Deepfakes without watermarking
- GDPR: Processing of Personal Data, Profiling, Automated Decision-Making

## ⚠️ Disclaimer

This tool does **not** provide legal advice and does **not** certify compliance with Regulation (EU) 2024/1689, GDPR, or any other legal framework.

It identifies technical risk signals that may require legal, technical, and operational review. Final classification depends on intended purpose, deployment context, affected persons, operator role, data processing, safeguards, and applicable national/EU law.

## 🔬 Scientific Foundation & Methodology

This open-source scanner builds on the public research baseline introduced in:

**Structural Asymmetries in the EU AI Act: A Computational Forensic Analysis of Legislative Architecture**  
Zenodo: https://zenodo.org/records/20284633

The paper analyzes the EU AI Act as a structured regulatory architecture, including cross-reference topology, regulatory density, obligation-rights asymmetry and enforcement concentration.

This scanner does not implement the proprietary TRACE Structural Audit Engine.  
It provides a lightweight technical triage layer for early signal detection in software systems.

## ⚙️ How to use it

1. **Clone the repository:**
   ```bash
   git clone https://github.com/joinsnipe/TRACE_ops-ai-act.git
   cd TRACE_ops-ai-act
   ```

2. **Run it against your project folder** (requires Python 3.8+):
   ```bash
   python trace_ai_act_risk_scanner.py /path/to/your/codebase
   ```

3. **Export the Triage Report:**
   ```bash
   python trace_ai_act_risk_scanner.py /path/to/your/codebase --json > ai_act_report.json
   ```

4. **Analyze the Results:**
   Integrate `ai_act_report.json` into your CI/CD pipeline or pass it to your legal/compliance team to evaluate the structural risks detected before releasing your product.

---
*Maintained by TRACE™ - Forensic Intelligence & Structural Diagnostics.*
