# TRACE™ AI Act Compliance Auditor

This is the open-source **TRACE™ AI Act Compliance Auditor**. 

It uses zero-trust Abstract Syntax Tree (AST) parsing to statically analyze your codebase and extract structural topology that may violate the **EU AI Act**.

## What does it do?

Instead of reading documentation or asking LLMs what your code does, this tool reads the raw structure of your software. It maps variables, function calls, and dependencies against heuristics derived directly from the EU AI Act (e.g., Article 5 prohibited practices, Annex III high-risk systems).

## Features

- **AST-Based Extraction:** Zero execution. Parses code mathematically.
- **EU AI Act Vectors:** Maps 15 specific legal vectors to code heuristics.
- **Prohibited Practices Detection:** Flags biometric emotion recognition, predictive policing, and social scoring.
- **High-Risk Detection:** Flags automated workplace rejection and biometric categorization.

## Usage

```bash
python trace_ai_act_extractor.py <path_to_codebase>
```

To output as JSON for further processing or CI/CD integration:
```bash
python trace_ai_act_extractor.py <path_to_codebase> --json
```
