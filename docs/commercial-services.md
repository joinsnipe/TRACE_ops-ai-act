# Commercial services — SPE Audit Reporting

This document describes the **commercial counterpart** to the open-source scanner. It is published here so the relationship is transparent.

## The problem the open-source scanner does not solve

The scanner detects **technical signals** in code. It does not tell you whether what your company **says publicly** about its AI matches what your code actually does.

That gap is real. A company may publish:

> "We do not use biometric data. All hiring decisions are made by humans."

…while the codebase contains `face_recognition`, `cv_score`, `auto_reject` and `candidate_ranking`. The scanner will flag those signals. It will not tell you that they contradict the public claim. That requires **qualified human analysis**.

## What SPE Audit Reporting does

It is a service, not a product. Your team runs the open-source scanner locally and sends us:

1. The JSON report (validated against `schema/trace-report-v1.json`).
2. Optionally, a `self_declaration` block listing your public claims and URLs.

Our analysts then:

- Crawl your public materials (website, AI policy, marketing, press, support docs).
- Extract verifiable public claims.
- Cross-check each claim against the detected signals and detected governance controls.
- Produce an **alignment dictum**: where narrative matches reality, where it does not, and what the regulatory exposure looks like under the EU AI Act and GDPR.
- Deliver an **evidence pack** suitable for an external auditor, regulator or investor.

We never need access to your source code. The scanner runs in your environment.

## When it is useful

- Before a product launch or major release.
- Before investor due diligence.
- Before engaging with a regulator.
- As continuous monitoring as the codebase evolves.

## Pricing and contact

Contact: **contact@…**

The open-source scanner is and will remain fully functional on its own under Apache-2.0. The commercial service adds qualified human analysis and the proprietary alignment engine — it is **not** gated behind missing scanner features.
