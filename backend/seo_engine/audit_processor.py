"""
Enhanced Audit Processing
Integrates enhanced orchestrator with 6 sub-agents and real API data
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Audit, AuditResult, AuditStatus, CheckStatus, CompetitorAnalysis, ContentOpportunity
from models import OpportunityType
from seo_engine import crawl_website, run_all_comprehensive_checks
from seo_engine.enhanced_orchestrator import enhanced_orchestrator
from seo_engine.scoring_integration import generate_seo_report_with_scoring
from services.integration_manager import api_manager
from services.anomaly_service import anomaly_detector
from models import APIServiceType

logger = logging.getLogger(__name__)


async def process_audit_enhanced(audit_id: str, website_url: str, max_pages: int, db: AsyncSession):
    """
    Enhanced audit processing with:
    - Real API data (DataForSEO, Lighthouse)
    - 6 AI sub-agents analysis
    - Competitor analysis
    - Content opportunities
    - Anomaly detection
    """
    try:
        # Get audit
        result = await db.execute(select(Audit).where(Audit.id == audit_id))
        audit = result.scalar_one()
        
        # ========================================================================
        # PHASE 1: CRAWLING
        # ========================================================================
        audit.status = AuditStatus.CRAWLING
        await db.commit()
        
        logger.info(f"🕷️ Starting enhanced crawl for {website_url}")
        start_time = datetime.now(timezone.utc)
        pages = await crawl_website(website_url, max_pages=max_pages)
        
        audit.pages_crawled = len(pages)
        audit.status = AuditStatus.ANALYZING
        
        # Prepare crawl data for orchestrator
        crawl_data = {
            'url': website_url,
            'total_pages': len(pages),
            'pages': pages,
            'crawl_time': sum(p.load_time for p in pages) if pages else 0,
            'avg_load_time': sum(p.load_time for p in pages) / len(pages) if pages else 0,
            'has_robots': any(p.url.endswith('/robots.txt') for p in pages),
            'has_sitemap': any(p.url.endswith('/sitemap.xml') for p in pages),
            'is_https': website_url.startswith('https://'),
            'has_blog': any('blog' in p.url.lower() for p in pages),
            'avg_word_count': sum(len(p.content.split()) for p in pages) / len(pages) if pages else 0
        }
        
        await db.commit()
        
        # ========================================================================
        # PHASE 2: RUN ENHANCED ORCHESTRATOR WITH SUB-AGENTS
        # ========================================================================
        logger.info(f"🤖 Running enhanced orchestrator with 6 sub-agents for audit {audit_id}")
        
        try:
            orchestrator_result = await enhanced_orchestrator.run_comprehensive_analysis(
                url=website_url,
                crawl_data=crawl_data,
                db=db
            )
            
            if orchestrator_result.get('success'):
                # Store API data in audit
                api_data = orchestrator_result.get('api_data', {})
                audit.lighthouse_data = api_data.get('lighthouse', {})
                audit.serp_data = api_data.get('serp', {})
                audit.backlink_data = api_data.get('backlinks', {})
                audit.keyword_data = api_data.get('keywords', {})
                
                # Record API successes
                if audit.lighthouse_data:
                    await api_manager.record_success(
                        db, APIServiceType.LIGHTHOUSE,
                        orchestrator_result.get('api_data', {}).get('lighthouse', {}).get('response_time_ms', 0)
                    )
                
                logger.info(f"✅ Orchestrator analysis completed in {orchestrator_result.get('execution_time_seconds')}s")
            else:
                logger.error(f"❌ Orchestrator failed: {orchestrator_result.get('error')}")
        
        except Exception as e:
            logger.error(f"Error in orchestrator: {e}")
            # Continue with standard checks even if orchestrator fails
        
        # ========================================================================
        # PHASE 3: RUN STANDARD SEO CHECKS
        # ========================================================================
        logger.info(f"🔍 Running 135+ comprehensive SEO checks for audit {audit_id}")
        check_results = run_all_comprehensive_checks(pages)
        
        # Generate scoring report
        website_data = {
            'url': website_url,
            'total_pages': len(pages),
            'crawl_time': crawl_data['crawl_time'],
            'avg_load_time': crawl_data['avg_load_time'],
            'lighthouse_score': audit.lighthouse_data.get('performance_score') if audit.lighthouse_data else None
        }
        scoring_report = generate_seo_report_with_scoring(check_results, website_data)
        analytics = scoring_report['analytics']
        
        # ========================================================================
        # PHASE 4: SAVE RESULTS TO DATABASE
        # ========================================================================
        logger.info(f"💾 Saving audit results to database")
        
        for check_result in check_results:
            result_obj = AuditResult(
                id=str(uuid.uuid4()),
                audit_id=audit_id,
                category=check_result.get('category', 'Unknown'),
                check_name=check_result.get('check_name', ''),
                status=CheckStatus(check_result.get('status', 'info')),
                impact_score=check_result.get('impact_score', 50),
                current_value=check_result.get('current_value', ''),
                recommended_value=check_result.get('recommended_value', ''),
                pros=check_result.get('pros', []),
                cons=check_result.get('cons', []),
                ranking_impact=check_result.get('ranking_impact', ''),
                solution=check_result.get('solution', ''),
                enhancements=check_result.get('enhancements', []),
                details=check_result.get('details', {})
            )
            db.add(result_obj)
        
        # ========================================================================
        # PHASE 5: SAVE COMPETITORS (if found)
        # ========================================================================
        competitor_data = orchestrator_result.get('api_data', {}).get('competitors', {})
        if competitor_data and competitor_data.get('tasks'):
            logger.info(f"🏆 Saving competitor analysis")
            for task in competitor_data.get('tasks', [])[:10]:  # Top 10 competitors
                for item in task.get('result', [])[:5]:
                    competitor = CompetitorAnalysis(
                        audit_id=audit_id,
                        competitor_url=item.get('domain', ''),
                        competitor_domain=item.get('domain', ''),
                        domain_authority=item.get('metrics', {}).get('organic', {}).get('pos_1', 0),
                        organic_traffic_estimate=item.get('metrics', {}).get('organic', {}).get('etv', 0),
                        data_source='dataforseo'
                    )
                    db.add(competitor)
                    audit.competitor_count += 1
        
        # ========================================================================
        # PHASE 6: GENERATE CONTENT OPPORTUNITIES
        # ========================================================================
        keyword_data = orchestrator_result.get('api_data', {}).get('keywords', {})
        if keyword_data and keyword_data.get('tasks'):
            logger.info(f"💡 Generating content opportunities")
            for task in keyword_data.get('tasks', [])[:1]:
                for item in task.get('result', [])[:20]:  # Top 20 keyword opportunities
                    keyword_info = item.get('keyword_info', {})
                    opportunity = ContentOpportunity(
                        audit_id=audit_id,
                        opportunity_type=OpportunityType.KEYWORD_GAP,
                        keyword=item.get('keyword', ''),
                        search_volume=keyword_info.get('search_volume'),
                        keyword_difficulty=keyword_info.get('competition', 0) * 100,
                        cpc_value=keyword_info.get('cpc'),
                        potential_traffic=keyword_info.get('search_volume', 0) // 10,  # Estimate
                        competition_level='low' if keyword_info.get('competition', 0) < 0.3 else 'medium',
                        priority_score=min(100, keyword_info.get('search_volume', 0) / 100),
                        status='pending'
                    )
                    db.add(opportunity)
                    audit.opportunities_found += 1
        
        # ========================================================================
        # PHASE 7: UPDATE AUDIT WITH FINAL DATA
        # ========================================================================
        audit.status = AuditStatus.COMPLETED
        audit.total_checks_run = analytics['total_checks']
        audit.checks_passed = analytics['status_distribution']['passed']
        audit.checks_failed = analytics['status_distribution']['failed']
        audit.checks_warning = analytics['status_distribution']['warnings']
        audit.overall_score = round(analytics['overall_score'], 1)
        audit.potential_score = round(analytics['potential_score'], 1)
        audit.score_grade = analytics['grade']
        audit.score_interpretation = analytics['interpretation']
        audit.category_scores = analytics['category_scores']
        audit.analytics_summary = {
            **analytics['executive_summary'],
            'orchestrator_insights': orchestrator_result.get('synthesis', {}).get('synthesis', '') if orchestrator_result.get('success') else None,
            'sub_agent_analyses': len(orchestrator_result.get('agent_analyses', {})) if orchestrator_result.get('success') else 0
        }
        audit.completed_at = datetime.now(timezone.utc)
        audit.audit_metadata = website_data
        
        await db.commit()
        
        # ========================================================================
        # PHASE 8: ANOMALY DETECTION
        # ========================================================================
        try:
            logger.info(f"🔍 Running anomaly detection for audit {audit_id}")
            
            # Get historical audits for this website
            historical_data = await anomaly_detector.get_historical_audits(
                user_id=audit.user_id,
                website_url=website_url,
                limit=10,
                db=db
            )
            
            if len(historical_data) >= 3:
                current_data = {
                    'overall_score': audit.overall_score,
                    'lighthouse_data': audit.lighthouse_data
                }
                
                anomalies = await anomaly_detector.detect_all_anomalies(
                    audit_id=audit_id,
                    user_id=audit.user_id,
                    current_data=current_data,
                    historical_data=historical_data,
                    db=db
                )
                
                audit.anomalies_detected = len(anomalies)
                await db.commit()
                
                if anomalies:
                    logger.warning(f"⚠️ Detected {len(anomalies)} anomalies for audit {audit_id}")
            else:
                logger.info("Not enough historical data for anomaly detection")
        
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            # Don't fail the audit if anomaly detection fails
        
        total_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(f"✅ Audit {audit_id} completed in {total_time:.2f}s. Score: {audit.overall_score}/100")
        logger.info(f"📊 Stats: {audit.competitor_count} competitors, {audit.opportunities_found} opportunities, {audit.anomalies_detected} anomalies")
        
    except Exception as e:
        logger.error(f"❌ Error processing audit {audit_id}: {str(e)}", exc_info=True)
        # Update audit status to failed
        result = await db.execute(select(Audit).where(Audit.id == audit_id))
        audit = result.scalar_one_or_none()
        if audit:
            audit.status = AuditStatus.FAILED
            audit.error_message = str(e)
            await db.commit()
        raise


async def process_audit_background_task(audit_id: str, website_url: str, max_pages: int):
    """
    Background task wrapper for audit processing
    Creates its own database session
    """
    from database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        await process_audit_enhanced(audit_id, website_url, max_pages, db)
