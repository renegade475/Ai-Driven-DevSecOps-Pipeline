"""
Main orchestrator for the AI-Driven DevSecOps Pipeline
Coordinates all AI processing components
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import sys

from models import AnalysisReport, Severity
from policy_loader import PolicyLoader
from parsers import parse_scan_results
from false_positive_detector import FalsePositiveDetector
from risk_scorer import RiskScorer
from prioritizer import VulnerabilityPrioritizer
from remediation_engine import RemediationEngine


class AIEngine:
    """Main AI processing engine"""
    
    def __init__(self, policy_path: str, verbose: bool = False):
        """
        Initialize AI engine
        
        Args:
            policy_path: Path to policy configuration file
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.log("Initializing AI-Driven DevSecOps Engine...")
        
        # Load policy
        self.log(f"Loading policy from: {policy_path}")
        policy_loader = PolicyLoader(policy_path)
        self.policy = policy_loader.load()
        self.log(f"Policy loaded: {self.policy.policy_name} v{self.policy.version}")
        
        # Initialize components
        self.fp_detector = FalsePositiveDetector(self.policy)
        self.risk_scorer = RiskScorer(self.policy)
        self.prioritizer = VulnerabilityPrioritizer(self.policy)
        self.remediation_engine = RemediationEngine()
        
        self.log("AI Engine initialized successfully")
    
    def process(self, sast_dir: Path, dast_dir: Path) -> AnalysisReport:
        """
        Process scan results through AI pipeline
        
        Args:
            sast_dir: Directory containing SAST results
            dast_dir: Directory containing DAST results
            
        Returns:
            AnalysisReport with processed results
        """
        self.log("\n" + "="*60)
        self.log("Starting AI Analysis Pipeline")
        self.log("="*60)
        
        # Step 1: Parse scan results
        self.log("\n[1/5] Parsing scan results...")
        sast_result, dast_result = parse_scan_results(sast_dir, dast_dir)
        
        sast_count = len(sast_result.vulnerabilities) if sast_result else 0
        dast_count = len(dast_result.vulnerabilities) if dast_result else 0
        self.log(f"  SAST findings: {sast_count}")
        self.log(f"  DAST findings: {dast_count}")
        
        # Combine all vulnerabilities
        all_vulnerabilities = []
        if sast_result:
            all_vulnerabilities.extend(sast_result.vulnerabilities)
        if dast_result:
            all_vulnerabilities.extend(dast_result.vulnerabilities)
        
        self.log(f"  Total raw findings: {len(all_vulnerabilities)}")
        
        if not all_vulnerabilities:
            self.log("\n⚠️  No vulnerabilities found in scan results")
            return self._create_empty_report()
        
        # Step 2: False positive detection
        self.log("\n[2/5] Detecting false positives...")
        all_vulnerabilities = self.fp_detector.analyze(all_vulnerabilities)
        fp_stats = self.fp_detector.get_statistics(all_vulnerabilities)
        
        self.log(f"  False positives detected: {fp_stats['false_positives']}")
        self.log(f"  False positive rate: {fp_stats['false_positive_rate']:.1f}%")
        self.log(f"  True positives: {fp_stats['true_positives']}")
        
        # Step 3: Risk scoring
        self.log("\n[3/5] Calculating risk scores...")
        all_vulnerabilities = self.risk_scorer.score_vulnerabilities(all_vulnerabilities)
        risk_stats = self.risk_scorer.get_statistics(all_vulnerabilities)
        
        if risk_stats:
            self.log(f"  Average risk score: {risk_stats['average_risk_score']}")
            self.log(f"  High risk vulnerabilities: {risk_stats['high_risk_count']}")
            self.log(f"  Medium risk vulnerabilities: {risk_stats['medium_risk_count']}")
            self.log(f"  Low risk vulnerabilities: {risk_stats['low_risk_count']}")
        
        # Step 4: Prioritization
        self.log("\n[4/5] Prioritizing vulnerabilities...")
        all_vulnerabilities = self.prioritizer.prioritize(all_vulnerabilities)
        priority_stats = self.prioritizer.get_statistics(all_vulnerabilities)
        
        self.log(f"  Priority 1 (Critical): {priority_stats['priority_1']}")
        self.log(f"  Priority 2 (High): {priority_stats['priority_2']}")
        self.log(f"  Priority 3 (Medium): {priority_stats['priority_3']}")
        
        # Step 5: Generate remediation guidance (must run before get_top_priorities
        # so that the same objects the prioritizer selects already have guidance set)
        self.log("\n[5/5] Generating remediation guidance...")
        all_vulnerabilities = self.remediation_engine.generate_guidance(all_vulnerabilities)
        remediated = sum(1 for v in all_vulnerabilities if v.remediation_guidance)
        self.log(f"  Remediation guidance generated for top {remediated} findings")
        
        # Fetch top priorities AFTER remediation so guidance is already populated
        top_priorities = self.prioritizer.get_top_priorities(all_vulnerabilities)
        self.log(f"  Top {len(top_priorities)} priorities identified")
        
        # Create analysis report
        filtered_vulns = self.fp_detector.filter_false_positives(all_vulnerabilities)
        
        report = AnalysisReport(
            report_id=f"ai_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            generated_at=datetime.utcnow(),
            sast_results=sast_result,
            dast_results=dast_result,
            all_vulnerabilities=all_vulnerabilities,
            filtered_vulnerabilities=filtered_vulns,
            top_priorities=top_priorities,
            policy_version=self.policy.version,
            policy_name=self.policy.policy_name,
            summary=self._generate_summary(
                all_vulnerabilities,
                filtered_vulns,
                top_priorities,
                fp_stats,
                risk_stats,
                priority_stats
            )
        )
        
        self.log("\n" + "="*60)
        self.log("AI Analysis Complete")
        self.log("="*60)
        
        return report
    
    def _generate_summary(self, all_vulns, filtered_vulns, top_priorities, 
                         fp_stats, risk_stats, priority_stats) -> dict:
        """Generate summary statistics"""
        
        # Count by severity
        severity_counts = {}
        for severity in Severity:
            severity_counts[severity.value] = sum(
                1 for v in filtered_vulns if v.severity == severity
            )
        
        # Count by source
        source_counts = {
            'SAST': sum(1 for v in filtered_vulns if v.source.value == 'SAST'),
            'DAST': sum(1 for v in filtered_vulns if v.source.value == 'DAST')
        }
        
        return {
            'total_vulnerabilities': len(all_vulns),
            'filtered_vulnerabilities': len(filtered_vulns),
            'false_positives': fp_stats['false_positives'],
            'false_positive_rate': fp_stats['false_positive_rate'] / 100,
            'by_severity': severity_counts,
            'by_source': source_counts,
            'risk_statistics': risk_stats,
            'priority_statistics': priority_stats,
            'top_priorities_count': len(top_priorities)
        }
    
    def _create_empty_report(self) -> AnalysisReport:
        """Create empty report when no vulnerabilities found"""
        return AnalysisReport(
            report_id=f"ai_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            generated_at=datetime.utcnow(),
            policy_version=self.policy.version,
            policy_name=self.policy.policy_name,
            summary={
                'total_vulnerabilities': 0,
                'filtered_vulnerabilities': 0,
                'false_positives': 0,
                'false_positive_rate': 0.0,
                'by_severity': {s.value: 0 for s in Severity},
                'by_source': {'SAST': 0, 'DAST': 0}
            }
        )
    
    def log(self, message: str):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AI-Driven DevSecOps Pipeline - Vulnerability Analysis Engine'
    )
    parser.add_argument(
        '--sast-results',
        type=str,
        required=True,
        help='Directory containing SAST scan results'
    )
    parser.add_argument(
        '--dast-results',
        type=str,
        required=True,
        help='Directory containing DAST scan results'
    )
    parser.add_argument(
        '--policy',
        type=str,
        required=True,
        help='Path to policy configuration file'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output path for analysis report (JSON)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize engine
        engine = AIEngine(args.policy, verbose=args.verbose)
        
        # Process scan results
        report = engine.process(
            Path(args.sast_results),
            Path(args.dast_results)
        )
        
        # Save report
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        print(f"\n✅ Analysis report saved to: {output_path}")
        
        # Print summary
        summary = report.summary
        print(f"\n📊 Summary:")
        print(f"  Total findings: {summary['total_vulnerabilities']}")
        print(f"  After filtering: {summary['filtered_vulnerabilities']}")
        print(f"  False positive rate: {summary['false_positive_rate']:.1%}")
        print(f"  Critical: {summary['by_severity']['CRITICAL']}")
        print(f"  High: {summary['by_severity']['HIGH']}")
        print(f"  Medium: {summary['by_severity']['MEDIUM']}")
        print(f"  Low: {summary['by_severity']['LOW']}")
        
        # Exit with error code if blocking severities found
        blocking_severities = engine.policy.blocking_severities
        has_blocking = any(
            summary['by_severity'].get(sev, 0) > 0 
            for sev in blocking_severities
        )
        
        if has_blocking:
            print(f"\n❌ Blocking severities found: {blocking_severities}")
            sys.exit(1)
        else:
            print(f"\n✅ No blocking vulnerabilities found")
            sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
