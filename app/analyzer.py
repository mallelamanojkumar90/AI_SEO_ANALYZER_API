from bs4 import BeautifulSoup
from typing import Dict, Any
from .keyword_extractor import KeywordExtractor
import re

class SEOAnalyzer:
    def __init__(self, html: str, url: str):
        self.soup = BeautifulSoup(html, 'lxml')
        self.url = url
        self.domain = self._get_domain(url)

    def _get_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def analyze(self) -> Dict[str, Any]:
        title = self._get_title()
        meta_desc = self._get_meta_description()
        headings = self._get_headings()
        images = self._get_images()
        links = self._get_links()
        text_content = self._get_text_content()
        words = len(text_content.split())
        
        # Keyword extraction
        keywords = KeywordExtractor.extract_keywords(text_content, top_n=5)
        
        # Technical
        canonical = self._get_canonical()
        mobile_friendly = self._get_viewport()
        
        issues = []
        
        # Issues detection
        if len(title) < 50 or len(title) > 60:
            if len(title) == 0:
                issues.append("Missing title tag.")
            else:
                issues.append(f"Title length is {len(title)} chars. Ideal is 50-60.")
                
        if len(meta_desc) < 150 or len(meta_desc) > 160:
            if len(meta_desc) == 0:
                issues.append("Missing meta description.")
            else:
                issues.append(f"Meta description length is {len(meta_desc)} chars. Ideal is 150-160.")
                
        if images['missing_alt'] > 0:
            issues.append(f"{images['missing_alt']} images out of {images['total']} missing alt tags.")
            
        if links['internal'] < 2:
            issues.append("Too few internal links. Consider adding more interconnectivity.")
            
        return {
            "title": title,
            "meta_description": meta_desc,
            "word_count": words,
            "readability_score": self._calculate_readability(text_content),
            "keywords": keywords,
            "internal_links": links['internal'],
            "external_links": links['external'],
            "images": images['total'],
            "images_without_alt": images['missing_alt'],
            "h1_count": headings.get('h1', 0),
            "h2_count": headings.get('h2', 0),
            "h3_count": headings.get('h3', 0),
            "canonical_tag": canonical,
            "mobile_viewport": mobile_friendly,
            "issues": issues,
            "text_content": text_content # Added for AI Context
        }

    def _get_title(self) -> str:
        title_tag = self.soup.find('title')
        return title_tag.text.strip() if title_tag else ""

    def _get_meta_description(self) -> str:
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""

    def _get_headings(self) -> Dict[str, int]:
        return {
            "h1": len(self.soup.find_all('h1')),
            "h2": len(self.soup.find_all('h2')),
            "h3": len(self.soup.find_all('h3'))
        }

    def _get_images(self) -> Dict[str, int]:
        images = self.soup.find_all('img')
        missing_alt = sum(1 for img in images if not img.get('alt', '').strip())
        return {"total": len(images), "missing_alt": missing_alt}

    def _get_links(self) -> Dict[str, int]:
        links = self.soup.find_all('a', href=True)
        internal = 0
        external = 0
        for link in links:
            href = link.get('href', '')
            if not href or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            if href.startswith('http') and self.domain not in href:
                external += 1
            else:
                internal += 1
        return {"internal": internal, "external": external}
        
    def _get_canonical(self) -> str:
        link = self.soup.find('link', attrs={'rel': 'canonical'})
        return link.get('href', '') if link else ""
        
    def _get_viewport(self) -> bool:
        meta = self.soup.find('meta', attrs={'name': 'viewport'})
        return bool(meta)

    def _get_text_content(self) -> str:
        # Clone soup to not destroy the original tree
        from copy import copy
        
        # Remove scripts, styles, metadata
        for element in self.soup(["script", "style", "meta", "noscript"]):
            element.extract()
            
        return self.soup.get_text(separator=' ', strip=True)
        
    def _calculate_readability(self, text: str) -> int:
        words = len(text.split())
        sentences = max(1, len(re.split(r'[.!?]+', text)))
        characters = len(re.sub(r'\s+', '', text))
        
        if words == 0:
            return 0
            
        syllables = max(1, characters / 3) # Very rough approximation for syllables
        
        # Flesch Reading Ease
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        return max(0, min(100, int(score)))
