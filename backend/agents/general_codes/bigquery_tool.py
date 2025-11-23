"""
BigQuery tool for database operations in agents.
Mock implementation for testing - replace with actual BigQuery client in production.
"""

from typing import List, Dict, Optional
import asyncio
import json
from datetime import datetime

class BigQueryTool:
    """Tool for database operations in agents"""

    def __init__(self):
        # Mock data for testing - in production, use actual BigQuery client
        self.mock_entities = [
            {
                'id': 'person_elon_musk_123',
                'title': 'Elon Musk',
                'type': 'PERSON',
                'aliases': ['Elon', 'Musk', 'Elon R. Musk'],
                'summary': 'CEO of SpaceX and Tesla, entrepreneur and engineer',
                'organizations': ['SpaceX', 'Tesla', 'Neuralink', 'The Boring Company'],
                'confidence': 0.95
            },
            {
                'id': 'org_spacex_456',
                'title': 'SpaceX',
                'type': 'ORGANIZATION',
                'aliases': ['Space Exploration Technologies Corp', 'Space X'],
                'summary': 'Private space exploration company',
                'confidence': 0.98
            },
            {
                'id': 'org_openai_789',
                'title': 'OpenAI',
                'type': 'ORGANIZATION',
                'aliases': ['Open AI'],
                'summary': 'AI research laboratory',
                'confidence': 0.97
            },
            {
                'id': 'person_sam_altman_234',
                'title': 'Sam Altman',
                'type': 'PERSON',
                'aliases': ['Samuel Altman', 'Sam'],
                'summary': 'CEO of OpenAI',
                'organizations': ['OpenAI', 'Y Combinator'],
                'confidence': 0.93
            },
            {
                'id': 'place_mars_567',
                'title': 'Mars',
                'type': 'PLACE',
                'aliases': ['Red Planet', 'Fourth Planet'],
                'summary': 'Fourth planet from the Sun in our solar system',
                'confidence': 1.0
            },
            {
                'id': 'product_gpt5_890',
                'title': 'GPT-5',
                'type': 'PRODUCT',
                'aliases': ['GPT 5', 'GPT-5.0'],
                'summary': 'Next generation AI language model from OpenAI',
                'organizations': ['OpenAI'],
                'confidence': 0.85
            },
            {
                'id': 'person_sarah_chen_345',
                'title': 'Sarah Chen',
                'type': 'PERSON',
                'aliases': ['Sarah', 'S. Chen'],
                'summary': 'Senior Software Engineer, API team lead',
                'confidence': 0.88
            },
            {
                'id': 'project_api_v2_678',
                'title': 'API v2 Project',
                'type': 'PROJECT',
                'aliases': ['API project', 'v2 API'],
                'summary': 'Next generation API development project',
                'confidence': 0.90
            }
        ]

        # Mock events for testing
        self.mock_events = [
            {
                'id': 'event_mars_2016_001',
                'type': 'prediction',
                'subject': 'person_elon_musk_123',
                'description': 'Predicted humans on Mars by 2024',
                'occurred_at': '2016-09-27',
                'confidence': 0.95
            },
            {
                'id': 'event_mars_2020_002',
                'type': 'prediction',
                'subject': 'person_elon_musk_123',
                'description': 'Updated Mars timeline to 2026',
                'occurred_at': '2020-12-01',
                'confidence': 0.93
            }
        ]

    async def query(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Execute query and return results.
        Mock implementation - returns test data based on query patterns.
        """
        # Simulate async database call
        await asyncio.sleep(0.1)

        # Parse query to determine what to return
        if 'core_entities' in sql.lower():
            if params and 'entity_id' in params:
                # Return specific entity
                entity_id = params['entity_id']
                for entity in self.mock_entities:
                    if entity['id'] == entity_id:
                        return [entity]
                return []
            elif params and 'text' in params:
                # Search for entities matching text
                text = params['text'].lower()
                results = []
                for entity in self.mock_entities:
                    if (text in entity['title'].lower() or
                        any(text in alias.lower() for alias in entity.get('aliases', []))):
                        results.append(entity)
                return results
            else:
                # Return all entities (for cache loading)
                return self.mock_entities

        elif 'events' in sql.lower():
            if params and 'entity_id' in params:
                # Return events for specific entity
                entity_id = params['entity_id']
                return [e for e in self.mock_events if e.get('subject') == entity_id]
            return self.mock_events

        return []

    async def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get a specific entity by ID"""
        results = await self.query(
            "SELECT * FROM core_entities WHERE id = @entity_id",
            {'entity_id': entity_id}
        )
        return results[0] if results else None

    async def search_entities(
        self,
        text: str,
        entity_type: Optional[str] = None
    ) -> List[Dict]:
        """Search for entities matching text"""
        results = await self.query(
            "SELECT * FROM core_entities WHERE title LIKE @text",
            {'text': text}
        )

        # Filter by type if specified
        if entity_type and results:
            results = [r for r in results if r.get('type') == entity_type]

        # Add match scores
        for result in results:
            if text.lower() == result['title'].lower():
                result['match_score'] = 1.0
            elif text.lower() in result['title'].lower():
                result['match_score'] = 0.8
            else:
                result['match_score'] = 0.5

        # Sort by match score
        results.sort(key=lambda x: x.get('match_score', 0), reverse=True)

        return results[:5]  # Return top 5 matches

    async def insert(self, table: str, records: List[Dict]) -> bool:
        """Insert records into table (mock implementation)"""
        await asyncio.sleep(0.1)  # Simulate database operation
        print(f"[Mock BigQuery] Would insert {len(records)} records into {table}")
        return True

    async def get_known_entities_for_cache(self, limit: int = 1000) -> List[Dict]:
        """Get top entities for caching"""
        # In production, this would order by access_count
        return self.mock_entities[:limit]