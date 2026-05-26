"""
TRACE™ AI Act Compliance Extractor
==================================
Zero-Trust AST-based Codebase Auditor for EU AI Act Compliance.

This tool statically analyzes Python codebases (via AST) to detect structural 
patterns that may violate the EU AI Act prohibited practices or high-risk requirements, 
such as emotion recognition, biometric categorization, predictive policing, 
or un-watermarked deepfake generation.
"""

import ast
import os
import json
import argparse
from typing import List, Dict, Any

# Heuristics for EU AI Act Prohibited Practices
HEURISTICS = {
    "biometric_rbi": {
        "keywords": ["face_recognition", "cctv_live", "real_time_tracking", "biometric_id", "remote_id"],
        "severity": "CRITICAL - PROHIBITED (Article 5)",
        "description": "Real-time Remote Biometric Identification (RBI) in publicly accessible spaces."
    },
    "biometric_emotion_recognition": {
        "keywords": ["emotion", "sentiment_facial", "detect_mood", "analyze_affect", "DeepFace", "FER", "voice_stress"],
        "severity": "CRITICAL - PROHIBITED (Article 5)",
        "description": "AI systems used in the workplace or educational institutions to infer emotions."
    },
    "biometric_categorization": {
        "keywords": ["race", "ethnicity", "sexual_orientation", "political_opinion", "categorize_face", "trade_union"],
        "severity": "CRITICAL - PROHIBITED (Article 5)",
        "description": "Categorization of natural persons based on biometrics to deduce sensitive data."
    },
    "predictive_policing": {
        "keywords": ["predict_crime", "risk_score_criminal", "recidivism", "predictive_policing", "offense_probability"],
        "severity": "CRITICAL - PROHIBITED (Article 5)",
        "description": "Risk assessments to predict the likelihood of an individual committing a criminal offense."
    },
    "social_scoring": {
        "keywords": ["social_score", "citizen_trust", "behavior_score_public", "social_credit"],
        "severity": "CRITICAL - PROHIBITED (Article 5)",
        "description": "Evaluation or classification of natural persons over time based on social behavior."
    },
    "subliminal_manipulation": {
        "keywords": ["subliminal", "manipulate_behavior", "dark_pattern", "cognitive_distortion"],
        "severity": "CRITICAL - PROHIBITED (Article 5)",
        "description": "Subliminal techniques deployed beyond a person's consciousness to materially distort their behavior."
    },
    "critical_infrastructure_digital": {
        "keywords": ["scada", "smart_grid", "traffic_control", "dns_routing_ai"],
        "severity": "HIGH RISK (Annex III)",
        "description": "AI components in the management and operation of critical digital infrastructure or road traffic."
    },
    "critical_infrastructure_physical": {
        "keywords": ["water_supply_ai", "gas_control", "heating_network", "electricity_grid_ai"],
        "severity": "HIGH RISK (Annex III)",
        "description": "AI components in the management and operation of physical critical infrastructure (water, gas, electricity)."
    },
    "education_admission_scoring": {
        "keywords": ["admission_score", "predict_grades", "student_risk", "evaluate_learning"],
        "severity": "HIGH RISK (Annex III)",
        "description": "AI systems used to determine access or assign natural persons to educational institutions."
    },
    "education_proctoring": {
        "keywords": ["proctor_exam", "cheat_detection", "monitor_student", "eye_tracking_exam"],
        "severity": "HIGH RISK (Annex III)",
        "description": "AI systems used to monitor and detect prohibited behavior of students during tests."
    },
    "workplace_automated_rejection": {
        "keywords": ["auto_reject", "filter_cv_auto", "score_candidate_auto", "resume_parser_score"],
        "severity": "HIGH RISK (Annex III)",
        "description": "AI systems used for recruitment or selection, particularly automated filtering of applications."
    },
    "workplace_management_allocation": {
        "keywords": ["shift_allocation", "worker_monitoring", "performance_score_worker", "gig_economy_score"],
        "severity": "HIGH RISK (Annex III)",
        "description": "AI used to make decisions affecting terms of work-related relationships, task allocation, or performance."
    },
    "credit_scoring": {
        "keywords": ["credit_score", "loan_approval_ai", "creditworthiness"],
        "severity": "HIGH RISK (Annex III)",
        "description": "AI systems used to evaluate the creditworthiness of natural persons or establish their credit score."
    },
    "generative_ai_watermarking": {
        "keywords": ["generate_image", "deepfake", "generate_audio", "synthetic_media", "watermark_missing"],
        "severity": "TRANSPARENCY RISK (Article 50)",
        "description": "Systems generating synthetic audio, image, or video content without clear machine-readable watermarking."
    },
    "democratic_process_elections": {
        "keywords": ["voter_influence", "election_score", "political_targeting", "campaign_ai"],
        "severity": "HIGH RISK (Annex III)",
        "description": "AI systems intended to influence the outcome of an election or referendum."
    }
}

class TraceASTVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.flags = []

    def _check_name(self, name: str, node: ast.AST):
        if not name:
            return
        
        name_lower = name.lower()
        for flag_id, rule in HEURISTICS.items():
            for kw in rule["keywords"]:
                if kw.lower() in name_lower:
                    self.flags.append({
                        "file": self.filename,
                        "line": getattr(node, 'lineno', 0),
                        "node_type": type(node).__name__,
                        "matched_keyword": kw,
                        "flag_id": flag_id,
                        "rule": rule["description"],
                        "severity": rule["severity"]
                    })

    def visit_FunctionDef(self, node):
        self._check_name(node.name, node)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self._check_name(node.func.id, node)
        elif isinstance(node.func, ast.Attribute):
            self._check_name(node.func.attr, node)
        self.generic_visit(node)

    def visit_Name(self, node):
        self._check_name(node.id, node)
        self.generic_visit(node)

def analyze_file(filepath: str) -> List[Dict[Any, Any]]:
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError as e:
            print(f"Syntax error in {filepath}: {e}")
            return []
    
    visitor = TraceASTVisitor(filepath)
    visitor.visit(tree)
    return visitor.flags

def analyze_directory(directory: str) -> List[Dict[Any, Any]]:
    all_flags = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                all_flags.extend(analyze_file(filepath))
    return all_flags

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TRACE AI Act Compliance Auditor")
    parser.add_argument("target", help="Directory or Python file to analyze")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    target_path = args.target
    if not os.path.exists(target_path):
        print(f"Error: Path {target_path} does not exist.")
        exit(1)

    if os.path.isfile(target_path):
        flags = analyze_file(target_path)
    else:
        flags = analyze_directory(target_path)

    if args.json:
        print(json.dumps(flags, indent=2))
    else:
        print(f"\nTRACE AI Act Compliance Audit for: {target_path}")
        print("=" * 60)
        if not flags:
            print("No AI Act compliance flags detected.")
        else:
            print(f"Found {len(flags)} potential compliance flags:\n")
            for f in flags:
                print(f"[{f['severity']}] {f['file']}:{f['line']}")
                print(f"  Flag: {f['flag_id']} (matched keyword: '{f['matched_keyword']}')")
                print(f"  Rule: {f['rule']}\n")
