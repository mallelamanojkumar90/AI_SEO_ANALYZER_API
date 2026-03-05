import pytest
from app.seo_score import SEOScorer
from app.keyword_extractor import KeywordExtractor

def test_seo_score_perfect():
    data = {
        "title": "A perfect title of roughly 55 characters is just here",
        "meta_description": "A" * 155,
        "word_count": 1600,
        "h1_count": 1,
        "h2_count": 2,
        "images": 5,
        "images_without_alt": 0,
        "internal_links": 6,
        "keywords": ["test", "seo"],
        "canonical_tag": "yes",
        "mobile_viewport": True
    }
    score = SEOScorer.calculate_score(data)
    assert score >= 90

def test_seo_score_poor():
    data = {
        "title": "Short",
        "meta_description": "",
        "word_count": 100,
        "h1_count": 0,
        "images": 1,
        "images_without_alt": 1,
        "internal_links": 0,
        "keywords": [],
    }
    score = SEOScorer.calculate_score(data)
    assert score < 50

def test_keyword_extraction():
    text = "AI agents are automation tools that use machine learning. Machine learning is great."
    keywords = KeywordExtractor.extract_keywords(text, top_n=2)
    assert "machine" in keywords or "learning" in keywords
