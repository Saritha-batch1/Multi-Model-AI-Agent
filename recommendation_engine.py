"""
Personalized Recommendation Generator
Creates actionable advice based on findings and user context.
"""
from typing import List, Dict, Any

class RecommendationGenerator:
    def __init__(self):
        # Knowledge base of recommendations linked to conditions
        self.recommendation_knowledge_base = {
            'anemia': {
                'diet': [
                    "Increase iron-rich foods: spinach, lentils, red meat, tofu",
                    "Consume vitamin C with iron meals to enhance absorption",
                    "Include folate sources: leafy greens, beans, fortified grains"
                ],
                'lifestyle': [
                    "Rest adequately - anemia can cause fatigue",
                    "Avoid tea/coffee with meals (inhibits iron absorption)",
                    "Consider iron supplements under medical guidance"
                ],
                'medical': [
                    "Consult hematologist for complete blood work",
                    "Check ferritin and transferrin saturation levels",
                    "Rule out internal bleeding if anemia is severe"
                ]
            },
            'diabetes_glucose': {
                'diet': [
                    "Follow low-glycemic diet: whole grains, vegetables, lean proteins",
                    "Limit simple sugars and refined carbohydrates",
                    "Eat smaller, frequent meals to stabilize blood sugar"
                ],
                'lifestyle': [
                    "Exercise 30 minutes daily (walking, swimming, cycling)",
                    "Monitor blood glucose regularly if prescribed",
                    "Maintain healthy weight through balanced diet"
                ],
                'medical': [
                    "Consult endocrinologist for proper diagnosis",
                    "Get HbA1c test for 3-month glucose average",
                    "Regular foot and eye exams (diabetes complications)"
                ]
            },
            'cholesterol_lipid': {
                'diet': [
                    "Reduce saturated fats (red meat, full-fat dairy)",
                    "Increase soluble fiber (oats, beans, apples, carrots)",
                    "Include omega-3 sources (fatty fish, walnuts, flaxseeds)"
                ],
                'lifestyle': [
                    "Aerobic exercise 150 minutes per week",
                    "Quit smoking if applicable",
                    "Limit alcohol consumption"
                ],
                'medical': [
                    "Consult cardiologist for cardiovascular risk assessment",
                    "Consider statin therapy if lifestyle changes insufficient",
                    "Monitor blood pressure regularly"
                ]
            },
            'infection_inflammation': {
                'diet': [
                    "Increase anti-inflammatory foods: turmeric, ginger, berries",
                    "Stay well-hydrated with water and herbal teas",
                    "Consume probiotic foods: yogurt, kefir, fermented foods"
                ],
                'lifestyle': [
                    "Get adequate rest for immune system recovery",
                    "Practice good hygiene and handwashing",
                    "Avoid crowded places if immune-compromised"
                ],
                'medical': [
                    "Consult primary care physician for antibiotic evaluation",
                    "Complete full course if antibiotics prescribed",
                    "Monitor temperature and symptoms daily"
                ]
            },
            'general_health': {
                'diet': [
                    "Eat balanced diet with 5+ servings of fruits/vegetables daily",
                    "Stay hydrated with 8+ glasses of water daily",
                    "Limit processed foods and added sugars"
                ],
                'lifestyle': [
                    "Aim for 7-9 hours of quality sleep nightly",
                    "Manage stress through meditation, yoga, or hobbies",
                    "Avoid smoking and limit alcohol to moderate levels"
                ],
                'medical': [
                    "Schedule annual physical examination",
                    "Keep vaccinations up to date",
                    "Maintain personal health record"
                ]
            }
        }
        
        # Age-specific adjustments
        self.age_adjustments = {
            'pediatric': (0, 18),
            'young_adult': (19, 35),
            'middle_age': (36, 50),
            'older_adult': (51, 65),
            'senior': (66, 120)
        }
        
        # Gender-specific considerations
        self.gender_considerations = {
            'female': [
                "Consider menstrual blood loss in anemia assessment",
                "Post-menopausal women have increased cardiovascular risk",
                "Pregnancy requires special nutritional considerations"
            ],
            'male': [
                "Men typically have higher cardiovascular risk at younger ages",
                "Prostate health screening recommended from age 50",
                "Testosterone levels may affect energy and metabolism"
            ]
        }
    
    def generate_recommendations(self,
                               findings: List[str],
                               user_context: Dict[str, Any],
                               synthesized_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized recommendations based on findings and context
        """
        # Extract user context
        age = user_context.get('age', 30)
        gender = user_context.get('gender', 'unspecified')
        
        # Detect conditions from findings
        detected_conditions = self._detect_conditions(findings, synthesized_report)
        
        # Generate recommendations for each condition
        condition_recommendations = {}
        for condition in detected_conditions:
            condition_recommendations[condition] = self._get_condition_recommendations(
                condition, age, gender
            )
        
        # Add general health recommendations
        condition_recommendations['general_health'] = self._get_condition_recommendations(
            'general_health', age, gender
        )
        
        # Personalize based on age
        age_group = self._determine_age_group(age)
        age_specific_recs = self._get_age_specific_recommendations(age_group, detected_conditions)
        
        # Personalize based on gender
        gender_specific_recs = []
        if gender in self.gender_considerations:
            gender_specific_recs = self.gender_considerations[gender]
        
        # Link recommendations to specific findings
        linked_recommendations = self._link_to_findings(
            condition_recommendations, findings, detected_conditions
        )
        
        # Prioritize recommendations
        prioritized_recs = self._prioritize_recommendations(linked_recommendations)
        
        # Generate actionable steps
        action_plan = self._create_action_plan(prioritized_recs, age, gender)
        
        return {
            'detected_conditions': detected_conditions,
            'condition_recommendations': condition_recommendations,
            'age_specific': age_specific_recs,
            'gender_specific': gender_specific_recs,
            'linked_recommendations': linked_recommendations,
            'prioritized_recommendations': prioritized_recs,
            'action_plan': action_plan,
            'personalization_factors': {
                'age': age,
                'age_group': age_group,
                'gender': gender
            }
        }
    
    def _detect_conditions(self, findings: List[str], synthesized_report: Dict[str, Any]) -> List[str]:
        """Detect medical conditions from findings"""
        findings_text = ' '.join(findings).lower()
        key_patterns = [p.lower() for p in synthesized_report.get('key_patterns', [])]
        
        detected = []
        
        # Check each condition
        condition_indicators = {
            'anemia': ['anemia', 'low hemoglobin', 'low hb', 'iron deficiency'],
            'diabetes_glucose': ['glucose', 'diabetes', 'blood sugar', 'hyperglycemi'],
            'cholesterol_lipid': ['cholesterol', 'lipid', 'hdl', 'ldl', 'triglyceride'],
            'infection_inflammation': ['infection', 'wbc', 'white blood', 'inflammatory']
        }
        
        for condition, indicators in condition_indicators.items():
            for indicator in indicators:
                if indicator in findings_text:
                    detected.append(condition)
                    break
        
        # Also check key patterns
        for pattern in key_patterns:
            if 'blood disorder' in pattern and 'anemia' not in detected:
                detected.append('anemia')
            elif 'metabolic' in pattern:
                if 'diabetes_glucose' not in detected:
                    detected.append('diabetes_glucose')
                if 'cholesterol_lipid' not in detected:
                    detected.append('cholesterol_lipid')
            elif 'infection' in pattern and 'infection_inflammation' not in detected:
                detected.append('infection_inflammation')
        
        return list(set(detected))
    
    def _get_condition_recommendations(self, condition: str, age: int, gender: str) -> Dict[str, List[str]]:
        """Get recommendations for a specific condition with age/gender adjustments"""
        if condition not in self.recommendation_knowledge_base:
            return {}
        
        base_recs = {}
        for category, recs in self.recommendation_knowledge_base[condition].items():
            base_recs[category] = recs.copy()
        
        # Age adjustments
        if age < 18 and condition == 'general_health':
            base_recs['lifestyle'] = [
                "Ensure 9-12 hours of sleep for growth and development",
                "Limit screen time to 2 hours daily",
                "Participate in 60 minutes of physical activity daily"
            ]
        elif age > 50:
            if condition in ['cholesterol_lipid', 'diabetes_glucose']:
                base_recs['medical'].append("Annual cardiovascular risk assessment recommended")
            if condition == 'general_health':
                base_recs['medical'].append("Regular bone density and vision checks")
        
        # Gender adjustments
        if gender == 'female' and condition == 'anemia':
            base_recs['diet'].append("Iron needs are higher during menstruation - monitor intake")
        elif gender == 'male' and condition == 'cholesterol_lipid':
            base_recs['medical'].append("Men should monitor cholesterol from age 35")
        
        return base_recs
    
    def _determine_age_group(self, age: int) -> str:
        """Determine which age group the user belongs to"""
        for group, (min_age, max_age) in self.age_adjustments.items():
            if min_age <= age <= max_age:
                return group
        return 'older_adult'
    
    def _get_age_specific_recommendations(self, age_group: str, conditions: List[str]) -> List[str]:
        """Get age-specific recommendations"""
        recommendations = []
        
        if age_group == 'pediatric':
            recommendations.append("Pediatrician consultation for abnormal findings")
        
        elif age_group == 'young_adult':
            recommendations.append("Establish healthy lifestyle habits early")
        
        elif age_group == 'middle_age':
            recommendations.append("Annual comprehensive health checkup recommended")
            if any(c in conditions for c in ['diabetes_glucose', 'cholesterol_lipid']):
                recommendations.append("Metabolic screening every 6-12 months")
        
        elif age_group in ['older_adult', 'senior']:
            recommendations.append("Bone density screening recommended")
            recommendations.append("Annual vision and hearing checks")
        
        return recommendations
    
    def _link_to_findings(self, 
                         recommendations: Dict[str, Dict[str, List[str]]], 
                         findings: List[str],
                         conditions: List[str]) -> List[Dict[str, Any]]:
        """Link each recommendation to specific findings that support it"""
        linked = []
        
        for condition, rec_categories in recommendations.items():
            for category, rec_list in rec_categories.items():
                for recommendation in rec_list:
                    # Find which findings support this recommendation
                    supporting_findings = []
                    
                    for finding in findings:
                        finding_lower = finding.lower()
                        rec_lower = recommendation.lower()
                        
                        # Simple keyword matching
                        common_terms = {
                            'anemia': ['iron', 'hemoglobin', 'anemia'],
                            'diabetes_glucose': ['glucose', 'sugar', 'diabetes'],
                            'cholesterol_lipid': ['cholesterol', 'lipid', 'fat'],
                            'infection_inflammation': ['infection', 'wbc', 'inflammatory']
                        }
                        
                        if condition in common_terms:
                            for term in common_terms[condition]:
                                if term in finding_lower and term in rec_lower:
                                    supporting_findings.append(finding)
                                    break
                    
                    # If no specific finding matched, use condition as basis
                    if not supporting_findings and condition in conditions:
                        supporting_findings.append(f"Based on {condition.replace('_', ' ')} pattern")
                    
                    linked.append({
                        'recommendation': recommendation,
                        'category': category,
                        'condition': condition,
                        'supporting_findings': supporting_findings[:3],
                        'evidence_based': len(supporting_findings) > 0
                    })
        
        return linked
    
    def _prioritize_recommendations(self, linked_recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on urgency and impact"""
        # Define priority scores
        category_priority = {'medical': 3, 'lifestyle': 2, 'diet': 1}
        condition_priority = {
            'anemia': 3, 'diabetes_glucose': 3, 'infection_inflammation': 3,
            'cholesterol_lipid': 2, 'general_health': 1
        }
        
        # Score each recommendation
        for rec in linked_recommendations:
            score = 0
            score += category_priority.get(rec['category'], 1)
            score += condition_priority.get(rec['condition'], 1)
            score += len(rec['supporting_findings']) * 0.5
            if rec['evidence_based']:
                score += 1
            
            rec['priority_score'] = score
        
        # Sort by priority score (descending)
        linked_recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Assign priority labels
        for i, rec in enumerate(linked_recommendations):
            if i < 3:
                rec['priority_label'] = 'High Priority'
            elif i < 8:
                rec['priority_label'] = 'Medium Priority'
            else:
                rec['priority_label'] = 'General Advice'
        
        return linked_recommendations
    
    def _create_action_plan(self, 
                           prioritized_recs: List[Dict[str, Any]], 
                           age: int, 
                           gender: str) -> Dict[str, Any]:
        """Create an actionable plan with timeline"""
        action_plan = {
            'immediate_actions': [],
            'this_week_actions': [],
            'this_month_actions': [],
            'long_term_actions': []
        }
        
        # Categorize recommendations by timeline
        for i, rec in enumerate(prioritized_recs[:12]):
            if i < 3 and rec['category'] == 'medical':
                action_plan['immediate_actions'].append({
                    'action': rec['recommendation'],
                    'reason': f"Based on: {', '.join(rec['supporting_findings'][:2]) or rec['condition'].replace('_', ' ')}",
                    'estimated_time': '1-2 days'
                })
            elif i < 8:
                action_plan['this_week_actions'].append({
                    'action': rec['recommendation'],
                    'reason': f"Addresses: {rec['condition'].replace('_', ' ')}",
                    'estimated_time': '1-2 weeks'
                })
            elif rec['category'] == 'lifestyle':
                action_plan['this_month_actions'].append({
                    'action': rec['recommendation'],
                    'reason': "Lifestyle modification for long-term health",
                    'estimated_time': '1 month'
                })
            else:
                action_plan['long_term_actions'].append({
                    'action': rec['recommendation'],
                    'reason': "Ongoing health maintenance",
                    'estimated_time': 'Ongoing'
                })
        
        return action_plan

# Example usage
if __name__ == "__main__":
    generator = RecommendationGenerator()
    
    # Test data
    test_findings = ["Low Hemoglobin - Possible Anemia", "Elevated Blood Glucose"]
    test_context = {'age': 45, 'gender': 'male'}
    test_synthesized = {'key_patterns': ['Metabolic syndrome pattern'], 'priority_level': 'Medium'}
    
    result = generator.generate_recommendations(test_findings, test_context, test_synthesized)
    print("Recommendation Test Result:", result['detected_conditions'])