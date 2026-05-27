<div align="center">
  <img src="./trace_logo.png" width="120" alt="TRACE Logo">
  <h1>TRACE™ Structural Extractor</h1>
  <p><b>We mathematically align your corporate communication with your structural codebase architecture.</b></p>
  <p><i>Zero-Trust Codebase Topology Extractor for Enterprise Audits</i></p>
</div>

---

## 🏗️ What is this?

Every tech company has two bodies: the **narrative** (the pitch deck, the website) and the **technical architecture** (the codebase, the actual product). Most consultancies audit one or the other. Never both. Never with the same mathematics.

**TRACE™ Structural Audits do both.**

This tool is the official open-source extraction script for TRACE™ Codebase Auditing. We convert your codebase into a mathematical graph (nodes + relationships) and apply network topology to answer three critical questions:

1. **What does everything depend on?** → *God Nodes* (central points of failure).
2. **What parts are isolated?** → *Community Fractures* (zombie code, disconnected modules).
3. **Is it coherent or a collection of loose pieces?** → *Cohesion Score* (0 to 1).

We don't do bug reviews. We don't judge code style. We map structural architecture.

## 🛡️ The Zero-Trust Guarantee: "We don't want your code"

In due diligence processes, handing over your proprietary source code is a massive friction point. 
That's why **we don't need it.**

This open-source script is designed to run LOCALLY on your machine. You can read `trace_extractor.py` (it is less than 150 lines). It uses Abstract Syntax Tree (AST) parsing and regex heuristics to:

- ✅ **EXTRACT**: Class names, Function names, Function call connections, Cyclomatic Complexity metrics, and LOC.
- ✅ **SUPPORT**: Python (`.py`), JavaScript (`.js`, `.jsx`), and TypeScript (`.ts`, `.tsx`).
- ❌ **IGNORE**: Variables, hardcoded strings, business logic, passwords, API keys, and database schemas.
- ❌ **OFFLINE**: The script does not make any network requests. It saves a `.json` file locally.

It’s like giving a blood test to a laboratory: we see the metrics, we never see the patient.

---

## 🛑 Addressing the "Linter" Objection

You might ask: *"Isn't this just a very basic AST parser? SonarQube does this."*

Yes, this extractor is intentionally simple. It is **not** a linter. Linters are excellent for finding bad code, bugs, and style violations. 

**TRACE is designed to audit architecture, not code syntax.** 

The value of the TRACE audit is not in this extraction script. This script is simply a secure data collector. The actual analysis happens during the TRACE diagnostic process, where we take this structural JSON and map it against your organizational narrative and documentation. 

We look for structural bottlenecks:
1. **God Nodes:** Classes or functions that have become too central, creating maintenance risks.
2. **Community Fractures:** Isolated code clusters that indicate silos in your development team or unused legacy systems.

This open-source tool exists exclusively to guarantee IP security, allowing us to audit your structural topology without ever asking for access to your proprietary source code.

## 🎯 Who is this for?

- **Venture Capital (VC):** Technical Due Diligence in 48h before investing, without NDAs holding up access to code.
- **CTOs:** Get a map of technical debt on day 1 of inheriting a new codebase.
- **M&A (Mergers & Acquisitions):** Are the two codebases structurally compatible, or are you buying an unmaintainable bifurcation?
- **Founders:** Does your narrative and your product architecture tell the same story?

---

## 🛣️ Technical Roadmap
Currently, `trace_extractor.py` relies on the standard `ast` library for Python and regex heuristics for JS/TS. 
In future iterations, we will migrate to **Tree-sitter** to provide robust, language-agnostic AST parsing for Go, Rust, Java, and C++.

---

## ⚙️ How to use it

1. **Download the script directly:**
   ```bash
   curl -O https://raw.githubusercontent.com/joinsnipe/SPE_TRACE./main/trace_extractor.py
   ```

2. **Run it against your project folder** (requires Python 3.8+):
   ```bash
   python trace_extractor.py /path/to/your/project
   ```

3. **Verify the output (Optional but encouraged):**
   The script generates a file called `trace_topology_export.json`. Open it with any text editor to verify that absolutely no sensitive code or logic was captured.

4. **Send it to TRACE:**
   Send the `trace_topology_export.json` file to your TRACE Structural Auditor to generate your architectural health report.

---
*Maintained by TRACE™ - Forensic Intelligence & Structural Diagnostics.*
