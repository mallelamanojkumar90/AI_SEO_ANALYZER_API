import os
import json
from typing import List, Dict, Any
import logging

try:
    from openai import AsyncOpenAI
    has_openai = True
except ImportError:
    has_openai = False

logger = logging.getLogger(__name__)

class AIRecommendationEngine:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key and has_openai:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            if not has_openai:
                logger.warning("OpenAI library not installed. Falling back to rule-based engine.")
            elif not self.api_key:
                logger.info("OPENAI_API_KEY not provided. Falling back to rule-based engine.")

    async def get_recommendations(self, data: Dict[str, Any]) -> List[str]:
        if self.client:
            return await self._get_llm_recommendations(data)
        else:
            return self._get_rule_based_recommendations(data)

    async def _get_llm_recommendations(self, data: Dict[str, Any]) -> List[str]:
        prompt = f"""
        Analyze the following SEO data and provide a concise JSON list of 3-5 specific, actionable SEO recommendations.
        Output exactly in this JSON format: {{"recommendations": ["rec1", "rec2"]}}
        
        Data:
        URL: {data.get('url')}
        Title: {data.get('title')}
        Description: {data.get('meta_description')}
        Word Count: {data.get('word_count')}
        H1 Count: {data.get('h1_count')}
        Issues: {', '.join(data.get('issues', []))}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            return result_json.get("recommendations", [])
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_rule_based_recommendations(data)

    def _get_rule_based_recommendations(self, data: Dict[str, Any]) -> List[str]:
        recs = []
        if len(data.get("title", "")) < 50:
            recs.append("Optimize title by increasing length to 50-60 characters and including primary keyword.")
        if data.get("word_count", 0) < 1500:
            recs.append("Increase content length to at least 1500 words for comprehensive topical relevance.")
        if data.get("h1_count", 0) != 1:
            recs.append("Ensure the page has exactly one H1 tag.")
        if data.get("internal_links", 0) < 5:
            recs.append("Add more internal links to related pages to improve navigation and SEO equity.")
        if data.get("images_without_alt", 0) > 0:
            recs.append("Add descriptive ALT tags to all images to improve accessibility and image search SEO.")
            
        if not recs:
            recs.append("Great job! Keep updating the content frequently to maintain relevance.")
            
        return recs
