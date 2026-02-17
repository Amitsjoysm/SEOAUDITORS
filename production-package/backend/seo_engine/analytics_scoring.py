"""Enhanced SEO Analytics Scoring System
Provides cumulative scores out of 100 based on real-world SEO importance
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    INFO = "info"


@dataclass
class CategoryWeights:
    """Real-world SEO importance weights for each category
    Based on industry research and ranking factor studies
    """
    # Total must equal 100 - Adjusted for maximum real-world impact
    TECHNICAL_SEO = 22          # Increased: Critical for crawling/indexing
    PERFORMANCE = 20            # Increased: Core Web Vitals = direct ranking factor
    ON_PAGE_SEO = 25            # Maintained: Most direct ranking impact
    CONTENT_QUALITY = 16        # Increased: E-E-A-T and relevance crucial
    OFF_PAGE_SEO = 10           # Decreased: Still matters but less than before
    ANALYTICS = 2               # Decreased: Tracking, not ranking
    SOCIAL_MEDIA = 1            # Decreased: Very indirect impact
    GEO_AEO = 2                 # Decreased: Growing but still niche
    ADVANCED_TECHNICAL = 2      # Maintained: Nice-to-have optimizations


class SEOScoreCalculator:
    """Calculate comprehensive SEO scores based on check results"""
    
    def __init__(self):
        self.weights = CategoryWeights()
        self.category_map = {
            "Technical SEO": self.weights.TECHNICAL_SEO,
            "Performance": self.weights.PERFORMANCE,
            "Performance & Core Web Vitals": self.weights.PERFORMANCE,
            "On-Page SEO": self.weights.ON_PAGE_SEO,
            "Content Quality": self.weights.CONTENT_QUALITY,
            "Off-Page SEO": self.weights.OFF_PAGE_SEO,
            "Analytics & Reporting": self.weights.ANALYTICS,
            "Social Media": self.weights.SOCIAL_MEDIA,
            "GEO & AEO": self.weights.GEO_AEO,
            "Advanced Technical": self.weights.ADVANCED_TECHNICAL,
            "Advanced Security": self.weights.ADVANCED_TECHNICAL,
            "Advanced Accessibility": self.weights.ADVANCED_TECHNICAL,
            "Advanced Performance": self.weights.PERFORMANCE,
            "Advanced Analytics": self.weights.ANALYTICS,
        }
    
    def calculate_check_score(self, check: Dict[str, Any]) -> float:
        """
        Calculate individual check score (0-100)
        
        Scoring logic:
        - PASS: 100% of impact_score
        - WARNING: 50% of impact_score
        - FAIL: 0% of impact_score
        - INFO: 75% of impact_score (not applicable/needs external data)
        """
        impact = check.get('impact_score', 50)
        status = check.get('status', 'info').lower()
        
        multipliers = {
            'pass': 1.0,
            'warning': 0.5,
            'fail': 0.0,
            'info': 0.75  # Partial credit for checks needing external data
        }
        
        multiplier = multipliers.get(status, 0.5)
        return impact * multiplier
    
    def calculate_category_score(self, checks: List[Dict[str, Any]], 
                                 category: str) -> Dict[str, Any]:
        """Calculate score for a specific category"""
        category_checks = [c for c in checks if c.get('category') == category]
        
        if not category_checks:
            return {
                'category': category,
                'score': 0,
                'max_score': 0,
                'percentage': 0,
                'total_checks': 0,
                'passed': 0,
                'warnings': 0,
                'failed': 0,
                'info': 0
            }
        
        # Calculate scores
        total_impact = sum(c.get('impact_score', 50) for c in category_checks)
        earned_score = sum(self.calculate_check_score(c) for c in category_checks)
        
        # Count statuses
        status_counts = {
            'passed': sum(1 for c in category_checks if c.get('status') == 'pass'),
            'warnings': sum(1 for c in category_checks if c.get('status') == 'warning'),
            'failed': sum(1 for c in category_checks if c.get('status') == 'fail'),
            'info': sum(1 for c in category_checks if c.get('status') == 'info'),
        }
        
        percentage = (earned_score / total_impact * 100) if total_impact > 0 else 0
        
        return {
            'category': category,
            'score': round(earned_score, 2),
            'max_score': total_impact,
            'percentage': round(percentage, 2),
            'total_checks': len(category_checks),
            **status_counts,
            'checks': category_checks
        }
    
    def calculate_weighted_score(self, category_scores: List[Dict[str, Any]]) -> float:
        """Calculate overall weighted score out of 100"""
        weighted_total = 0
        
        for cat_score in category_scores:
            category = cat_score['category']
            weight = self.category_map.get(category, 1)
            percentage = cat_score['percentage']
            
            # Weighted contribution: (category_percentage * category_weight) / 100
            weighted_total += (percentage * weight) / 100
        
        return round(weighted_total, 2)
    
    def get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        elif score >= 45:
            return "D+"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    def get_score_interpretation(self, score: float) -> str:
        """Provide interpretation of the score"""
        if score >= 90:
            return "Excellent! Your SEO is highly optimized."
        elif score >= 80:
            return "Very Good. Strong SEO foundation with minor improvements needed."
        elif score >= 70:
            return "Good. Solid SEO but several optimization opportunities exist."
        elif score >= 60:
            return "Fair. Significant SEO improvements needed to compete effectively."
        elif score >= 50:
            return "Poor. Major SEO issues requiring immediate attention."
        else:
            return "Critical. Severe SEO problems limiting your visibility."
    
    def calculate_comprehensive_score(self, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive SEO score with detailed breakdown
        
        Returns:
            Dictionary containing:
            - overall_score: Weighted score out of 100
            - grade: Letter grade (A+ to F)
            - interpretation: Human-readable assessment
            - category_scores: Detailed breakdown by category
            - critical_issues: List of failed checks
            - quick_wins: List of warning checks that are easy to fix
            - total_checks: Total number of checks run
        """
        # Calculate scores for each category
        categories = set(c.get('category') for c in checks)
        category_scores = [
            self.calculate_category_score(checks, cat) 
            for cat in categories
        ]
        
        # Sort by weight (importance)
        category_scores.sort(
            key=lambda x: self.category_map.get(x['category'], 0),
            reverse=True
        )
        
        # Calculate weighted overall score
        overall_score = self.calculate_weighted_score(category_scores)
        grade = self.get_grade(overall_score)
        interpretation = self.get_score_interpretation(overall_score)
        
        # Identify critical issues (failed checks with high impact)
        critical_issues = sorted(
            [c for c in checks if c.get('status') == 'fail'],
            key=lambda x: x.get('impact_score', 0),
            reverse=True
        )[:10]  # Top 10 critical issues
        
        # Identify quick wins (warnings with high impact, easier to fix)
        quick_wins = sorted(
            [c for c in checks if c.get('status') == 'warning'],
            key=lambda x: x.get('impact_score', 0),
            reverse=True
        )[:10]  # Top 10 quick wins
        
        # Calculate status distribution
        total_checks = len(checks)
        status_distribution = {
            'passed': sum(1 for c in checks if c.get('status') == 'pass'),
            'warnings': sum(1 for c in checks if c.get('status') == 'warning'),
            'failed': sum(1 for c in checks if c.get('status') == 'fail'),
            'info': sum(1 for c in checks if c.get('status') == 'info'),
        }
        
        # Calculate potential score (if all warnings and fails were fixed)
        potential_score = self._calculate_potential_score(checks)
        score_gap = potential_score - overall_score
        
        return {
            'overall_score': overall_score,
            'potential_score': round(potential_score, 2),
            'score_gap': round(score_gap, 2),
            'grade': grade,
            'interpretation': interpretation,
            'category_scores': category_scores,
            'critical_issues': [
                {
                    'check_name': c['check_name'],
                    'category': c['category'],
                    'impact_score': c['impact_score'],
                    'ranking_impact': c.get('ranking_impact', ''),
                    'solution': c.get('solution', '')
                }
                for c in critical_issues
            ],
            'quick_wins': [
                {
                    'check_name': c['check_name'],
                    'category': c['category'],
                    'impact_score': c['impact_score'],
                    'solution': c.get('solution', '')
                }
                for c in quick_wins
            ],
            'total_checks': total_checks,
            'status_distribution': status_distribution,
            'status_percentages': {
                k: round(v / total_checks * 100, 1) 
                for k, v in status_distribution.items()
            }
        }
    
    def _calculate_potential_score(self, checks: List[Dict[str, Any]]) -> float:
        """Calculate potential score if all fixable issues were resolved"""
        potential_checks = []
        for check in checks:
            potential_check = check.copy()
            # Convert warnings and fails to pass (but keep info as-is)
            if check.get('status') in ['warning', 'fail']:
                potential_check['status'] = 'pass'
            potential_checks.append(potential_check)
        
        categories = set(c.get('category') for c in potential_checks)
        category_scores = [
            self.calculate_category_score(potential_checks, cat) 
            for cat in categories
        ]
        
        return self.calculate_weighted_score(category_scores)
    
    def generate_priority_roadmap(self, checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate prioritized SEO improvement roadmap
        
        Returns list of improvements sorted by:
        1. Impact score (higher first)
        2. Ease of fix (fails before warnings)
        3. Category weight
        """
        actionable_checks = [
            c for c in checks 
            if c.get('status') in ['fail', 'warning']
        ]
        
        def priority_score(check):
            impact = check.get('impact_score', 0)
            category_weight = self.category_map.get(check.get('category'), 1)
            status_multiplier = 2 if check.get('status') == 'fail' else 1
            
            return impact * category_weight * status_multiplier
        
        sorted_checks = sorted(
            actionable_checks,
            key=priority_score,
            reverse=True
        )
        
        roadmap = []
        for i, check in enumerate(sorted_checks[:20], 1):  # Top 20 priorities
            roadmap.append({
                'priority': i,
                'check_name': check['check_name'],
                'category': check['category'],
                'status': check['status'],
                'impact_score': check['impact_score'],
                'ranking_impact': check.get('ranking_impact', ''),
                'solution': check.get('solution', ''),
                'enhancements': check.get('enhancements', [])
            })
        
        return roadmap


def analyze_seo_results(check_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main function to analyze SEO check results and generate comprehensive report
    
    Args:
        check_results: List of check result dictionaries from run_all_comprehensive_checks()
    
    Returns:
        Complete SEO analysis with scores, grades, and recommendations
    """
    calculator = SEOScoreCalculator()
    
    # Calculate comprehensive score
    analysis = calculator.calculate_comprehensive_score(check_results)
    
    # Generate priority roadmap
    roadmap = calculator.generate_priority_roadmap(check_results)
    analysis['priority_roadmap'] = roadmap
    
    # Add executive summary
    analysis['executive_summary'] = {
        'total_score': f"{analysis['overall_score']}/100",
        'grade': analysis['grade'],
        'interpretation': analysis['interpretation'],
        'checks_passed': analysis['status_distribution']['passed'],
        'checks_failed': analysis['status_distribution']['failed'],
        'checks_warning': analysis['status_distribution']['warnings'],
        'potential_improvement': f"+{analysis['score_gap']} points available",
        'top_priority': roadmap[0]['check_name'] if roadmap else None
    }
    
    return analysis
