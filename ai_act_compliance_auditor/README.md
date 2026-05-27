<div align="center">
  <img src="../trace_logo.png" width="120" alt="TRACE Logo">
  <h1>TRACE™ AI Act Compliance Auditor</h1>
  <p><b>Zero-Trust codebase inspection for EU AI Act regulatory compliance.</b></p>
  <p><i>Audit your technical architecture against European law without exposing your source code.</i></p>
</div>

---

## 🏛️ What is this?

The **EU Artificial Intelligence Act** imposes severe restrictions and bans on specific AI practices (e.g., biometric categorization, predictive policing, subliminal manipulation). Fines for non-compliance can reach up to **7% of global annual turnover**.

Most legal audits rely on documentation and interviews. **TRACE™ AI Act Compliance Auditor** relies on mathematics. 

This open-source extraction script uses Abstract Syntax Tree (AST) parsing to statically analyze your codebase. It mathematically maps variables, function calls, and structural dependencies against **15 specific legal vectors** derived directly from the EU AI Act (Article 5 prohibited practices and Annex III high-risk systems).

## 🛡️ The Zero-Trust Guarantee: "We don't want your code"

In regulatory audits, handing over your proprietary source code to consultants or lawyers is a massive security risk. 
That's why **we don't need it.**

This script is designed to run **LOCALLY** on your isolated servers. It parses your code mathematically to detect structural patterns (like `detect_mood`, `score_candidate_auto`, or `predictive_policing_score`) and generates a clean JSON report.

- ✅ **EXTRACT**: AST-based pattern matching for the 15 critical vectors of the AI Act.
- ✅ **DETECT**: Prohibited Practices (Critical Risk) and High-Risk Systems.
- ❌ **IGNORE**: Business logic, passwords, API keys, and database schemas.
- ❌ **OFFLINE**: The script does not make any network requests. It saves a `.json` file locally.

## ⚖️ The 15 Vectors Audited

The script scans for structural evidence of the following regulatory categories:

**Prohibited Practices (Article 5) - CRITICAL RISK:**
1. Real-time Remote Biometric Identification (RBI)
2. Biometric Emotion Recognition in Workplace/Education
3. Biometric Categorization (Race, Political, Sexual Orientation)
4. Predictive Policing and Criminal Profiling
5. Social Scoring and Citizen Trust
6. Subliminal Manipulation and Dark Patterns

**High-Risk Systems (Annex III) - HIGH RISK:**
7. Critical Digital Infrastructure (SCADA, DNS routing)
8. Critical Physical Infrastructure (Water, Gas, Electricity)
9. Educational Admission and Learning Scoring
10. Educational Proctoring and Monitoring
11. Workplace Automated Rejection (CV Filtering)
12. Workplace Management and Task Allocation
13. Credit Scoring and Loan Approval
14. Democratic Process and Election Influence

**Transparency Risk (Article 50):**
15. Generative AI Synthetic Media (Deepfakes) without Watermarking

## ⚙️ How to use it

1. **Navigate to this directory:**
   ```bash
   cd ai_act_compliance_auditor
   ```

2. **Run it against your project folder** (requires Python 3.8+):
   ```bash
   python trace_ai_act_extractor.py /path/to/your/codebase
   ```

3. **Export the Official JSON Report:**
   ```bash
   python trace_ai_act_extractor.py /path/to/your/codebase --json > ai_act_report.json
   ```

4. **Analyze the Results:**
   Integrate `ai_act_report.json` into your CI/CD pipeline or pass it to your compliance team to evaluate the structural risks detected.

---
*Maintained by TRACE™ - Forensic Intelligence & Structural Diagnostics.*
