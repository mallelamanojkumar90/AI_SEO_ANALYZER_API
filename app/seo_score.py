from typing import Dict, Any

class SEOScorer:
    @staticmethod
    def calculate_score(data: Dict[str, Any]) -> int:
        score = 0
        
        # Title optimization (10)
        title_len = len(data.get("title", ""))
        if 50 <= title_len <= 60:
            score += 10
        elif 30 <= title_len <= 70:
            score += 5
            
        # Meta description (10)
        desc_len = len(data.get("meta_description", ""))
        if 150 <= desc_len <= 160:
            score += 10
        elif 100 <= desc_len <= 180:
            score += 5
            
        # Content length (20)
        word_count = data.get("word_count", 0)
        if word_count > 1500:
            score += 20
        elif word_count > 1000:
            score += 15
        elif word_count > 500:
            score += 10
        elif word_count > 300:
            score += 5
            
        # Heading structure (10)
        if data.get("h1_count", 0) == 1:
            score += 5
        if data.get("h2_count", 0) > 0:
            score += 5
            
        # Images ALT tags (10)
        total_images = data.get("images", 0)
        missing_alt = data.get("images_without_alt", 0)
        if total_images == 0:
            score += 10
        else:
            pct_with_alt = (total_images - missing_alt) / total_images
            score += int(10 * pct_with_alt)
            
        # Internal linking (10)
        internal_links = data.get("internal_links", 0)
        if internal_links >= 5:
            score += 10
        elif internal_links > 0:
            score += 5
            
        # Keyword usage (20)
        if len(data.get("keywords", [])) > 0:
            score += 20
            
        # Technical SEO (10)
        technical_score = 0
        if data.get("canonical_tag"):
            technical_score += 3
        if data.get("mobile_viewport"):
            technical_score += 4
            
        # Missing load time direct evaluation here, assume healthy 3 points padding
        score += technical_score + 3
        
        return min(100, max(0, score))
