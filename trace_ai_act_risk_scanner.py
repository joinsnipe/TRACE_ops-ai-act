#!/usr/bin/env python3
"""
TRACE AI Act Risk Scanner
===========================
Static red-flag scanner for EU AI Act + GDPR risk triage.

What it does:
- Scans source code and lightweight documentation files for technical signals.
- Classifies signals as Article 5, Annex III high-risk, Article 50 transparency, GDPR/data-protection, or governance-readiness.
- Produces an enterprise-readiness view: blockers, potential high-risk areas, transparency gaps, GDPR overlaps, evidence coverage.

What it does NOT do:
- It does not determine legal compliance.
- It does not replace legal review, DPIA, FRIA, conformity assessment, or technical documentation.
- It does not infer intended purpose with certainty from code alone.

Design principles:
- Signal, not verdict.
- Context-aware, not keyword-only.
- Exact-token matching to avoid false positives such as 'Trace' matching 'race'.
- Separate risk triggers from governance controls.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import hashlib
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", ".yml", ".toml", ".md", ".txt", ".html", ".css"
}

DEFAULT_EXCLUDES = {
    ".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__", ".mypy_cache", ".pytest_cache"
}

TOKEN_SPLIT_RE = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]*")


@dataclass(frozen=True)
class Rule:
    id: str
    bucket: str
    legal_basis: str
    label: str
    severity: str
    weight: int
    exact_terms: Tuple[str, ...] = ()
    phrases: Tuple[str, ...] = ()
    regexes: Tuple[str, ...] = ()
    context_terms: Tuple[str, ...] = ()
    required_context: Tuple[str, ...] = ()
    negative_terms: Tuple[str, ...] = ()
    guidance: str = ""


@dataclass
class Signal:
    rule_id: str
    bucket: str
    legal_basis: str
    label: str
    severity: str
    weight: int
    file: str
    line: int
    symbol: str
    matched: str
    evidence: str
    confidence: float
    node_type: str = "text"
    guidance: str = ""


@dataclass
class ScanSummary:
    target: str
    files_scanned: int
    signals_total: int
    risk_score: int
    readiness_score: int
    viability: str
    blockers: int
    potential_high_risk: int
    transparency_risks: int
    gdpr_overlaps: int
    governance_controls_detected: int
    missing_governance_controls: List[str]
    notes: List[str] = field(default_factory=list)


@dataclass
class ScanReport:
    summary: ScanSummary
    signals: List[Signal]
    controls: Dict[str, List[Dict[str, Any]]]
    config: Dict[str, Any]
    disclaimer: str


# ---------------------------------------------------------------------------
# Rule set
# ---------------------------------------------------------------------------

RISK_RULES: List[Rule] = [
    Rule(
        id="A5_MANIPULATION_SUBLIMINAL_EXPLOITATIVE",
        bucket="article_5_prohibited_practice_signal",
        legal_basis="EU AI Act Article 5",
        label="Potential manipulative, subliminal or exploitative practice",
        severity="ARTICLE_5_REVIEW_REQUIRED",
        weight=35,
        exact_terms=("subliminal", "manipulate", "manipulation", "exploit", "exploitative", "vulnerability"),
        phrases=("dark pattern", "cognitive distortion", "materially distort", "behaviour manipulation", "behavior manipulation"),
        context_terms=("user", "person", "child", "consumer", "decision", "choice", "behaviour", "behavior"),
        guidance="Check whether the system materially distorts behaviour or exploits vulnerability. If yes, legal review is mandatory before deployment.",
    ),
    Rule(
        id="A5_SOCIAL_SCORING",
        bucket="article_5_prohibited_practice_signal",
        legal_basis="EU AI Act Article 5",
        label="Potential social scoring of natural persons",
        severity="ARTICLE_5_REVIEW_REQUIRED",
        weight=40,
        exact_terms=("social_score", "socialscore", "citizen_score", "citizen_trust", "trust_score", "reputation_score"),
        phrases=("social credit", "citizen trust", "behaviour score", "behavior score"),
        context_terms=("person", "citizen", "individual", "natural_person", "public_service", "eligibility"),
        guidance="Confirm whether individuals are evaluated over time using social behaviour or personal characteristics with detrimental treatment.",
    ),
    Rule(
        id="A5_BIOMETRIC_CATEGORISATION_SENSITIVE",
        bucket="article_5_prohibited_practice_signal",
        legal_basis="EU AI Act Article 5 + GDPR special categories",
        label="Potential biometric categorisation to infer sensitive attributes",
        severity="ARTICLE_5_REVIEW_REQUIRED",
        weight=40,
        exact_terms=("race", "ethnicity", "religion", "political", "sexual_orientation", "trade_union"),
        phrases=("biometric categorisation", "biometric categorization", "infer race", "infer ethnicity", "political opinion", "trade union", "sexual orientation"),
        context_terms=("classify", "categorize", "categorise", "infer", "deduce", "attribute", "sensitive"),
        required_context=("biometric", "face", "fingerprint", "iris", "gait", "voiceprint", "facial"),
        negative_terms=("hair_colour", "hair_color", "eye_colour", "eye_color", "product_filter", "avatar_filter"),
        guidance="Check if biometric data is used to infer protected or sensitive attributes. Requires biometric + sensitive context.",
    ),
    Rule(
        id="A5_REAL_TIME_REMOTE_BIOMETRIC_ID",
        bucket="article_5_prohibited_practice_signal",
        legal_basis="EU AI Act Article 5",
        label="Potential real-time remote biometric identification in public spaces",
        severity="ARTICLE_5_REVIEW_REQUIRED",
        weight=45,
        exact_terms=("face_recognition", "facial_recognition", "remote_biometric", "biometric_id", "cctv", "live_camera", "surveillance"),
        phrases=("real time biometric", "real-time biometric", "remote biometric identification", "public space", "publicly accessible"),
        context_terms=("live", "real_time", "realtime", "identify", "camera", "crowd", "law_enforcement", "public"),
        guidance="This is one of the highest-risk blockers. Determine law-enforcement purpose, public-space context, real-time nature and exceptions.",
    ),
    Rule(
        id="A5_PREDICTIVE_POLICING_INDIVIDUAL",
        bucket="article_5_prohibited_practice_signal",
        legal_basis="EU AI Act Article 5",
        label="Potential individual predictive policing / criminal risk assessment",
        severity="ARTICLE_5_REVIEW_REQUIRED",
        weight=40,
        exact_terms=("predict_crime", "crime_prediction", "recidivism", "offender_score", "criminal_risk", "offense_probability", "offence_probability"),
        phrases=("predictive policing", "risk of committing", "criminal offence", "criminal offense"),
        context_terms=("individual", "person", "natural_person", "law_enforcement", "police", "profile", "risk_score"),
        guidance="Differentiate individual prediction from area-level resource allocation or evidence-based investigative support.",
    ),
    Rule(
        id="A5_EMOTION_RECOGNITION_WORK_EDU",
        bucket="article_5_prohibited_practice_signal",
        legal_basis="EU AI Act Article 5 / Annex III where not prohibited",
        label="Potential emotion recognition in workplace or education",
        severity="ARTICLE_5_REVIEW_REQUIRED",
        weight=35,
        exact_terms=("emotion", "mood", "affect", "stress", "sentiment_facial", "deepface", "fer", "voice_stress"),
        phrases=("emotion recognition", "infer emotion", "detect mood", "facial sentiment", "voice stress"),
        context_terms=("employee", "worker", "candidate", "student", "school", "exam", "classroom", "workplace", "education"),
        guidance="If used in workplace or education to infer emotions, treat as blocker. If used for safety/fatigue exceptions, document narrowly.",
    ),
    Rule(
        id="AIII_BIOMETRICS_HIGH_RISK",
        bucket="annex_iii_high_risk_signal",
        legal_basis="EU AI Act Annex III(1)",
        label="Potential high-risk biometric system",
        severity="HIGH_RISK_REVIEW",
        weight=28,
        exact_terms=("biometric", "facial_recognition", "face_recognition", "voiceprint", "gait", "iris", "fingerprint", "emotion_recognition"),
        phrases=("remote biometric", "biometric verification", "biometric categorisation", "biometric categorization"),
        context_terms=("identify", "verify", "authenticate", "classify", "categorize", "recognize"),
        guidance="Biometric verification may be excluded from some high-risk categories if used only for authentication; document purpose.",
    ),
    Rule(
        id="AIII_CRITICAL_INFRASTRUCTURE",
        bucket="annex_iii_high_risk_signal",
        legal_basis="EU AI Act Annex III(2)",
        label="Potential AI safety component in critical infrastructure",
        severity="HIGH_RISK_REVIEW",
        weight=30,
        exact_terms=("scada", "smart_grid", "traffic_control", "electricity_grid", "gas_control", "water_supply", "heating_network", "dns_routing_ai"),
        phrases=("critical infrastructure", "road traffic", "water supply", "electricity grid", "gas supply"),
        context_terms=("safety", "operation", "control", "dispatch", "routing", "grid", "infrastructure"),
        guidance="Determine whether the AI system is a safety component or used in operation/management of critical infrastructure.",
    ),
    Rule(
        id="AIII_EDUCATION_VOCATIONAL",
        bucket="annex_iii_high_risk_signal",
        legal_basis="EU AI Act Annex III(3)",
        label="Potential high-risk education/vocational training system",
        severity="HIGH_RISK_REVIEW",
        weight=26,
        exact_terms=("admission_score", "student_score", "predict_grades", "student_risk", "proctor", "cheat_detection", "exam_monitor"),
        phrases=("student admission", "education access", "vocational training", "exam proctoring", "learning assessment"),
        context_terms=("student", "school", "university", "exam", "teacher", "admission", "education"),
        guidance="Check if the system determines access, admission, assignment, assessment, monitoring or detection of prohibited behaviour.",
    ),
    Rule(
        id="AIII_EMPLOYMENT_WORKER_MANAGEMENT",
        bucket="annex_iii_high_risk_signal",
        legal_basis="EU AI Act Annex III(4)",
        label="Potential high-risk employment, recruitment or worker-management system",
        severity="HIGH_RISK_REVIEW",
        weight=32,
        exact_terms=("auto_reject", "cv_score", "resume_score", "candidate_score", "rank_candidate", "shift_allocation", "worker_monitoring", "performance_score"),
        phrases=("filter cv", "resume parser", "candidate ranking", "employee monitoring", "worker performance", "task allocation"),
        context_terms=("candidate", "employee", "worker", "job", "recruitment", "hiring", "promotion", "termination"),
        guidance="Employment AI is a core high-risk area. Check whether output materially affects hiring, allocation, monitoring or termination.",
    ),
    Rule(
        id="AIII_CREDITWORTHINESS_INSURANCE",
        bucket="annex_iii_high_risk_signal",
        legal_basis="EU AI Act Annex III(5)",
        label="Potential high-risk creditworthiness or essential service access system",
        severity="HIGH_RISK_REVIEW",
        weight=30,
        exact_terms=("credit_score", "creditworthiness", "loan_approval", "risk_premium", "insurance_score", "eligibility_score"),
        phrases=("credit scoring", "loan approval", "insurance pricing", "essential service", "access to service"),
        context_terms=("consumer", "natural_person", "individual", "eligibility", "deny", "approve", "price"),
        guidance="Assess whether the system evaluates natural persons for credit or essential private/public services.",
    ),
    Rule(
        id="AIII_LAW_ENFORCEMENT_MIGRATION_JUSTICE",
        bucket="annex_iii_high_risk_signal",
        legal_basis="EU AI Act Annex III(6-8)",
        label="Potential high-risk law enforcement, migration, asylum, border control or justice system",
        severity="HIGH_RISK_REVIEW",
        weight=32,
        exact_terms=("law_enforcement", "asylum", "border_control", "migration_risk", "case_outcome", "evidence_assessment", "judge_assistant"),
        phrases=("law enforcement", "border control", "asylum decision", "judicial decision", "evidence reliability", "risk assessment"),
        context_terms=("police", "court", "judge", "prosecutor", "migrant", "asylum", "border", "evidence"),
        guidance="Separate administrative triage from decisions affecting rights; these domains require close legal and fundamental-rights review.",
    ),
    Rule(
        id="AIII_DEMOCRATIC_PROCESS",
        bucket="annex_iii_high_risk_signal",
        legal_basis="EU AI Act Annex III(8)",
        label="Potential AI system influencing elections or democratic processes",
        severity="HIGH_RISK_REVIEW",
        weight=30,
        exact_terms=("voter_score", "voter_influence", "election_score", "campaign_ai", "political_targeting"),
        phrases=("voter influence", "election influence", "political targeting", "referendum outcome"),
        context_terms=("voter", "election", "referendum", "campaign", "political", "democratic"),
        guidance="Political targeting and democratic influence require intended-purpose review and transparency controls.",
    ),
    Rule(
        id="A50_SYNTHETIC_CONTENT_DISCLOSURE",
        bucket="article_50_transparency_signal",
        legal_basis="EU AI Act Article 50",
        label="Potential synthetic content / deepfake transparency obligation",
        severity="TRANSPARENCY_REVIEW",
        weight=22,
        exact_terms=("deepfake", "synthetic_media", "generate_image", "generate_audio", "generate_video", "text_to_image", "voice_clone", "tts"),
        phrases=("synthetic content", "machine readable", "ai generated", "content provenance", "watermark missing", "generated media"),
        context_terms=("publish", "export", "upload", "display", "user", "public", "media", "watermark", "label", "metadata"),
        guidance="Do not only detect generation. Check output path and whether disclosure/watermark/provenance is implemented.",
    ),
    Rule(
        id="GDPR_PERSONAL_DATA_PROCESSING",
        bucket="gdpr_data_protection_overlap",
        legal_basis="GDPR + EU AI Act complementarity",
        label="Potential personal data processing / profiling overlap",
        severity="DATA_PROTECTION_REVIEW",
        weight=18,
        exact_terms=("personal_data", "pii", "profile", "profiling", "user_id", "email", "phone", "location", "biometric", "health", "criminal", "sensitive"),
        phrases=("personal data", "data subject", "special category", "automated decision", "solely automated", "data minimisation", "data minimization"),
        context_terms=("collect", "process", "store", "infer", "predict", "identify", "consent", "legitimate_interest"),
        guidance="If personal data is processed, GDPR controls must sit beside AI Act controls: lawful basis, minimisation, transparency, rights, security.",
    ),
]

CONTROL_RULES: List[Rule] = [
    Rule("CTRL_RISK_MANAGEMENT", "governance_control", "EU AI Act Article 9", "Risk management system", "CONTROL", -8, exact_terms=("risk_management", "risk_register", "risk_assessment"), phrases=("risk management", "risk register")),
    Rule("CTRL_DATA_GOVERNANCE", "governance_control", "EU AI Act Article 10 + GDPR", "Data governance / data quality", "CONTROL", -8, exact_terms=("data_governance", "data_quality", "bias_audit", "dataset_card"), phrases=("data governance", "data quality", "bias audit", "dataset card")),
    Rule("CTRL_TECHNICAL_DOCUMENTATION", "governance_control", "EU AI Act Article 11", "Technical documentation", "CONTROL", -8, exact_terms=("technical_documentation", "model_card", "system_card", "conformity"), phrases=("technical documentation", "model card", "system card", "conformity assessment")),
    Rule("CTRL_LOGGING_RECORDKEEPING", "governance_control", "EU AI Act Article 12", "Logging / record-keeping", "CONTROL", -8, exact_terms=("audit_log", "logging", "recordkeeping", "traceability"), phrases=("audit log", "record keeping", "record-keeping", "traceability")),
    Rule("CTRL_TRANSPARENCY_INSTRUCTIONS", "governance_control", "EU AI Act Article 13 + Article 50", "Transparency / instructions for use", "CONTROL", -8, exact_terms=("instructions_for_use", "disclosure", "watermark", "provenance", "c2pa"), phrases=("instructions for use", "user disclosure", "machine-readable", "content provenance")),
    Rule("CTRL_HUMAN_OVERSIGHT", "governance_control", "EU AI Act Article 14", "Human oversight / override", "CONTROL", -8, exact_terms=("human_review", "human_oversight", "override", "appeal", "stop_button"), phrases=("human oversight", "human review", "manual review", "stop button", "appeal process")),
    Rule("CTRL_ROBUSTNESS_CYBERSECURITY", "governance_control", "EU AI Act Article 15", "Accuracy, robustness and cybersecurity", "CONTROL", -8, exact_terms=("robustness", "cybersecurity", "adversarial", "data_poisoning", "model_poisoning", "fail_safe", "fallback"), phrases=("accuracy metrics", "adversarial testing", "data poisoning", "model poisoning", "fail safe")),
    Rule("CTRL_POST_MARKET_MONITORING", "governance_control", "EU AI Act provider obligations", "Post-market monitoring / incident handling", "CONTROL", -8, exact_terms=("post_market", "incident_report", "monitoring", "corrective_action"), phrases=("post-market monitoring", "serious incident", "corrective action")),
    Rule("CTRL_FRIA_DPIA", "governance_control", "EU AI Act fundamental rights + GDPR DPIA", "FRIA/DPIA evidence", "CONTROL", -8, exact_terms=("fria", "dpia", "impact_assessment", "fundamental_rights"), phrases=("fundamental rights impact assessment", "data protection impact assessment", "impact assessment")),
]

REQUIRED_CONTROLS_BY_BUCKET = {
    "article_5_prohibited_practice_signal": ["CTRL_RISK_MANAGEMENT", "CTRL_TECHNICAL_DOCUMENTATION", "CTRL_HUMAN_OVERSIGHT", "CTRL_FRIA_DPIA", "CTRL_LOGGING_RECORDKEEPING"],
    "annex_iii_high_risk_signal": ["CTRL_RISK_MANAGEMENT", "CTRL_DATA_GOVERNANCE", "CTRL_TECHNICAL_DOCUMENTATION", "CTRL_LOGGING_RECORDKEEPING", "CTRL_TRANSPARENCY_INSTRUCTIONS", "CTRL_HUMAN_OVERSIGHT", "CTRL_ROBUSTNESS_CYBERSECURITY", "CTRL_POST_MARKET_MONITORING", "CTRL_FRIA_DPIA"],
    "article_50_transparency_signal": ["CTRL_TRANSPARENCY_INSTRUCTIONS", "CTRL_LOGGING_RECORDKEEPING"],
    "gdpr_data_protection_overlap": ["CTRL_DATA_GOVERNANCE", "CTRL_FRIA_DPIA", "CTRL_TRANSPARENCY_INSTRUCTIONS", "CTRL_LOGGING_RECORDKEEPING"],
}


# ---------------------------------------------------------------------------
# Normalisation and matching
# ---------------------------------------------------------------------------

def split_identifier(value: str) -> List[str]:
    """Split identifiers into safe tokens: snake_case, kebab-case, camelCase.

    Prevents false positives such as 'TraceASTVisitor' matching the exact term 'race'.
    """
    if not value:
        return []
    pieces: List[str] = []
    for part in re.split(r"[^A-Za-z0-9]+", value):
        if not part:
            continue
        sub = TOKEN_SPLIT_RE.findall(part)
        pieces.extend(s.lower() for s in (sub or [part]))
    # Also keep normalized compound tokens for exact technical names like face_recognition.
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    if normalized:
        pieces.append(normalized)
    return pieces


def line_context(text: str, line_no: int, radius: int = 1) -> str:
    lines = text.splitlines()
    idx = max(line_no - 1, 0)
    start = max(idx - radius, 0)
    end = min(idx + radius + 1, len(lines))
    return "\n".join(lines[start:end]).strip()[:700]


def whole_word_phrase_match(phrase: str, haystack: str) -> bool:
    escaped = re.escape(phrase.lower())
    escaped = escaped.replace(r"\ ", r"[\s_\-]+")
    return bool(re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", haystack.lower()))




def is_negated_config_context(matched: str, haystack: str) -> bool:
    """Suppress weak config matches such as `uses_biometric_data: false`."""
    m = re.escape(matched.lower()).replace(r"\ ", r"[\s_\-]+")
    patterns = [
        rf"{m}[a-z0-9_\-]*[^\n]{{0,100}}[:=]\s*(false|none|null|0|disabled|off|no)\b",
        rf"(no|without|disable|disabled)\s+[^\n]{{0,40}}{m}",
    ]
    return any(re.search(pattern, haystack.lower()) for pattern in patterns)

def score_confidence(rule: Rule, text: str, symbol: str, matched: str) -> float:
    low = f"{symbol}\n{text}".lower()
    tokens = set(split_identifier(symbol) + split_identifier(text))

    confidence = 0.45
    if matched.lower() in tokens:
        confidence += 0.20
    if any(t.lower() in tokens or whole_word_phrase_match(t, low) for t in rule.context_terms):
        confidence += 0.20
    if any(t.lower() in tokens or whole_word_phrase_match(t, low) for t in rule.negative_terms):
        confidence -= 0.25
    if rule.bucket == "article_5_prohibited_practice_signal" and any(t in tokens for t in ("test", "mock", "example", "demo")):
        confidence -= 0.10
    return max(0.10, min(0.95, round(confidence, 2)))


def match_rule(rule: Rule, symbol: str, context: str) -> Optional[Tuple[str, float]]:
    tokens = set(split_identifier(symbol) + split_identifier(context))
    haystack = f"{symbol}\n{context}".lower()

    if rule.required_context:
        if not any(t.lower() in tokens or whole_word_phrase_match(t, haystack) for t in rule.required_context):
            return None

    # Negative context can suppress very weak exact matches, but not strong phrase matches.
    negative_hit = any(t.lower() in tokens or whole_word_phrase_match(t, haystack) for t in rule.negative_terms)

    for term in rule.exact_terms:
        term_norm = term.lower()
        term_tokens = split_identifier(term_norm)
        atomic_term_tokens = [t for t in term_tokens if t != term_norm]
        # Match either the preserved compound token (e.g. face_recognition) or
        # the atomic tokens in any order (e.g. score_candidate_auto -> candidate_score).
        if term_norm in tokens or (atomic_term_tokens and all(t in tokens for t in atomic_term_tokens)):
            if is_negated_config_context(term, haystack):
                return None
            conf = score_confidence(rule, context, symbol, term)
            if negative_hit and conf < 0.65:
                return None
            return term, conf

    for phrase in rule.phrases:
        if whole_word_phrase_match(phrase, haystack):
            if is_negated_config_context(phrase, haystack):
                return None
            conf = score_confidence(rule, context, symbol, phrase) + 0.05
            return phrase, min(0.95, round(conf, 2))

    for pattern in rule.regexes:
        if re.search(pattern, haystack, flags=re.IGNORECASE):
            conf = score_confidence(rule, context, symbol, pattern) + 0.05
            return pattern, min(0.95, round(conf, 2))

    return None


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------

class PythonASTExtractor(ast.NodeVisitor):
    def __init__(self, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.items: List[Tuple[str, int, str, str]] = []  # symbol, line, node_type, context

    def add(self, symbol: str, node: ast.AST, node_type: str) -> None:
        if symbol:
            line = getattr(node, "lineno", 1) or 1
            self.items.append((symbol, line, node_type, line_context(self.source, line)))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.add(node.name, node, "FunctionDef")
        for arg in node.args.args + node.args.kwonlyargs:
            self.add(arg.arg, arg, "Argument")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.add(node.name, node, "ClassDef")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Name):
            self.add(node.func.id, node, "Call")
        elif isinstance(node.func, ast.Attribute):
            self.add(node.func.attr, node, "CallAttribute")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> Any:
        self.add(node.id, node, "Name")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        self.add(node.attr, node, "Attribute")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            self.add(alias.name, node, "Import")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        if node.module:
            self.add(node.module, node, "ImportFrom")
        for alias in node.names:
            self.add(alias.name, node, "ImportFrom")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, str) and len(node.value) <= 500:
            self.add(node.value, node, "StringLiteral")
        self.generic_visit(node)


def extract_python_items(path: Path, source: str) -> List[Tuple[str, int, str, str]]:
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return extract_text_items(source)
    visitor = PythonASTExtractor(str(path), source)
    visitor.visit(tree)
    # Include text scan too, to catch comments/config-like strings.
    return visitor.items + extract_text_items(source)


def extract_text_items(source: str) -> List[Tuple[str, int, str, str]]:
    items: List[Tuple[str, int, str, str]] = []
    for i, line in enumerate(source.splitlines(), start=1):
        if not line.strip():
            continue
        # Scan whole line for phrases plus identifiers/words.
        items.append((line.strip()[:300], i, "Line", line.strip()[:700]))
        for word in WORD_RE.findall(line):
            if len(word) >= 3:
                items.append((word, i, "Word", line.strip()[:700]))
    return items


def iter_files(target: Path, excludes: Sequence[str]) -> Iterable[Path]:
    excludes_set = set(excludes) | DEFAULT_EXCLUDES
    if target.is_file():
        if target.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield target
        return
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in excludes_set and not d.startswith(".")]
        for filename in files:
            p = Path(root) / filename
            if p.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield p


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    data = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
            return yaml.safe_load(data) or {}
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("YAML config requires PyYAML or use JSON config") from exc
    return json.loads(data)


# ---------------------------------------------------------------------------
# Scanning and reporting
# ---------------------------------------------------------------------------

def file_hash(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8", errors="ignore")).hexdigest()[:16]


def redact_secrets(text: str) -> str:
    if not text:
        return text
    patterns = [
        r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]+['\"]",
        r"sk-[A-Za-z0-9_\-]{20,}",
        r"AKIA[0-9A-Z]{16}",
    ]
    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED_SECRET]", redacted)
    return redacted


def scan_file(path: Path, target_root: Path, rules: Sequence[Rule], no_snippets: bool = False) -> Tuple[List[Signal], Dict[str, List[Dict[str, Any]]]]:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return [], {}

    rel = str(path.relative_to(target_root)) if target_root.is_dir() else str(path)
    items = extract_python_items(path, source) if path.suffix.lower() == ".py" else extract_text_items(source)

    signals: List[Signal] = []
    controls: Dict[str, List[Dict[str, Any]]] = {}
    seen: set[Tuple[str, str, int, str]] = set()

    for symbol, line, node_type, context in items:
        for rule in rules:
            matched = match_rule(rule, symbol, context)
            if not matched:
                continue
            matched_text, conf = matched
            dedupe_key = (rule.id, rel, line, matched_text.lower())
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            evidence = line_context(source, line, radius=1) or context
            if no_snippets:
                evidence = f"[SNIPPET OMITTED: {file_hash(evidence)}]"
            else:
                evidence = redact_secrets(evidence)

            symbol_redacted = redact_secrets(symbol[:200])
            matched_redacted = redact_secrets(matched_text)

            if rule.bucket == "governance_control":
                controls.setdefault(rule.id, []).append({
                    "file": rel,
                    "line": line,
                    "matched": matched_redacted,
                    "node_type": node_type,
                    "evidence": evidence[:500] if not no_snippets else evidence,
                })
            else:
                signals.append(Signal(
                    rule_id=rule.id,
                    bucket=rule.bucket,
                    legal_basis=rule.legal_basis,
                    label=rule.label,
                    severity=rule.severity,
                    weight=rule.weight,
                    file=rel,
                    line=line,
                    symbol=symbol_redacted,
                    matched=matched_redacted,
                    evidence=evidence[:700] if not no_snippets else evidence,
                    confidence=conf,
                    node_type=node_type,
                    guidance=rule.guidance,
                ))
    return signals, controls


def aggregate_controls(control_hits: Dict[str, List[Dict[str, Any]]]) -> int:
    return len([cid for cid, hits in control_hits.items() if hits])


def needed_controls(signals: Sequence[Signal]) -> List[str]:
    required: set[str] = set()
    for sig in signals:
        required.update(REQUIRED_CONTROLS_BY_BUCKET.get(sig.bucket, []))
    return sorted(required)


def classify_viability(risk_score: int, blockers: int, high_risk: int, missing_controls: int) -> str:
    if blockers > 0 and risk_score >= 70:
        return "BLOCKED_UNTIL_LEGAL_AND_TECHNICAL_REVIEW"
    if blockers > 0:
        return "ARTICLE_5_REVIEW_REQUIRED"
    if high_risk > 0 and missing_controls >= 4:
        return "HIGH_RISK_WITH_INSUFFICIENT_EVIDENCE"
    if high_risk > 0:
        return "CONDITIONALLY_VIABLE_WITH_HIGH_RISK_CONTROLS"
    if risk_score >= 35:
        return "MODERATE_RISK_REVIEW_REQUIRED"
    return "LOW_SIGNAL_NOT_A_COMPLIANCE_VERDICT"


def compute_report(target: str, config: Dict[str, Any], no_snippets: bool = False) -> ScanReport:
    target_path = Path(target).resolve()
    all_signals: List[Signal] = []
    controls: Dict[str, List[Dict[str, Any]]] = {}
    files_scanned = 0

    excludes = config.get("exclude", []) if isinstance(config, dict) else []

    for path in iter_files(target_path, excludes):
        files_scanned += 1
        file_signals, file_controls = scan_file(path, target_path if target_path.is_dir() else path.parent, RISK_RULES + CONTROL_RULES, no_snippets)
        all_signals.extend(file_signals)
        for cid, hits in file_controls.items():
            controls.setdefault(cid, []).extend(hits)

    # Confidence-weighted risk. Cap to 100.
    raw_risk = sum(sig.weight * sig.confidence for sig in all_signals)

    # Context multipliers from optional config: intended purpose matters.
    multiplier = 1.0
    intended = json.dumps(config, ensure_ascii=False).lower() if config else ""
    if any(x in intended for x in ["employment", "recruitment", "education", "credit", "biometric", "law_enforcement", "police", "border"]):
        multiplier += 0.12
    if any(x in intended for x in ["eu_market", "european_union", "union", "spain", "canarias", "canary"]):
        multiplier += 0.05
    if any(x in intended for x in ["provider", "deployer", "controller", "processor"]):
        multiplier += 0.05

    risk_score = min(100, int(round(raw_risk * multiplier)))
    control_count = aggregate_controls(controls)

    required_controls = needed_controls(all_signals)
    detected_control_ids = {cid for cid, hits in controls.items() if hits}
    missing_controls = [cid for cid in required_controls if cid not in detected_control_ids]

    readiness_score = 100 if not required_controls else int(round(100 * (len(required_controls) - len(missing_controls)) / len(required_controls)))

    blockers = sum(1 for s in all_signals if s.bucket == "article_5_prohibited_practice_signal" and s.confidence >= 0.55)
    high_risk = sum(1 for s in all_signals if s.bucket == "annex_iii_high_risk_signal" and s.confidence >= 0.50)
    transparency = sum(1 for s in all_signals if s.bucket == "article_50_transparency_signal" and s.confidence >= 0.50)
    gdpr = sum(1 for s in all_signals if s.bucket == "gdpr_data_protection_overlap" and s.confidence >= 0.50)

    notes = [
        "This is a static signal scanner. Treat results as triage, not as a legal conclusion.",
        "A clean scan does not prove compliance; risky intent can exist outside code names.",
    ]
    if blockers:
        notes.append("Article 5 signals deserve priority because prohibited-practice exposure can block deployment regardless of later controls.")
    if high_risk and missing_controls:
        notes.append("High-risk signals require evidence of governance controls: risk management, data governance, documentation, logs, human oversight, robustness and monitoring.")
    if gdpr:
        notes.append("GDPR overlap detected: AI Act review should be paired with privacy-by-design/DPIA analysis where personal data is involved.")

    summary = ScanSummary(
        target=target,
        files_scanned=files_scanned,
        signals_total=len(all_signals),
        risk_score=risk_score,
        readiness_score=readiness_score,
        viability=classify_viability(risk_score, blockers, high_risk, len(missing_controls)),
        blockers=blockers,
        potential_high_risk=high_risk,
        transparency_risks=transparency,
        gdpr_overlaps=gdpr,
        governance_controls_detected=control_count,
        missing_governance_controls=missing_controls,
        notes=notes,
    )

    # Sort high confidence / high impact first.
    all_signals.sort(key=lambda s: (s.weight * s.confidence, s.confidence), reverse=True)

    return ScanReport(
        summary=summary,
        signals=all_signals,
        controls=controls,
        config=config,
        disclaimer="This tool identifies technical and documentary signals that may require EU AI Act/GDPR review. It is not legal advice and does not determine compliance.",
    )


def report_to_dict(report: ScanReport) -> Dict[str, Any]:
    return {
        "summary": asdict(report.summary),
        "signals": [asdict(s) for s in report.signals],
        "controls": report.controls,
        "config": report.config,
        "disclaimer": report.disclaimer,
    }


def render_markdown(report: ScanReport, max_signals: int = 30) -> str:
    s = report.summary
    lines = [
        "# TRACE AI Act Risk Scanner — Report",
        "",
        f"**Target:** `{s.target}`",
        f"**Files scanned:** {s.files_scanned}",
        f"**Signals found:** {s.signals_total}",
        f"**Risk score:** {s.risk_score}/100",
        f"**Governance readiness:** {s.readiness_score}/100",
        f"**Viability:** `{s.viability}`",
        "",
        "## Signal summary",
        "",
        f"- Article 5 blocker signals: {s.blockers}",
        f"- Annex III high-risk signals: {s.potential_high_risk}",
        f"- Article 50 transparency signals: {s.transparency_risks}",
        f"- GDPR/data-protection overlaps: {s.gdpr_overlaps}",
        f"- Governance controls detected: {s.governance_controls_detected}",
        "",
    ]

    if s.missing_governance_controls:
        lines += ["## Missing governance controls", ""]
        for cid in s.missing_governance_controls:
            ctrl = next((r for r in CONTROL_RULES if r.id == cid), None)
            label = ctrl.label if ctrl else cid
            basis = ctrl.legal_basis if ctrl else ""
            lines.append(f"- `{cid}` — {label} ({basis})")
        lines.append("")

    lines += ["## Top signals", ""]
    for sig in report.signals[:max_signals]:
        lines += [
            f"### {sig.severity}: {sig.label}",
            f"- Rule: `{sig.rule_id}`",
            f"- Legal basis: {sig.legal_basis}",
            f"- Location: `{sig.file}:{sig.line}`",
            f"- Matched: `{sig.matched}` | Confidence: {sig.confidence}",
            f"- Guidance: {sig.guidance}",
            "",
            "```",
            sig.evidence,
            "```",
            "",
        ]

    if report.controls:
        lines += ["## Detected governance controls", ""]
        for cid, hits in sorted(report.controls.items()):
            ctrl = next((r for r in CONTROL_RULES if r.id == cid), None)
            label = ctrl.label if ctrl else cid
            lines.append(f"- `{cid}` — {label}: {len(hits)} hit(s)")
        lines.append("")

    lines += ["## Notes", ""]
    for note in s.notes:
        lines.append(f"- {note}")
    lines += ["", f"> {report.disclaimer}", ""]
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="TRACE AI Act Risk Scanner")
    parser.add_argument("target", help="File or directory to scan")
    parser.add_argument("--config", help="Optional JSON/YAML context file describing company/system purpose")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    parser.add_argument("--markdown", help="Write Markdown report to path")
    parser.add_argument("--max-signals", type=int, default=30, help="Max signals in Markdown report")
    parser.add_argument("--no-snippets", action="store_true", help="Omit code snippets from the report to protect IP")
    parser.add_argument("--fail-on", choices=["none", "article5", "high", "any"], default="none", help="Fail pipeline if risk thresholds are met")
    args = parser.parse_args(argv)

    if not os.path.exists(args.target):
        raise SystemExit(f"Target does not exist: {args.target}")

    config = load_config(args.config)
    report = compute_report(args.target, config, args.no_snippets)

    if args.markdown:
        Path(args.markdown).write_text(render_markdown(report, args.max_signals), encoding="utf-8")

    if args.json:
        print(json.dumps(report_to_dict(report), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report, args.max_signals))

    if args.fail_on != "none":
        if args.fail_on == "any" and report.summary.signals_total > 0:
            return 1
        if args.fail_on in ["high", "article5"] and report.summary.blockers > 0:
            return 1
        if args.fail_on == "high" and report.summary.potential_high_risk > 0:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
