"""Integration module to add scoring system to existing SEO checks"""
from typing import List, Dict, Any
from .analytics_scoring import analyze_seo_results


def generate_seo_report_with_scoring(check_results: List[Dict[str, Any]], 
                                     website_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Complete SEO analysis with scoring system
    
    Usage:
        from seo_engine import run_all_comprehensive_checks
        from seo_engine.scoring_integration import generate_seo_report_with_scoring
        
        pages = crawl_website(url)
        check_results = run_all_comprehensive_checks(pages)
        report = generate_seo_report_with_scoring(check_results, website_data)
        
        print(f"SEO Score: {report['analytics']['overall_score']}/100")
        print(f"Grade: {report['analytics']['grade']}")
    """
    # Run analytics
    analytics = analyze_seo_results(check_results)
    
    return {
        'website_data': website_data or {},
        'total_pages_analyzed': website_data.get('total_pages', 0) if website_data else 0,
        'checks': check_results,
        'analytics': analytics,
        'summary': analytics['executive_summary']
    }


def format_for_api_response(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the report for clean API responses or UI display
    """
    analytics = report['analytics']
    
    return {
        'score': {
            'current': analytics['overall_score'],
            'potential': analytics['potential_score'],
            'grade': analytics['grade'],
            'improvement_available': analytics['score_gap']
        },
        'summary': {
            'interpretation': analytics['interpretation'],
            'total_checks': analytics['total_checks'],
            'passed': analytics['status_distribution']['passed'],
            'warnings': analytics['status_distribution']['warnings'],
            'failed': analytics['status_distribution']['failed'],
            'info': analytics['status_distribution']['info']
        },
        'categories': [
            {
                'name': cat['category'],
                'score': cat['percentage'],
                'checks_total': cat['total_checks'],
                'checks_passed': cat['passed'],
                'checks_failed': cat['failed'],
                'checks_warning': cat['warnings']
            }
            for cat in analytics['category_scores']
        ],
        'priorities': {
            'critical_issues': analytics['critical_issues'][:5],  # Top 5
            'quick_wins': analytics['quick_wins'][:5],  # Top 5
            'roadmap': analytics['priority_roadmap'][:10]  # Top 10
        },
        'detailed_checks': report['checks']
    }


def get_score_visualization(score: float) -> str:
    """
    Generate a visual progress bar for the score
    
    Returns ASCII/Unicode progress bar
    """
    filled = int(score / 10)
    empty = 10 - filled
    
    bar = "█" * filled + "░" * empty
    
    return f"[{bar}] {score}/100"


def get_score_color_class(score: float) -> str:
    """
    Get CSS color class based on score for UI display
    """
    if score >= 90:
        return "text-green-600"  # Excellent
    elif score >= 80:
        return "text-green-500"  # Very Good
    elif score >= 70:
        return "text-blue-500"   # Good
    elif score >= 60:
        return "text-yellow-500" # Fair
    elif score >= 50:
        return "text-orange-500" # Poor
    else:
        return "text-red-600"    # Critical


def generate_dashboard_summary(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a concise dashboard summary for quick overview
    """
    analytics = report['analytics']
    
    # Calculate category health
    category_health = {}
    for cat in analytics['category_scores']:
        score = cat['percentage']
        if score >= 80:
            health = "healthy"
        elif score >= 60:
            health = "needs_attention"
        else:
            health = "critical"
        category_health[cat['category']] = health
    
    # Identify biggest opportunity
    biggest_opportunity = None
    max_impact = 0
    for issue in analytics['critical_issues']:
        if issue['impact_score'] > max_impact:
            max_impact = issue['impact_score']
            biggest_opportunity = issue
    
    return {
        'overall': {
            'score': analytics['overall_score'],
            'grade': analytics['grade'],
            'visual': get_score_visualization(analytics['overall_score']),
            'color': get_score_color_class(analytics['overall_score'])
        },
        'health_indicators': {
            'passed_percentage': round(
                analytics['status_distribution']['passed'] / 
                analytics['total_checks'] * 100, 1
            ),
            'critical_issues_count': analytics['status_distribution']['failed'],
            'warnings_count': analytics['status_distribution']['warnings']
        },
        'category_health': category_health,
        'biggest_opportunity': biggest_opportunity,
        'estimated_traffic_impact': estimate_traffic_impact(
            analytics['overall_score'],
            analytics['potential_score']
        )
    }


def estimate_traffic_impact(current_score: float, potential_score: float) -> Dict[str, Any]:
    """
    Estimate potential traffic improvement based on score increase
    
    This is a rough estimate based on industry benchmarks
    """
    score_improvement = potential_score - current_score
    
    # Rough estimate: Each 10 points = ~15-25% traffic increase
    estimated_increase_low = score_improvement * 1.5
    estimated_increase_high = score_improvement * 2.5
    
    return {
        'score_improvement': round(score_improvement, 1),
        'estimated_traffic_increase': f"{estimated_increase_low:.0f}-{estimated_increase_high:.0f}%",
        'explanation': f"Fixing these issues could increase organic traffic by {estimated_increase_low:.0f}-{estimated_increase_high:.0f}%"
    }
