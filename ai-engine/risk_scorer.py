"""
Risk Scorer for the AI-Driven DevSecOps Pipeline
Calculates multi-factor risk scores for vulnerabilities
"""

from typing import List, Dict
from models import Vulnerability, PolicyConfig, Severity


class RiskScorer:
    """Calculates risk scores using multiple factors"""
    
    def __init__(self, policy: PolicyConfig):
        """
        Initialize risk scorer
        
        Args:
            policy: Policy configuration
        """
        self.policy = policy
        self.risk_factors = policy.risk_factors
    
    def score_vulnerabilities(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
        """
        Calculate risk scores for all vulnerabilities
        
        Args:
            vulnerabilities: List of vulnerabilities
            
        Returns:
            List with risk scores calculated
        """
        for vuln in vulnerabilities:
            # Skip false positives
            if vuln.is_false_positive:
                vuln.risk_score = 0.0
                continue
            
            # Calculate individual factor scores
            severity_score = self._calculate_severity_score(vuln)
            exploitability_score = self._calculate_exploitability_score(vuln)
            business_impact_score = self._calculate_business_impact_score(vuln)
            exposure_score = self._calculate_exposure_score(vuln)
            compliance_score = self._calculate_compliance_score(vuln)
            
            # Store individual scores
            vuln.exploitability_score = exploitability_score
            vuln.business_impact_score = business_impact_score
            vuln.exposure_score = exposure_score
            
            # Calculate weighted risk score
            risk_score = (
                severity_score * self.risk_factors.get('severity', 0.3) +
                exploitability_score * self.risk_factors.get('exploitability', 0.25) +
                business_impact_score * self.risk_factors.get('business_impact', 0.2) +
                exposure_score * self.risk_factors.get('exposure', 0.15) +
                compliance_score * self.risk_factors.get('compliance', 0.1)
            )
            
            vuln.risk_score = min(1.0, max(0.0, risk_score))
        
        return vulnerabilities
    
    def _calculate_severity_score(self, vuln: Vulnerability) -> float:
        """Calculate score based on severity"""
        severity_weights = self.policy.severity_weights
        return severity_weights.get(vuln.severity.value, 0.5)
    
    def _calculate_exploitability_score(self, vuln: Vulnerability) -> float:
        """Calculate exploitability score"""
        # Determine exploitability based on vulnerability type and characteristics
        cwe = vuln.cwe
        
        # High exploitability vulnerabilities
        high_exploit_cwes = ['CWE-89', 'CWE-78', 'CWE-94', 'CWE-502']  # SQLi, Command Injection, Code Injection
        if cwe in high_exploit_cwes:
            return self.policy.exploitability_scores.get('PROVEN_EXPLOIT', 1.0)
        
        # Medium exploitability
        medium_exploit_cwes = ['CWE-79', 'CWE-352', 'CWE-22']  # XSS, CSRF, Path Traversal
        if cwe in medium_exploit_cwes:
            return self.policy.exploitability_scores.get('FUNCTIONAL_EXPLOIT', 0.9)
        
        # Authentication/crypto issues
        auth_cwes = ['CWE-287', 'CWE-798', 'CWE-327']
        if cwe in auth_cwes:
            return self.policy.exploitability_scores.get('POC_EXPLOIT', 0.7)
        
        # Default based on severity
        if vuln.severity == Severity.CRITICAL:
            return self.policy.exploitability_scores.get('FUNCTIONAL_EXPLOIT', 0.9)
        elif vuln.severity == Severity.HIGH:
            return self.policy.exploitability_scores.get('POC_EXPLOIT', 0.7)
        else:
            return self.policy.exploitability_scores.get('THEORETICAL', 0.4)
    
    def _calculate_business_impact_score(self, vuln: Vulnerability) -> float:
        """Calculate business impact score"""
        # Determine impact based on vulnerability type
        cwe = vuln.cwe
        
        # Catastrophic impact - data breach, RCE
        catastrophic_cwes = ['CWE-89', 'CWE-78', 'CWE-94', 'CWE-502', 'CWE-798']
        if cwe in catastrophic_cwes:
            return self.policy.business_impact_scores.get('CATASTROPHIC', 1.0)
        
        # Severe impact - authentication bypass, sensitive data exposure
        severe_cwes = ['CWE-287', 'CWE-306', 'CWE-200', 'CWE-311']
        if cwe in severe_cwes:
            return self.policy.business_impact_scores.get('SEVERE', 0.8)
        
        # Moderate impact - XSS, CSRF
        moderate_cwes = ['CWE-79', 'CWE-352', 'CWE-918']
        if cwe in moderate_cwes:
            return self.policy.business_impact_scores.get('MODERATE', 0.5)
        
        # Default based on severity
        severity_impact_map = {
            Severity.CRITICAL: self.policy.business_impact_scores.get('CATASTROPHIC', 1.0),
            Severity.HIGH: self.policy.business_impact_scores.get('SEVERE', 0.8),
            Severity.MEDIUM: self.policy.business_impact_scores.get('MODERATE', 0.5),
            Severity.LOW: self.policy.business_impact_scores.get('MINOR', 0.3),
            Severity.INFO: self.policy.business_impact_scores.get('NEGLIGIBLE', 0.1)
        }
        return severity_impact_map.get(vuln.severity, 0.5)
    
    def _calculate_exposure_score(self, vuln: Vulnerability) -> float:
        """Calculate exposure score"""
        # DAST vulnerabilities are in running applications (higher exposure)
        if vuln.source.value == 'DAST':
            # Check if URL indicates public endpoint
            url = vuln.location.url or ''
            if url:
                # Public endpoints have higher exposure
                if any(indicator in url.lower() for indicator in ['/api/', '/public/', '/login', '/register']):
                    return self.policy.exposure_scores.get('PUBLIC_INTERNET', 1.0)
                else:
                    return self.policy.exposure_scores.get('AUTHENTICATED_EXTERNAL', 0.7)
            return self.policy.exposure_scores.get('AUTHENTICATED_EXTERNAL', 0.7)
        
        # SAST vulnerabilities - check file path
        file_path = vuln.location.file_path.lower()
        
        # API/web endpoints have higher exposure
        if any(indicator in file_path for indicator in ['api', 'controller', 'view', 'route', 'endpoint']):
            return self.policy.exposure_scores.get('AUTHENTICATED_EXTERNAL', 0.7)
        
        # Internal services/utilities have lower exposure
        if any(indicator in file_path for indicator in ['internal', 'util', 'helper', 'service']):
            return self.policy.exposure_scores.get('INTERNAL_NETWORK', 0.4)
        
        # Default to internal network
        return self.policy.exposure_scores.get('INTERNAL_NETWORK', 0.4)
    
    def _calculate_compliance_score(self, vuln: Vulnerability) -> float:
        """Calculate compliance impact score"""
        # Check if vulnerability maps to compliance frameworks
        owasp = vuln.owasp
        cwe = vuln.cwe

        # Normalize owasp: parsers may return a list instead of a string
        if isinstance(owasp, list):
            owasp = owasp[0] if owasp else None

        # High compliance impact for OWASP Top 10 (A01 through A10)
        owasp_top10_prefixes = ('A01:', 'A02:', 'A03:', 'A04:', 'A05:',
                                'A06:', 'A07:', 'A08:', 'A09:', 'A10:')
        if owasp and any(owasp.startswith(p) for p in owasp_top10_prefixes):
            return 1.0
        
        # Medium compliance impact for common CWEs
        if cwe:
            return 0.7
        
        # Default
        return 0.5
    
    def get_statistics(self, vulnerabilities: List[Vulnerability]) -> Dict:
        """
        Get risk scoring statistics
        
        Args:
            vulnerabilities: List of scored vulnerabilities
            
        Returns:
            Statistics dictionary
        """
        if not vulnerabilities:
            return {}
        
        scores = [v.risk_score for v in vulnerabilities if not v.is_false_positive]
        
        if not scores:
            return {}
        
        return {
            'average_risk_score': round(sum(scores) / len(scores), 3),
            'max_risk_score': round(max(scores), 3),
            'min_risk_score': round(min(scores), 3),
            'high_risk_count': sum(1 for s in scores if s >= 0.7),
            'medium_risk_count': sum(1 for s in scores if 0.4 <= s < 0.7),
            'low_risk_count': sum(1 for s in scores if s < 0.4)
        }
