"""
Policy loader for the AI-Driven DevSecOps Pipeline
Loads and validates security policy configuration from YAML
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from models import PolicyConfig


class PolicyLoader:
    """Loads and validates security policy configuration"""
    
    def __init__(self, policy_path: str):
        """
        Initialize policy loader
        
        Args:
            policy_path: Path to policy YAML file
        """
        self.policy_path = Path(policy_path)
        self.config: Optional[PolicyConfig] = None
    
    def load(self) -> PolicyConfig:
        """
        Load policy configuration from YAML file
        
        Returns:
            PolicyConfig object
            
        Raises:
            FileNotFoundError: If policy file doesn't exist
            ValueError: If policy configuration is invalid
        """
        if not self.policy_path.exists():
            raise FileNotFoundError(f"Policy file not found: {self.policy_path}")
        
        with open(self.policy_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        
        # Validate and parse configuration
        self.config = self._parse_config(raw_config)
        return self.config
    
    def _parse_config(self, raw: Dict[str, Any]) -> PolicyConfig:
        """
        Parse raw YAML configuration into PolicyConfig object
        
        Args:
            raw: Raw configuration dictionary
            
        Returns:
            PolicyConfig object
        """
        # Extract severity configuration
        severity = raw.get('severity', {})
        severity_weights = severity.get('weights', {})
        severity_threshold = severity.get('threshold', 'LOW')
        blocking_severities = severity.get('blocking_severities', [])
        
        # Extract false positive detection configuration
        fp_config = raw.get('false_positive_detection', {})
        fp_enabled = fp_config.get('enabled', True)
        fp_confidence_threshold = fp_config.get('confidence_threshold', 0.7)
        
        exclusion_patterns = fp_config.get('exclusion_patterns', {})
        fp_file_patterns = exclusion_patterns.get('file_patterns', [])
        fp_code_patterns = exclusion_patterns.get('code_patterns', [])
        
        # Extract risk scoring configuration
        risk_config = raw.get('risk_scoring', {})
        risk_factors = risk_config.get('factors', {})
        exploitability_scores = risk_config.get('exploitability', {})
        business_impact_scores = risk_config.get('business_impact', {})
        exposure_scores = risk_config.get('exposure', {})
        
        # Extract prioritization configuration
        priority_config = raw.get('prioritization', {})
        top_priority_limit = priority_config.get('top_priority_limit', 20)
        auto_priority_rules = priority_config.get('auto_priority_rules', [])
        
        # Extract remediation SLA configuration
        sla_config = raw.get('remediation_sla', {})
        sla_by_priority = sla_config.get('by_priority', {})
        sla_by_severity = sla_config.get('by_severity', {})
        
        return PolicyConfig(
            version=raw.get('version', '1.0'),
            policy_name=raw.get('policy_name', 'Default Policy'),
            severity_weights=severity_weights,
            severity_threshold=severity_threshold,
            blocking_severities=blocking_severities,
            fp_enabled=fp_enabled,
            fp_confidence_threshold=fp_confidence_threshold,
            fp_file_patterns=fp_file_patterns,
            fp_code_patterns=fp_code_patterns,
            risk_factors=risk_factors,
            exploitability_scores=exploitability_scores,
            business_impact_scores=business_impact_scores,
            exposure_scores=exposure_scores,
            top_priority_limit=top_priority_limit,
            auto_priority_rules=auto_priority_rules,
            sla_by_priority=sla_by_priority,
            sla_by_severity=sla_by_severity,
            raw_config=raw
        )
    
    def get_severity_weight(self, severity: str) -> float:
        """Get weight for a severity level"""
        if not self.config:
            raise ValueError("Policy not loaded")
        return self.config.severity_weights.get(severity, 0.5)
    
    def is_blocking_severity(self, severity: str) -> bool:
        """Check if severity should block CI/CD"""
        if not self.config:
            raise ValueError("Policy not loaded")
        return severity in self.config.blocking_severities
    
    def get_sla_days(self, severity: str = None, priority: int = None) -> int:
        """
        Get remediation SLA in days
        
        Args:
            severity: Vulnerability severity
            priority: Vulnerability priority (1-5)
            
        Returns:
            SLA in days
        """
        if not self.config:
            raise ValueError("Policy not loaded")
        
        # Priority takes precedence
        if priority is not None:
            return self.config.sla_by_priority.get(priority, 90)
        
        # Fall back to severity
        if severity is not None:
            return self.config.sla_by_severity.get(severity, 90)
        
        return 90  # Default
