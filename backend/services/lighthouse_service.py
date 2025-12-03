"""
Lighthouse CLI Integration Service
Provides real Core Web Vitals and performance data using Google Lighthouse
"""
import asyncio
import json
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LighthouseService:
    """
    Google Lighthouse service for performance audits
    Uses Lighthouse CLI to generate reports
    """
    
    def __init__(self):
        self.lighthouse_cmd = "lighthouse"
    
    async def run_audit(
        self,
        url: str,
        categories: Optional[list] = None,
        device: str = "desktop"
    ) -> Dict[str, Any]:
        """
        Run Lighthouse audit on a URL
        
        Args:
            url: Target URL to audit
            categories: List of categories (performance, accessibility, best-practices, seo, pwa)
            device: desktop or mobile
        
        Returns:
            Dictionary with Lighthouse results
        """
        if categories is None:
            categories = ["performance", "accessibility", "best-practices", "seo"]
        
        try:
            # Create temporary file for JSON output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                output_path = tmp_file.name
            
            # Build Lighthouse command
            cmd = [
                self.lighthouse_cmd,
                url,
                "--output=json",
                f"--output-path={output_path}",
                f"--preset={device}",
                "--quiet",
                "--chrome-flags='--headless --no-sandbox --disable-dev-shm-usage'",
            ]
            
            # Add categories
            for category in categories:
                cmd.append(f"--only-categories={category}")
            
            # Run Lighthouse
            logger.info(f"Running Lighthouse audit for {url} ({device})")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120  # 2 minutes timeout
            )
            
            # Read results
            if os.path.exists(output_path):
                with open(output_path, 'r') as f:
                    lighthouse_data = json.load(f)
                
                # Clean up temp file
                os.unlink(output_path)
                
                # Extract key metrics
                result = self._extract_metrics(lighthouse_data)
                result["success"] = True
                result["raw_data"] = lighthouse_data
                
                logger.info(f"Lighthouse audit completed. Performance score: {result.get('performance_score', 'N/A')}")
                return result
            
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Lighthouse failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
        
        except asyncio.TimeoutError:
            logger.error(f"Lighthouse timeout for {url}")
            return {
                "success": False,
                "error": "Lighthouse audit timed out after 2 minutes"
            }
        
        except FileNotFoundError:
            logger.error("Lighthouse CLI not found. Install with: npm install -g lighthouse")
            return {
                "success": False,
                "error": "Lighthouse CLI not installed"
            }
        
        except Exception as e:
            logger.error(f"Lighthouse error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_metrics(self, lighthouse_data: Dict) -> Dict[str, Any]:
        """Extract key metrics from Lighthouse report"""
        try:
            categories = lighthouse_data.get('categories', {})
            audits = lighthouse_data.get('audits', {})
            
            # Extract category scores
            result = {
                "performance_score": self._get_score(categories.get('performance')),
                "accessibility_score": self._get_score(categories.get('accessibility')),
                "best_practices_score": self._get_score(categories.get('best-practices')),
                "seo_score": self._get_score(categories.get('seo')),
            }
            
            # Extract Core Web Vitals
            result["core_web_vitals"] = {
                "lcp": self._get_metric_value(audits.get('largest-contentful-paint')),
                "fid": self._get_metric_value(audits.get('max-potential-fid')),
                "cls": self._get_metric_value(audits.get('cumulative-layout-shift')),
                "fcp": self._get_metric_value(audits.get('first-contentful-paint')),
                "si": self._get_metric_value(audits.get('speed-index')),
                "tti": self._get_metric_value(audits.get('interactive')),
                "tbt": self._get_metric_value(audits.get('total-blocking-time')),
            }
            
            # Extract performance metrics
            result["performance_metrics"] = {
                "total_byte_weight": audits.get('total-byte-weight', {}).get('numericValue'),
                "dom_size": audits.get('dom-size', {}).get('numericValue'),
                "uses_http2": audits.get('uses-http2', {}).get('score') == 1,
                "uses_text_compression": audits.get('uses-text-compression', {}).get('score') == 1,
                "efficient_cache": audits.get('uses-long-cache-ttl', {}).get('score'),
            }
            
            # Extract opportunities (things to improve)
            result["opportunities"] = []
            for audit_id, audit_data in audits.items():
                if audit_data.get('details', {}).get('type') == 'opportunity':
                    if audit_data.get('score', 1) < 1:  # Not perfect score
                        result["opportunities"].append({
                            "id": audit_id,
                            "title": audit_data.get('title'),
                            "description": audit_data.get('description'),
                            "score": audit_data.get('score'),
                            "potential_savings": audit_data.get('details', {}).get('overallSavingsMs'),
                        })
            
            # Extract diagnostics
            result["diagnostics"] = []
            for audit_id, audit_data in audits.items():
                if audit_data.get('score') is not None and audit_data.get('score') < 1:
                    if 'diagnostic' in audit_data.get('scoreDisplayMode', ''):
                        result["diagnostics"].append({
                            "id": audit_id,
                            "title": audit_data.get('title'),
                            "description": audit_data.get('description'),
                        })
            
            return result
        
        except Exception as e:
            logger.error(f"Error extracting Lighthouse metrics: {e}")
            return {}
    
    def _get_score(self, category_data: Optional[Dict]) -> Optional[float]:
        """Get score from category data (0-100)"""
        if not category_data:
            return None
        score = category_data.get('score')
        return round(score * 100, 1) if score is not None else None
    
    def _get_metric_value(self, audit_data: Optional[Dict]) -> Optional[Dict]:
        """Get metric value and assessment"""
        if not audit_data:
            return None
        
        return {
            "value": audit_data.get('numericValue'),
            "display_value": audit_data.get('displayValue'),
            "score": self._get_score({'score': audit_data.get('score')}),
        }
    
    async def check_lighthouse_installed(self) -> bool:
        """Check if Lighthouse CLI is installed"""
        try:
            process = await asyncio.create_subprocess_exec(
                self.lighthouse_cmd,
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                version = stdout.decode().strip()
                logger.info(f"Lighthouse CLI found: {version}")
                return True
            
            return False
        
        except FileNotFoundError:
            logger.warning("Lighthouse CLI not found")
            return False
    
    def interpret_core_web_vitals(self, cwv: Dict) -> Dict[str, str]:
        """
        Interpret Core Web Vitals scores
        Returns assessment (good, needs-improvement, poor) for each metric
        """
        interpretations = {}
        
        # LCP (Largest Contentful Paint)
        lcp_value = cwv.get('lcp', {}).get('value', 0)
        if lcp_value <= 2500:
            interpretations['lcp'] = 'good'
        elif lcp_value <= 4000:
            interpretations['lcp'] = 'needs-improvement'
        else:
            interpretations['lcp'] = 'poor'
        
        # FID (First Input Delay)
        fid_value = cwv.get('fid', {}).get('value', 0)
        if fid_value <= 100:
            interpretations['fid'] = 'good'
        elif fid_value <= 300:
            interpretations['fid'] = 'needs-improvement'
        else:
            interpretations['fid'] = 'poor'
        
        # CLS (Cumulative Layout Shift)
        cls_value = cwv.get('cls', {}).get('value', 0)
        if cls_value <= 0.1:
            interpretations['cls'] = 'good'
        elif cls_value <= 0.25:
            interpretations['cls'] = 'needs-improvement'
        else:
            interpretations['cls'] = 'poor'
        
        return interpretations


# Global instance
lighthouse_service = LighthouseService()
