# Limitations

1. **Static Analysis Only**: This tool performs static analysis on code and configuration. It does not understand runtime behavior.
2. **Signal vs Verdict**: A match is a "signal" for review, not a final legal verdict. 
3. **Context Dependency**: AI Act risk classification heavily depends on the intended purpose and deployment context, which may not be fully represented in the code.
4. **False Positives/Negatives**: The tool uses heuristics and may flag benign code or miss obscured high-risk logic.
5. **Secret Exposure**: While efforts are made to redact obvious secrets (API keys, tokens), snippets included in the report may contain sensitive proprietary logic. Always review generated reports before sharing them.
