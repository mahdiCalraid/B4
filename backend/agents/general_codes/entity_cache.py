"""
Entity cache for fast lookups during attention filtering.
Maintains in-memory cache of frequently accessed entities.
"""

from typing import Dict, List, Optional, Set
import time
import re
from agents.general_codes.bigquery_tool import BigQueryTool

class EntityCache:
    """In-memory cache for frequently accessed entities"""

    def __init__(self, bigquery_tool: Optional[BigQueryTool] = None):
        self.bq_tool = bigquery_tool or BigQueryTool()
        self.cache: Dict[str, Dict] = {}
        self.top_entities: List[Dict] = []
        self.entity_patterns: Dict[str, List[str]] = {}  # For fast pattern matching
        self.ttl = 3600  # 1 hour TTL
        self.last_refresh = 0
        self.initialized = False

    async def initialize(self):
        """Load top entities into cache"""
        if not self.initialized:
            await self.refresh_top_entities()
            self.initialized = True

    async def refresh_top_entities(self):
        """Refresh the cache of top entities"""
        # Get top entities from BigQuery
        self.top_entities = await self.bq_tool.get_known_entities_for_cache(limit=100)
        self.last_refresh = time.time()

        # Build cache index and pattern matching structures
        for entity in self.top_entities:
            entity_id = entity['id']
            self.cache[entity_id] = entity

            # Build pattern list for fast matching
            patterns = [entity['title'].lower()]
            if entity.get('aliases'):
                patterns.extend([alias.lower() for alias in entity['aliases']])
            self.entity_patterns[entity_id] = patterns

        print(f"[EntityCache] Loaded {len(self.top_entities)} entities into cache")

    async def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get entity from cache or database"""
        # Check if cache needs refresh
        if time.time() - self.last_refresh > self.ttl:
            await self.refresh_top_entities()

        # Check cache first
        if entity_id in self.cache:
            return self.cache[entity_id]

        # Fall back to database
        entity = await self.bq_tool.get_entity(entity_id)
        if entity:
            self.cache[entity_id] = entity

        return entity

    def quick_match(self, text: str) -> List[Dict]:
        """
        Quick pattern match against cached entities.
        Returns list of matching entities with their IDs.
        """
        if not self.initialized:
            return []

        matches = []
        text_lower = text.lower()
        found_ids = set()

        # Check each entity's patterns
        for entity_id, patterns in self.entity_patterns.items():
            for pattern in patterns:
                # Check for word boundary matches to avoid false positives
                # For example, "Sam" should match "Sam Altman" but not "Samsung"
                if self._is_entity_match(pattern, text_lower):
                    if entity_id not in found_ids:
                        entity = self.cache[entity_id]
                        matches.append({
                            'id': entity_id,
                            'title': entity['title'],
                            'type': entity['type'],
                            'confidence': self._calculate_match_confidence(pattern, text_lower)
                        })
                        found_ids.add(entity_id)
                    break

        return matches

    def _is_entity_match(self, pattern: str, text: str) -> bool:
        """Check if pattern matches in text with word boundaries"""
        # Simple word boundary check
        if pattern in text:
            # Check if it's a word boundary match
            # This is simplified - in production, use proper regex
            index = text.find(pattern)
            if index == -1:
                return False

            # Check start boundary
            if index > 0 and text[index - 1].isalnum():
                return False

            # Check end boundary
            end_index = index + len(pattern)
            if end_index < len(text) and text[end_index].isalnum():
                return False

            return True
        return False

    def _calculate_match_confidence(self, pattern: str, text: str) -> float:
        """Calculate confidence score for entity match"""
        # Exact match of full text
        if pattern == text:
            return 1.0
        # Pattern is significant part of text
        elif len(pattern) > 5 and pattern in text:
            return 0.85
        # Short pattern match
        else:
            return 0.7

    def get_entities_for_prompt(self, limit: int = 50) -> str:
        """
        Get formatted entity list for inclusion in prompts.
        Returns a condensed string representation of known entities.
        """
        if not self.top_entities:
            return "No entities cached"

        entity_list = []
        for entity in self.top_entities[:limit]:
            # Format: ID | Name (Type) | Aliases
            aliases = ', '.join(entity.get('aliases', [])[:2]) if entity.get('aliases') else ''
            aliases_str = f" aka {aliases}" if aliases else ""
            entity_list.append(
                f"{entity['id']} | {entity['title']} ({entity['type']}){aliases_str}"
            )

        return '\n'.join(entity_list)

    def get_entity_ids(self) -> List[str]:
        """Get list of all cached entity IDs"""
        return list(self.cache.keys())

    def get_entities_by_type(self, entity_type: str) -> List[Dict]:
        """Get all cached entities of a specific type"""
        return [
            entity for entity in self.top_entities
            if entity.get('type') == entity_type
        ]