# Methodology

This open-source scanner builds on the public research baseline introduced in:

**Structural Asymmetries in the EU AI Act: A Computational Forensic Analysis of Legislative Architecture**  
Zenodo: https://zenodo.org/records/20284633

The paper analyzes the EU AI Act as a structured regulatory architecture, including cross-reference topology, regulatory density, obligation-rights asymmetry and enforcement concentration.

This scanner does not implement the proprietary TRACE Structural Audit Engine.
It provides a lightweight technical triage layer for early signal detection in software systems.

## Heuristic Scanning
The tool analyzes Abstract Syntax Trees (AST) and string tokens to identify structural matches for Article 5 (Prohibited AI), Annex III (High-Risk AI), and GDPR complementary requirements (profiling, personal data processing). It also identifies the presence or absence of required governance controls.
