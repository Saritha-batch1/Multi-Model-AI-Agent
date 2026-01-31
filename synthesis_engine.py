"""
Findings Synthesis Engine
Aggregates results from all analysis models into a coherent summary.
"""
from typing import List, Dict, Any

class FindingsSynthesizer:
    def __init__(self):
        self.priority_keywords = {
            'high': ['critical', 'severe', 'emergency', 'urgent', 'high risk', 'danger', 'immediate'],
            'medium': ['warning', 'moderate', 'elevated', 'attention', 'consult', 'possible', 'potential'],
            'low': ['normal', 'good', 'healthy', 'optimal', 'within range', 'stable']
        }
        
        self.conflict_rules = {
            'anemia_infection': {
                'triggers': ['anemia', 'infection', 'inflammatory'],
                'resolution': 'Consider both conditions independently'
            },
            'glucose_cholesterol': {
                'triggers': ['glucose', 'diabetes', 'cholesterol', 'metabolic'],
                'resolution': 'Metabolic syndrome pattern requires comprehensive management'
            }
        }
    
    def synthesize_findings(self, 
                           parameter_results: List[str],
                           pattern_results: List[str],
                           context_results: List[str] = None) -> Dict[str, Any]:
        """
        Combine findings from all three AI models into a coherent summary
        """
        # Combine all findings
        all_findings = parameter_results.copy()
        all_findings.extend(pattern_results)
        if context_results:
            all_findings.extend(context_results)
        
        # Remove duplicates while preserving order
        unique_findings = []
        for finding in all_findings:
            if finding not in unique_findings:
                unique_findings.append(finding)
        
        # Categorize findings by priority
        categorized = self._categorize_by_priority(unique_findings)
        
        # Check for and resolve contradictions
        resolved_findings = self._resolve_contradictions(categorized)
        
        # Generate summary
        summary = self._generate_summary(resolved_findings)
        
        # Extract key patterns
        key_patterns = self._extract_key_patterns(resolved_findings)
        
        # Prioritize findings (most important first)
        prioritized_findings = self._prioritize_findings(resolved_findings)
        
        return {
            'all_findings': prioritized_findings,
            'summary': summary,
            'key_patterns': key_patterns,
            'priority_level': self._determine_overall_priority(resolved_findings),
            'contradictions_resolved': len(all_findings) - len(unique_findings),
            'total_insights': len(prioritized_findings)
        }
    
    def _categorize_by_priority(self, findings: List[str]) -> Dict[str, List[str]]:
        """Categorize findings by priority level"""
        categorized = {'high': [], 'medium': [], 'low': [], 'neutral': []}
        
        for finding in findings:
            finding_lower = finding.lower()
            priority_assigned = False
            
            # Check for high priority keywords
            for keyword in self.priority_keywords['high']:
                if keyword in finding_lower:
                    categorized['high'].append(finding)
                    priority_assigned = True
                    break
            
            if not priority_assigned:
                for keyword in self.priority_keywords['medium']:
                    if keyword in finding_lower:
                        categorized['medium'].append(finding)
                        priority_assigned = True
                        break
            
            if not priority_assigned:
                for keyword in self.priority_keywords['low']:
                    if keyword in finding_lower:
                        categorized['low'].append(finding)
                        priority_assigned = True
                        break
            
            if not priority_assigned:
                categorized['neutral'].append(finding)
        
        return categorized
    
    def _resolve_contradictions(self, categorized_findings: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Identify and resolve contradictory findings"""
        all_findings = []
        all_findings.extend(categorized_findings['high'])
        all_findings.extend(categorized_findings['medium'])
        all_findings.extend(categorized_findings['low'])
        all_findings.extend(categorized_findings['neutral'])
        
        resolved = categorized_findings.copy()
        findings_text = ' '.join(all_findings).lower()
        
        # Check for specific conflict patterns
        for conflict_name, rules in self.conflict_rules.items():
            trigger_count = 0
            for trigger in rules['triggers']:
                if trigger in findings_text:
                    trigger_count += 1
            
            # If multiple triggers from same conflict group found
            if trigger_count >= 2:
                # Add resolution note to findings
                resolved['medium'].append(f"Note: {rules['resolution']}")
        
        return resolved
    
    def _generate_summary(self, categorized_findings: Dict[str, List[str]]) -> str:
        """Generate a concise summary of all findings"""
        high_count = len(categorized_findings['high'])
        medium_count = len(categorized_findings['medium'])
        low_count = len(categorized_findings['low'])
        neutral_count = len(categorized_findings['neutral'])
        
        total = high_count + medium_count + low_count + neutral_count
        
        if total == 0:
            return "No significant findings detected."
        
        if high_count > 0:
            summary = f"{high_count} high-priority finding(s) require immediate attention. "
        elif medium_count > 0:
            summary = f"{medium_count} finding(s) need monitoring and follow-up. "
        else:
            summary = "All parameters are within normal ranges. "
        
        # Add pattern-based insights
        findings_text = ' '.join(categorized_findings['high'] + categorized_findings['medium']).lower()
        
        if 'anemia' in findings_text or 'hemoglobin' in findings_text:
            summary += "Blood-related patterns detected. "
        
        if ('glucose' in findings_text or 'diabetes' in findings_text) and \
           ('cholesterol' in findings_text or 'lipid' in findings_text):
            summary += "Metabolic pattern requires comprehensive management. "
        
        summary += f"Total insights: {total}."
        return summary
    
    def _extract_key_patterns(self, categorized_findings: Dict[str, List[str]]) -> List[str]:
        """Extract key patterns from findings"""
        all_findings = []
        all_findings.extend(categorized_findings['high'])
        all_findings.extend(categorized_findings['medium'])
        
        patterns = []
        findings_text = ' '.join(all_findings).lower()
        
        # Check for anemia patterns
        anemia_indicators = ['hemoglobin', 'anemia', 'low hb', 'low hemoglobin']
        if any(indicator in findings_text for indicator in anemia_indicators):
            patterns.append("Blood disorder pattern")
        
        # Check for infection/inflammation patterns
        infection_indicators = ['wbc', 'infection', 'inflammatory', 'white blood']
        if any(indicator in findings_text for indicator in infection_indicators):
            patterns.append("Infection/Inflammation pattern")
        
        # Check for metabolic syndrome patterns
        metabolic_indicators = ['glucose', 'cholesterol', 'triglyceride', 'metabolic', 'diabetes']
        metabolic_count = sum(1 for indicator in metabolic_indicators if indicator in findings_text)
        if metabolic_count >= 2:
            patterns.append("Metabolic syndrome pattern")
        
        return patterns
    
    def _prioritize_findings(self, categorized_findings: Dict[str, List[str]]) -> List[str]:
        """Order findings by priority (high → medium → low → neutral)"""
        prioritized = []
        
        # Add in priority order
        prioritized.extend(categorized_findings['high'])
        prioritized.extend(categorized_findings['medium'])
        prioritized.extend(categorized_findings['low'])
        prioritized.extend(categorized_findings['neutral'])
        
        return prioritized
    
    def _determine_overall_priority(self, categorized_findings: Dict[str, List[str]]) -> str:
        """Determine overall priority level for the report"""
        if len(categorized_findings['high']) > 0:
            return "High - Requires immediate medical attention"
        elif len(categorized_findings['medium']) > 0:
            return "Medium - Medical follow-up recommended"
        elif len(categorized_findings['low']) > 0:
            return "Low - Lifestyle monitoring advised"
        else:
            return "Normal - Continue healthy practices"

# Example usage
if __name__ == "__main__":
    synthesizer = FindingsSynthesizer()
    
    # Test data
    test_parameter = ["Low Hemoglobin - Possible Anemia", "WBC Count: Normal range"]
    test_pattern = ["Metabolic pattern detected"]
    test_context = ["Age > 50: Increased monitoring recommended"]
    
    result = synthesizer.synthesize_findings(test_parameter, test_pattern, test_context)
    print("Synthesis Test Result:", result)