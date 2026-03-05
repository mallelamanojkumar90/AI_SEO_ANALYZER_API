import re
from collections import Counter
from typing import List

# A curated set of common English stop words
STOP_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
    "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now",
    "also", "really", "could", "would", "may", "might", "much", "many", "well", "like"
}

class KeywordExtractor:
    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        # Clean text: lowercase and remove non-alphanumeric characters
        text = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Filter stop words
        filtered_words = [word for word in words if word not in STOP_WORDS]
        
        # Count frequencies
        word_counts = Counter(filtered_words)
        
        # Return top N keywords
        return [word for word, count in word_counts.most_common(top_n)]
