"""Website crawler for SEO audits"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Optional
import logging
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class CrawledPage:
    """Data structure for a crawled page with detailed website-specific data"""
    url: str
    html: str
    status_code: int
    title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_robots: Optional[str] = None
    canonical: Optional[str] = None
    h1_tags: List[str] = None
    h2_tags: List[str] = None
    h3_tags: List[str] = None
    images: List[Dict[str, str]] = None
    links: List[str] = None
    internal_links: List[str] = None
    external_links: List[str] = None
    broken_links: List[str] = None
    scripts: List[str] = None
    stylesheets: List[str] = None
    load_time: float = 0.0
    has_viewport: bool = False
    has_https: bool = False
    word_count: int = 0
    # Enhanced metadata
    og_tags: Dict[str, str] = None
    twitter_tags: Dict[str, str] = None
    schema_markup: List[str] = None
    meta_charset: Optional[str] = None
    meta_lang: Optional[str] = None
    # Content analysis
    paragraphs: List[str] = None
    headings_structure: Dict[str, List[str]] = None
    alt_missing_images: List[str] = None
    large_images: List[Dict[str, any]] = None
    # Technical details
    redirects: List[str] = None
    response_headers: Dict[str, str] = None
    content_type: Optional[str] = None
    # SEO specific
    keyword_density: Dict[str, float] = None
    readability_score: float = 0.0
    
    def __post_init__(self):
        if self.h1_tags is None:
            self.h1_tags = []
        if self.h2_tags is None:
            self.h2_tags = []
        if self.h3_tags is None:
            self.h3_tags = []
        if self.images is None:
            self.images = []
        if self.links is None:
            self.links = []
        if self.internal_links is None:
            self.internal_links = []
        if self.external_links is None:
            self.external_links = []
        if self.broken_links is None:
            self.broken_links = []
        if self.scripts is None:
            self.scripts = []
        if self.stylesheets is None:
            self.stylesheets = []
        if self.og_tags is None:
            self.og_tags = {}
        if self.twitter_tags is None:
            self.twitter_tags = {}
        if self.schema_markup is None:
            self.schema_markup = []
        if self.paragraphs is None:
            self.paragraphs = []
        if self.headings_structure is None:
            self.headings_structure = {}
        if self.alt_missing_images is None:
            self.alt_missing_images = []
        if self.large_images is None:
            self.large_images = []
        if self.redirects is None:
            self.redirects = []
        if self.response_headers is None:
            self.response_headers = {}
        if self.keyword_density is None:
            self.keyword_density = {}


class WebsiteCrawler:
    """Crawls a website and extracts SEO-relevant data"""
    
    def __init__(self, max_pages: int = 20, timeout: int = 30):
        self.max_pages = max_pages
        self.timeout = timeout
        self.visited_urls: Set[str] = set()
        self.crawled_pages: List[CrawledPage] = []
        self.base_domain = ""
    
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain"""
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain or parsed.netloc == f"www.{self.base_domain}" or parsed.netloc == self.base_domain.replace("www.", "")
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and trailing slashes"""
        parsed = urlparse(url)
        # Remove fragment
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        # Remove trailing slash except for root
        if normalized.endswith('/') and len(parsed.path) > 1:
            normalized = normalized[:-1]
        return normalized
    
    async def _fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[CrawledPage]:
        """Fetch and parse a single page"""
        try:
            start_time = time.time()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout), allow_redirects=True) as response:
                html = await response.text()
                load_time = time.time() - start_time
                
                # Parse HTML
                soup = BeautifulSoup(html, 'lxml')
                
                # Extract metadata
                title_tag = soup.find('title')
                title = title_tag.string.strip() if title_tag and title_tag.string else None
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                meta_description = meta_desc.get('content', '').strip() if meta_desc else None
                
                meta_robots = soup.find('meta', attrs={'name': 'robots'})
                robots_content = meta_robots.get('content', '') if meta_robots else None
                
                canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
                canonical = canonical_tag.get('href', '') if canonical_tag else None
                
                # Extract headings with structure
                h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
                h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
                h3_tags = [h3.get_text(strip=True) for h3 in soup.find_all('h3')]
                
                headings_structure = {
                    'h1': h1_tags,
                    'h2': h2_tags,
                    'h3': h3_tags,
                    'h4': [h.get_text(strip=True) for h in soup.find_all('h4')],
                    'h5': [h.get_text(strip=True) for h in soup.find_all('h5')],
                    'h6': [h.get_text(strip=True) for h in soup.find_all('h6')]
                }
                
                # Extract images with detailed info
                images = []
                alt_missing_images = []
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    images.append({
                        'src': src,
                        'alt': alt,
                        'title': img.get('title', ''),
                        'width': img.get('width', ''),
                        'height': img.get('height', '')
                    })
                    if not alt:
                        alt_missing_images.append(src)
                
                # Extract Open Graph tags
                og_tags = {}
                for og in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
                    og_tags[og.get('property')] = og.get('content', '')
                
                # Extract Twitter Card tags
                twitter_tags = {}
                for tw in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
                    twitter_tags[tw.get('name')] = tw.get('content', '')
                
                # Extract schema markup (JSON-LD)
                schema_markup = []
                for script in soup.find_all('script', type='application/ld+json'):
                    if script.string:
                        schema_markup.append(script.string.strip())
                
                # Extract charset and language
                meta_charset = None
                charset_tag = soup.find('meta', charset=True)
                if charset_tag:
                    meta_charset = charset_tag.get('charset')
                
                meta_lang = soup.html.get('lang') if soup.html else None
                
                # Extract paragraphs
                paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
                
                # Extract links - internal vs external
                links = []
                internal_links = []
                external_links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    absolute_url = urljoin(url, href)
                    if absolute_url.startswith('http'):
                        links.append(absolute_url)
                        parsed_link = urlparse(absolute_url)
                        parsed_base = urlparse(url)
                        if parsed_link.netloc == parsed_base.netloc:
                            internal_links.append(absolute_url)
                        else:
                            external_links.append(absolute_url)
                
                # Extract scripts and stylesheets
                scripts = [script.get('src', '') for script in soup.find_all('script', src=True)]
                stylesheets = [link.get('href', '') for link in soup.find_all('link', rel='stylesheet')]
                
                # Check viewport
                viewport = soup.find('meta', attrs={'name': 'viewport'})
                has_viewport = viewport is not None
                
                # Check HTTPS
                has_https = url.startswith('https://')
                
                # Get response headers
                response_headers = dict(response.headers)
                content_type = response_headers.get('Content-Type', '')
                
                # Word count
                text = soup.get_text()
                word_count = len(text.split())
                
                crawled_page = CrawledPage(
                    url=url,
                    html=html,
                    status_code=response.status,
                    title=title,
                    meta_description=meta_description,
                    meta_robots=robots_content,
                    canonical=canonical,
                    h1_tags=h1_tags,
                    h2_tags=h2_tags,
                    h3_tags=h3_tags,
                    images=images,
                    links=links,
                    internal_links=internal_links,
                    external_links=external_links,
                    scripts=scripts,
                    stylesheets=stylesheets,
                    load_time=load_time,
                    has_viewport=has_viewport,
                    has_https=has_https,
                    word_count=word_count,
                    og_tags=og_tags,
                    twitter_tags=twitter_tags,
                    schema_markup=schema_markup,
                    meta_charset=meta_charset,
                    meta_lang=meta_lang,
                    paragraphs=paragraphs,
                    headings_structure=headings_structure,
                    alt_missing_images=alt_missing_images,
                    response_headers=response_headers,
                    content_type=content_type
                )
                
                logger.info(f"Successfully crawled: {url} (Status: {response.status}, Load time: {load_time:.2f}s)")
                return crawled_page
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout crawling {url}")
            return None
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return None
    
    async def crawl(self, start_url: str) -> List[CrawledPage]:
        """
        Crawl a website starting from the given URL
        Returns list of crawled pages
        """
        # Parse base domain
        parsed = urlparse(start_url)
        self.base_domain = parsed.netloc
        
        # Initialize
        urls_to_visit = [start_url]
        self.visited_urls = set()
        self.crawled_pages = []
        
        async with aiohttp.ClientSession() as session:
            while urls_to_visit and len(self.crawled_pages) < self.max_pages:
                # Get next URL
                current_url = urls_to_visit.pop(0)
                normalized_url = self._normalize_url(current_url)
                
                # Skip if already visited
                if normalized_url in self.visited_urls:
                    continue
                
                # Mark as visited
                self.visited_urls.add(normalized_url)
                
                # Crawl the page
                crawled_page = await self._fetch_page(session, normalized_url)
                
                if crawled_page:
                    self.crawled_pages.append(crawled_page)
                    
                    # Add new URLs to visit (only from same domain)
                    for link in crawled_page.links:
                        normalized_link = self._normalize_url(link)
                        if (self._is_same_domain(normalized_link) and 
                            normalized_link not in self.visited_urls and 
                            normalized_link not in urls_to_visit):
                            urls_to_visit.append(normalized_link)
                
                # Small delay to be polite
                await asyncio.sleep(0.5)
        
        logger.info(f"Crawling completed. Total pages crawled: {len(self.crawled_pages)}")
        return self.crawled_pages


async def crawl_website(url: str, max_pages: int = 20) -> List[CrawledPage]:
    """Main function to crawl a website"""
    crawler = WebsiteCrawler(max_pages=max_pages)
    return await crawler.crawl(url)
