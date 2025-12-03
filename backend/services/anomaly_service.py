"""
Anomaly Detection Service
Automatically detects issues like traffic drops, ranking drops, performance degradation
Uses statistical analysis to identify significant deviations
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import statistics

from models import Audit, AnomalyDetection, AnomalyType, AnomalySeverity

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detects anomalies in SEO metrics using statistical analysis
    """
    
    def __init__(self):
        self.deviation_threshold = 2.0  # Standard deviations
    
    async def detect_all_anomalies(
        self,
        audit_id: str,
        user_id: str,
        current_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]],
        db: AsyncSession
    ) -> List[AnomalyDetection]:
        """
        Detect all types of anomalies
        
        Args:
            audit_id: Current audit ID
            user_id: User ID
            current_data: Current audit data
            historical_data: List of previous audit data
            db: Database session
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Need at least 3 historical data points for statistical analysis
        if len(historical_data) < 3:
            logger.info("Not enough historical data for anomaly detection")
            return anomalies
        
        # Detect performance anomalies
        perf_anomalies = await self._detect_performance_anomalies(
            audit_id, user_id, current_data, historical_data, db
        )
        anomalies.extend(perf_anomalies)
        
        # Detect ranking anomalies
        ranking_anomalies = await self._detect_ranking_anomalies(
            audit_id, user_id, current_data, historical_data, db
        )
        anomalies.extend(ranking_anomalies)
        
        # Detect score anomalies
        score_anomalies = await self._detect_score_anomalies(
            audit_id, user_id, current_data, historical_data, db
        )
        anomalies.extend(score_anomalies)
        
        logger.info(f"Detected {len(anomalies)} anomalies for audit {audit_id}")
        
        return anomalies
    
    async def _detect_performance_anomalies(
        self,
        audit_id: str,
        user_id: str,
        current_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]],
        db: AsyncSession
    ) -> List[AnomalyDetection]:
        """Detect performance degradation"""
        anomalies = []
        
        try:
            # Get Lighthouse performance scores
            current_lighthouse = current_data.get('lighthouse_data', {})
            current_perf = current_lighthouse.get('performance_score')
            
            if current_perf is None:
                return anomalies
            
            # Get historical performance scores
            historical_scores = []
            for hist in historical_data:
                lighthouse = hist.get('lighthouse_data', {})
                score = lighthouse.get('performance_score')
                if score is not None:
                    historical_scores.append(score)
            
            if len(historical_scores) < 3:
                return anomalies
            
            # Calculate statistics
            mean = statistics.mean(historical_scores)
            stdev = statistics.stdev(historical_scores) if len(historical_scores) > 1 else 0
            
            # Check for significant degradation
            if stdev > 0:
                z_score = (current_perf - mean) / stdev
                
                if z_score < -self.deviation_threshold:
                    # Significant performance drop
                    severity = self._calculate_severity(abs(z_score))
                    deviation_pct = ((current_perf - mean) / mean) * 100
                    
                    anomaly = AnomalyDetection(
                        audit_id=audit_id,
                        user_id=user_id,
                        anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                        severity=severity,
                        metric_name="lighthouse_performance_score",
                        expected_value=mean,
                        actual_value=current_perf,
                        deviation_percentage=abs(deviation_pct),
                        statistical_significance=abs(z_score),
                        impact_assessment=f"Performance score dropped from avg {mean:.1f} to {current_perf:.1f}",
                        root_cause_analysis="Possible causes: Increased page size, slow third-party scripts, server response time degradation, unoptimized images",
                        recommended_action="1. Run Lighthouse audit to identify bottlenecks\n2. Check Core Web Vitals (LCP, FID, CLS)\n3. Optimize images and lazy load resources\n4. Minimize JavaScript execution time"
                    )
                    
                    db.add(anomaly)
                    anomalies.append(anomaly)
        
        except Exception as e:
            logger.error(f"Error detecting performance anomalies: {e}")
        
        return anomalies
    
    async def _detect_ranking_anomalies(
        self,
        audit_id: str,
        user_id: str,
        current_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]],
        db: AsyncSession
    ) -> List[AnomalyDetection]:
        """Detect ranking drops"""
        anomalies = []
        
        # TODO: Implement when SERP data is available
        # Check for significant ranking position changes
        
        return anomalies
    
    async def _detect_score_anomalies(
        self,
        audit_id: str,
        user_id: str,
        current_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]],
        db: AsyncSession
    ) -> List[AnomalyDetection]:
        """Detect overall SEO score drops"""
        anomalies = []
        
        try:
            current_score = current_data.get('overall_score')
            
            if current_score is None:
                return anomalies
            
            # Get historical scores
            historical_scores = [
                hist.get('overall_score')
                for hist in historical_data
                if hist.get('overall_score') is not None
            ]
            
            if len(historical_scores) < 3:
                return anomalies
            
            # Calculate statistics
            mean = statistics.mean(historical_scores)
            stdev = statistics.stdev(historical_scores) if len(historical_scores) > 1 else 0
            
            # Check for significant drop (>10 points or >2 std deviations)
            score_drop = mean - current_score
            
            if score_drop > 10 or (stdev > 0 and score_drop / stdev > self.deviation_threshold):
                severity = AnomalySeverity.HIGH if score_drop > 20 else AnomalySeverity.MEDIUM
                deviation_pct = (score_drop / mean) * 100
                
                anomaly = AnomalyDetection(
                    audit_id=audit_id,
                    user_id=user_id,
                    anomaly_type=AnomalyType.RANKING_DROP,
                    severity=severity,
                    metric_name="overall_seo_score",
                    expected_value=mean,
                    actual_value=current_score,
                    deviation_percentage=abs(deviation_pct),
                    statistical_significance=score_drop / stdev if stdev > 0 else 0,
                    impact_assessment=f"SEO score dropped {score_drop:.1f} points from average {mean:.1f}",
                    root_cause_analysis="Check recent website changes, broken links, indexing issues, or technical SEO problems",
                    recommended_action="1. Review failed checks in audit report\n2. Check for recent website updates\n3. Verify robots.txt and sitemap\n4. Monitor Google Search Console for manual actions"
                )
                
                db.add(anomaly)
                anomalies.append(anomaly)
        
        except Exception as e:
            logger.error(f"Error detecting score anomalies: {e}")
        
        return anomalies
    
    def _calculate_severity(self, z_score: float) -> AnomalySeverity:
        """Calculate severity based on z-score"""
        if z_score >= 3.0:
            return AnomalySeverity.CRITICAL
        elif z_score >= 2.5:
            return AnomalySeverity.HIGH
        elif z_score >= 2.0:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    async def get_historical_audits(
        self,
        user_id: str,
        website_url: str,
        limit: int = 10,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical audits for the same website
        
        Args:
            user_id: User ID
            website_url: Website URL to match
            limit: Number of historical audits to retrieve
            db: Database session
        
        Returns:
            List of historical audit data
        """
        try:
            result = await db.execute(
                select(Audit)
                .where(
                    Audit.user_id == user_id,
                    Audit.website_url == website_url,
                    Audit.status == "completed"
                )
                .order_by(Audit.created_at.desc())
                .limit(limit)
            )
            audits = result.scalars().all()
            
            return [
                {
                    'overall_score': audit.overall_score,
                    'lighthouse_data': audit.lighthouse_data,
                    'serp_data': audit.serp_data,
                    'created_at': audit.created_at
                }
                for audit in audits
            ]
        
        except Exception as e:
            logger.error(f"Error getting historical audits: {e}")
            return []


# Global instance
anomaly_detector = AnomalyDetector()
