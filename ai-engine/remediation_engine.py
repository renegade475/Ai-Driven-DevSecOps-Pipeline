"""
Enhanced Remediation Engine for the AI-Driven DevSecOps Pipeline
Generates detailed, context-aware remediation guidance using Google Gemini.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
import google.generativeai as genai
from models import Vulnerability, Severity

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class RemediationEngine:
    """Generates remediation guidance using detailed scanner metadata and Gemini AI"""

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the remediation engine with Gemini model.
        
        Args:
            model_name: The Gemini model to use (default: gemini-2.0-flash)
        """
        self.model = genai.GenerativeModel(model_name)

    def _generate_with_gemini(self, llm_context: Dict[str, Any]) -> str:
        """
        Call Gemini API to generate remediation guidance.
        
        Args:
            llm_context: Structured context about the vulnerability
            
        Returns:
            Generated remediation guidance from Gemini
        """
        prompt = f"""You are a security expert. Analyze this vulnerability and provide detailed remediation guidance.

**Vulnerability Details:**
- **File:** {llm_context['file_path']}
- **Lines:** {llm_context['line_range']['start']} - {llm_context['line_range']['end']}
- **CWE:** {llm_context['cwe']}
- **Severity:** {llm_context['severity']}
- **Description:** {llm_context['description']}

**Vulnerable Code:**
```
{llm_context['vulnerable_code']}
```

**Additional Context:**
{json.dumps(llm_context.get('raw_data', {}), indent=2)}

Please provide:
1. **Root Cause Analysis**: Why is this code vulnerable?
2. **Impact Assessment**: What could happen if exploited?
3. **Remediation Steps**: Step-by-step fix instructions
4. **Fixed Code Example**: Provide corrected code
5. **Prevention Tips**: How to avoid this in the future

Be specific and actionable in your response."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[ERROR] Failed to generate remediation with Gemini: {str(e)}"

    # Severity ranking for sorting (lower number = higher priority)
    SEVERITY_RANK = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4,
    }

    def generate_guidance(self, vulnerabilities: List[Vulnerability], top_n: int = 3) -> List[Vulnerability]:
        """
        Generate remediation guidance for the top N most severe vulnerabilities.

        Vulnerabilities are ranked by severity (CRITICAL > HIGH > MEDIUM > LOW > INFO)
        with risk_score as a tiebreaker. Only the top N non-false-positive
        vulnerabilities receive AI-generated remediation from Gemini.

        Args:
            vulnerabilities: List of detected vulnerabilities.
            top_n: Number of top vulnerabilities to generate remediation for (default: 3).
        """
        # Filter out false positives, then sort by severity rank and risk score
        actionable = [v for v in vulnerabilities if not v.is_false_positive]
        actionable.sort(
            key=lambda v: (self.SEVERITY_RANK.get(v.severity, 99), -v.risk_score)
        )

        # Only remediate the top N
        top_vulns = set(id(v) for v in actionable[:top_n])

        for vuln in vulnerabilities:
            if id(vuln) not in top_vulns:
                continue

            llm_context = self._build_llm_context(vuln)

            # Generate remediation using Gemini
            remediation = self._generate_with_gemini(llm_context)

            vuln.remediation_guidance = remediation
            vuln.code_example = llm_context["vulnerable_code"]

        return vulnerabilities

    def _build_llm_context(self, vuln: Vulnerability) -> Dict[str, Any]:
        """
        Build a single structured context object for LLM consumption.
        """
        file_path = vuln.location.file_path
        line_start = vuln.location.line_start
        line_end = vuln.location.line_end

        vulnerable_code = self._extract_vulnerable_code(
            file_path, line_start, line_end
        )

        return {
            "file_path": file_path,
            "line_range": {
                "start": line_start,
                "end": line_end
            },
            "cwe": vuln.cwe,
            "description": vuln.description,
            "severity": vuln.severity,
            "raw_data": vuln.raw_data,
            "vulnerable_code": vulnerable_code
        }

    def _extract_vulnerable_code(
        self,
        file_path: str,
        line_start: int,
        line_end: int
    ) -> str:
        """
        Safely extract vulnerable code lines from a source file.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return "[ERROR] Source file not found."

            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

            # Line numbers are 1-based
            extracted = lines[line_start - 1 : line_end]

            return "\n".join(extracted)

        except Exception as exc:
            return f"[ERROR] Failed to extract code: {exc}"

    @staticmethod
    def serialize_for_llm(llm_context: Dict[str, Any]) -> str:
        """
        Serialize context to JSON for text-only LLM APIs.
        """
        return json.dumps(llm_context, indent=2)
