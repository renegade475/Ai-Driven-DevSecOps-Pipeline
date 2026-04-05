"""
Vulnerability parsers for SAST and DAST scan results
Converts tool-specific formats to common vulnerability model
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from models import Vulnerability, ScanResult, Location, Severity, ScanSource
from datetime import datetime
import hashlib


class SemgrepParser:
    """Parser for Semgrep SAST results"""
    
    def parse(self, semgrep_file: Path) -> ScanResult:
        """
        Parse Semgrep JSON output
        
        Args:
            semgrep_file: Path to Semgrep JSON file
            
        Returns:
            ScanResult object
        """
        with open(semgrep_file, 'r') as f:
            data = json.load(f)
        
        vulnerabilities = []
        results = data.get('results', [])
        
        for result in results:
            vuln = self._parse_semgrep_finding(result)
            if vuln:
                vulnerabilities.append(vuln)
        
        return ScanResult(
            scan_id=f"semgrep_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            scan_type=ScanSource.SAST,
            scan_date=datetime.utcnow(),
            vulnerabilities=vulnerabilities,
            metadata={
                'tool': 'semgrep',
                'total_findings': len(results)
            }
        )
    
    def _parse_semgrep_finding(self, finding: Dict[str, Any]) -> Optional[Vulnerability]:
        """Parse a single Semgrep finding"""
        try:
            # Extract location information
            path = finding.get('path', 'unknown')
            start_line = finding.get('start', {}).get('line')
            end_line = finding.get('end', {}).get('line')
            start_col = finding.get('start', {}).get('col')
            end_col = finding.get('end', {}).get('col')
            
            location = Location(
                file_path=path,
                line_start=start_line,
                line_end=end_line,
                column_start=start_col,
                column_end=end_col
            )
            
            # Extract metadata
            extra = finding.get('extra', {})
            metadata = extra.get('metadata', {})
            message = extra.get('message', finding.get('check_id', 'Unknown issue'))
            
            # Map severity
            severity_str = extra.get('severity', 'WARNING').upper()
            severity = self._map_severity(severity_str)
            
            # Extract CWE and OWASP
            cwe = metadata.get('cwe')
            owasp = metadata.get('owasp')
            
            # Generate unique ID
            vuln_id = self._generate_id('semgrep', path, start_line, finding.get('check_id'))
            
            # Extract confidence
            confidence_str = metadata.get('confidence', 'MEDIUM').upper()
            confidence = self._map_confidence(confidence_str)
            
            return Vulnerability(
                id=vuln_id,
                title=finding.get('check_id', 'Unknown'),
                description=message,
                severity=severity,
                source=ScanSource.SAST,
                location=location,
                cwe=cwe,
                owasp=owasp,
                confidence=confidence,
                raw_data={
                    'check_id': finding.get('check_id'),
                    'lines': finding.get('extra', {}).get('lines'),
                    'metadata': metadata,
                    'fingerprint': extra.get('fingerprint')
                },
                tags=[metadata.get('category', 'security')],
                references=metadata.get('references', [])
            )
        except Exception as e:
            print(f"Error parsing Semgrep finding: {e}")
            return None
    
    def _map_severity(self, semgrep_severity: str) -> Severity:
        """Map Semgrep severity to standard severity"""
        mapping = {
            'ERROR': Severity.HIGH,
            'WARNING': Severity.MEDIUM,
            'INFO': Severity.LOW
        }
        return mapping.get(semgrep_severity, Severity.MEDIUM)
    
    def _map_confidence(self, confidence_str: str) -> float:
        """Map confidence string to float"""
        mapping = {
            'HIGH': 0.9,
            'MEDIUM': 0.7,
            'LOW': 0.5
        }
        return mapping.get(confidence_str, 0.7)
    
    def _generate_id(self, source: str, path: str, line: int, check_id: str) -> str:
        """Generate unique vulnerability ID"""
        content = f"{source}:{path}:{line}:{check_id}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


class ZAPParser:
    """Parser for OWASP ZAP DAST results"""
    
    def parse(self, zap_file: Path) -> ScanResult:
        """
        Parse OWASP ZAP JSON output
        
        Args:
            zap_file: Path to ZAP JSON file
            
        Returns:
            ScanResult object
        """
        with open(zap_file, 'r') as f:
            data = json.load(f)
        
        vulnerabilities = []
        
        # ZAP format: site -> alerts
        sites = data.get('site', [])
        for site in sites:
            alerts = site.get('alerts', [])
            for alert in alerts:
                vulns = self._parse_zap_alert(alert, site.get('@name', 'unknown'))
                vulnerabilities.extend(vulns)
        
        return ScanResult(
            scan_id=f"zap_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            scan_type=ScanSource.DAST,
            scan_date=datetime.utcnow(),
            vulnerabilities=vulnerabilities,
            metadata={
                'tool': 'owasp-zap',
                'total_findings': len(vulnerabilities)
            }
        )
    
    def _parse_zap_alert(self, alert: Dict[str, Any], site_name: str) -> List[Vulnerability]:
        """Parse a single ZAP alert (may have multiple instances)"""
        vulnerabilities = []
        
        try:
            # Extract common alert information
            alert_name = alert.get('name', 'Unknown')
            description = alert.get('desc', '')
            solution = alert.get('solution', '')
            reference = alert.get('reference', '')
            
            # Map risk level to severity
            risk = alert.get('riskcode', '0')
            severity = self._map_risk_to_severity(risk)
            
            # Extract CWE
            cwe_id = alert.get('cweid')
            cwe = f"CWE-{cwe_id}" if cwe_id else None
            
            # Parse each instance of the alert
            instances = alert.get('instances', [])
            if not instances:
                # Create at least one vulnerability if no instances
                instances = [{}]
            
            for idx, instance in enumerate(instances):
                url = instance.get('uri', alert.get('uri', site_name))
                method = instance.get('method', alert.get('method', 'GET'))
                param = instance.get('param', alert.get('param', ''))
                evidence = instance.get('evidence', '')
                
                location = Location(
                    file_path='',
                    url=url,
                    method=method,
                    parameter=param
                )
                
                # Generate unique ID
                vuln_id = self._generate_id('zap', url, alert_name, param, idx)
                
                # Map confidence
                confidence = self._map_confidence(alert.get('confidence', '2'))
                
                vuln = Vulnerability(
                    id=vuln_id,
                    title=alert_name,
                    description=description,
                    severity=severity,
                    source=ScanSource.DAST,
                    location=location,
                    cwe=cwe,
                    owasp=self._map_cwe_to_owasp(cwe_id),
                    confidence=confidence,
                    raw_data={
                        'alert_id': alert.get('pluginid'),
                        'risk': risk,
                        'evidence': evidence,
                        'attack': instance.get('attack', ''),
                        'solution': solution
                    },
                    tags=[alert.get('alertRef', '')],
                    references=reference.split('\n') if reference else [],
                    remediation_guidance=solution
                )
                
                vulnerabilities.append(vuln)
        
        except Exception as e:
            print(f"Error parsing ZAP alert: {e}")
        
        return vulnerabilities
    
    def _map_risk_to_severity(self, risk_code: str) -> Severity:
        """Map ZAP risk code to severity"""
        mapping = {
            '3': Severity.HIGH,      # ZAP's max risk level is High, not Critical
            '2': Severity.MEDIUM,
            '1': Severity.LOW,
            '0': Severity.INFO
        }
        return mapping.get(str(risk_code), Severity.INFO)
    
    def _map_confidence(self, confidence_code: str) -> float:
        """Map ZAP confidence code to float"""
        mapping = {
            '3': 0.9,  # High
            '2': 0.7,  # Medium
            '1': 0.5,  # Low
            '0': 0.3   # False Positive
        }
        return mapping.get(str(confidence_code), 0.7)
    
    def _map_cwe_to_owasp(self, cwe_id: Optional[str]) -> Optional[str]:
        """Map CWE to OWASP Top 10 2021"""
        if not cwe_id:
            return None
        
        # Common CWE to OWASP mappings
        mapping = {
            '89': 'A03:2021-Injection',
            '79': 'A03:2021-Injection',
            '78': 'A03:2021-Injection',
            '22': 'A01:2021-Broken Access Control',
            '352': 'A01:2021-Broken Access Control',
            '287': 'A07:2021-Identification and Authentication Failures',
            '798': 'A07:2021-Identification and Authentication Failures',
            '327': 'A02:2021-Cryptographic Failures',
            '502': 'A08:2021-Software and Data Integrity Failures',
            '918': 'A10:2021-Server-Side Request Forgery'
        }
        return mapping.get(str(cwe_id))
    
    def _generate_id(self, source: str, url: str, alert: str, param: str, idx: int) -> str:
        """Generate unique vulnerability ID"""
        content = f"{source}:{url}:{alert}:{param}:{idx}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


def parse_scan_results(sast_dir: Path, dast_dir: Path) -> tuple[Optional[ScanResult], Optional[ScanResult]]:
    """
    Parse all scan results from directories
    
    Args:
        sast_dir: Directory containing SAST results
        dast_dir: Directory containing DAST results
        
    Returns:
        Tuple of (SAST results, DAST results)
    """
    sast_result = None
    dast_result = None
    
    # Parse SAST results
    if sast_dir.exists():
        semgrep_parser = SemgrepParser()
        for sast_file in sast_dir.glob('*.json'):
            try:
                result = semgrep_parser.parse(sast_file)
                if sast_result is None:
                    sast_result = result
                else:
                    # Merge results
                    sast_result.vulnerabilities.extend(result.vulnerabilities)
            except Exception as e:
                print(f"Error parsing SAST file {sast_file}: {e}")
    
    # Parse DAST results
    if dast_dir.exists():
        zap_parser = ZAPParser()
        for dast_file in dast_dir.glob('*.json'):
            try:
                result = zap_parser.parse(dast_file)
                if dast_result is None:
                    dast_result = result
                else:
                    # Merge results
                    dast_result.vulnerabilities.extend(result.vulnerabilities)
            except Exception as e:
                print(f"Error parsing DAST file {dast_file}: {e}")
    
    return sast_result, dast_result
