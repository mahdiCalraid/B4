"""Text analyzer module."""

import re
from typing import Dict, Any, List
from datetime import datetime
from modules.base import BaseModule, ModuleType


class AnalyzerModule(BaseModule):
    """
    Analyzes text and extracts insights like keywords, entities, sentiment, and topics.

    Uses simple pattern matching and rules. Can be enhanced with NLP libraries
    or AI models later.
    """

    def __init__(self):
        super().__init__()
        self.module_type = ModuleType.INTERACTIVE
        self.version = "1.0.0"

        # Predefined topic keywords
        self.topic_keywords = {
            "energy": ["oil", "gas", "energy", "petroleum", "barrel", "opec"],
            "markets": ["market", "stock", "trading", "price", "surge", "drop"],
            "politics": ["president", "government", "policy", "election", "vote"],
            "technology": ["tech", "ai", "software", "computer", "digital"],
            "economy": ["economy", "gdp", "inflation", "interest", "rate"],
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze text and return insights.

        Args:
            input_data: Dictionary with 'text' and optional parameters

        Returns:
            Dictionary with analysis results
        """
        start_time = datetime.now()

        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            return {
                "error": error,
                "confidence": 0.0,
                **self._get_processing_metadata(start_time)
            }

        text = input_data.get("text", "")
        params = input_data.get("params", {})

        # Perform analysis
        analysis = {
            "keywords": self._extract_keywords(text),
            "entities": self._extract_entities(text),
            "sentiment": self._analyze_sentiment(text),
            "topics": self._classify_topics(text),
            "statistics": self._get_statistics(text),
        }

        # Optional detailed analysis
        if params.get("include_details", False):
            analysis["details"] = {
                "word_count": len(text.split()),
                "char_count": len(text),
                "sentences": len(self._split_sentences(text)),
            }

        return {
            "analysis": analysis,
            "confidence": 0.92,
            **self._get_processing_metadata(start_time)
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Simple: extract words longer than 4 characters
        words = re.findall(r'\b\w{5,}\b', text.lower())

        # Remove common words
        stopwords = {
            "about", "above", "after", "again", "against", "could",
            "should", "would", "there", "their", "where", "which"
        }
        keywords = [w for w in words if w not in stopwords]

        # Return unique keywords, limited to top 10 by frequency
        from collections import Counter
        counter = Counter(keywords)
        return [word for word, count in counter.most_common(10)]

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities (simple pattern matching)."""
        entities = []

        # Capitalized words (potential proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.extend(set(capitalized))

        # Numbers with units (prices, measurements)
        numbers = re.findall(r'\$?\d+(?:,\d{3})*(?:\.\d+)?(?:/\w+)?', text)
        entities.extend(numbers)

        return list(set(entities))[:15]  # Limit to 15 entities

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple sentiment analysis using keyword matching."""
        text_lower = text.lower()

        positive_words = [
            "good", "great", "excellent", "positive", "up", "increase",
            "surge", "growth", "success", "win"
        ]
        negative_words = [
            "bad", "poor", "negative", "down", "decrease", "drop",
            "decline", "loss", "fail", "concern"
        ]

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            sentiment = "positive"
            score = min(0.5 + (pos_count - neg_count) * 0.1, 1.0)
        elif neg_count > pos_count:
            sentiment = "negative"
            score = max(0.5 - (neg_count - pos_count) * 0.1, 0.0)
        else:
            sentiment = "neutral"
            score = 0.5

        return {
            "label": sentiment,
            "score": score,
            "positive_signals": pos_count,
            "negative_signals": neg_count
        }

    def _classify_topics(self, text: str) -> List[str]:
        """Classify text into topics based on keywords."""
        text_lower = text.lower()
        detected_topics = []

        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)

        return detected_topics if detected_topics else ["general"]

    def _get_statistics(self, text: str) -> Dict[str, int]:
        """Get basic text statistics."""
        return {
            "words": len(text.split()),
            "characters": len(text),
            "sentences": len(self._split_sentences(text)),
            "paragraphs": len(text.split('\n\n'))
        }

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting on common punctuation
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
