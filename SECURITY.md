# Security Policy

## Reporting a vulnerability

Please **do not** open public GitHub issues for security vulnerabilities.

Send a private report to **security@…** with:

- A description of the issue.
- Steps to reproduce or a proof-of-concept.
- The version of the scanner affected.
- Your name and affiliation (optional, for credit).

We will acknowledge receipt within 3 business days and aim to issue a fix within 30 days for high-severity issues.

## Scope

In scope:

- Code execution, file disclosure, or path traversal in the scanner itself.
- Secret leakage through reports (the scanner is supposed to redact common secret patterns; bypasses are vulnerabilities).
- Denial-of-service through pathological input files.

Out of scope:

- False positives or false negatives in rules (open a normal issue).
- Misinterpretation of legal categories (open a normal issue).
- Vulnerabilities in third-party tools that consume the JSON output.

## Supported versions

We provide security patches for the latest minor release and the previous one.
