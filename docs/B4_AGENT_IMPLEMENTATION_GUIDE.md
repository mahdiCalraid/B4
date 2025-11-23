# B4 Agent Implementation Quick Start Guide

## 🚀 How to Implement the Waterfall Agents

### **Directory Structure**

```
backend/
├── agents/
│   ├── agent_definitions/
│   │   ├── attention_filter/
│   │   │   ├── info.txt
│   │   │   ├── prompt.txt
│   │   │   └── structure_output.json
│   │   ├── context_builder/
│   │   ├── entity_extractor/
│   │   ├── event_action/
│   │   ├── concept_sentiment/
│   │   ├── entity_resolver/
│   │   ├── hypothesis_generator/
│   │   ├── memory_prioritizer/
│   │   └── memory_writer/
│   │
│   ├── general_codes/
│   │   ├── bigquery_tool.py      # NEW: Database access
│   │   ├── embedding_tool.py     # NEW: Embedding generation
│   │   ├── entity_cache.py       # NEW: Entity caching
│   │   └── cost_tracker.py       # NEW: Cost management
│   │
│   └── waterfall/
│       ├── __init__.py
│       ├── orchestrator.py       # Main waterfall orchestrator
│       └── stage_processors.py   # Stage-specific logic
```

---

## 📝 Agent Definition Templates

### **Example: `attention_filter` Agent**

#### **info.txt**
```
name: attention_filter
version: 1.0
stage: 1_attention
type: filter
description: Fast triage to filter irrelevant content using pattern matching and cached entities
default_model: regex
escalation_model: gpt-oss-20b
```

#### **prompt.txt**
```
You are the Attention Filter for the B4 memory system. Your job is to quickly assess if an input is worth processing.

Analyze the input for:
1. Relevance to known domains (tech, business, personal)
2. Presence of important entities or concepts
3. Urgency indicators
4. Information value

Known entities to check for:
{known_entities}

Return a structured assessment of whether this input should be processed further.
```

#### **structure_output.json**
```json
{
  "should_process": {
    "type": "boolean",
    "description": "Whether the input should proceed through the pipeline"
  },
  "relevance_score": {
    "type": "number",
    "description": "Relevance score from 0 to 1"
  },
  "importance_score": {
    "type": "number",
    "description": "Importance score from 0 to 1"
  },
  "detected_domains": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Detected topic domains"
  },
  "known_entity_hints": {
    "type": "array",
    "items": {"type": "string"},
    "description": "IDs of detected known entities"
  },
  "skip_reason": {
    "type": "string",
    "description": "Reason for skipping if should_process is false"
  }
}
```

---

## 🔧 Tool Implementation Examples

### **BigQueryTool** (`agents/general_codes/bigquery_tool.py`)

```python
from typing import List, Dict, Optional
from google.cloud import bigquery
import asyncio

class BigQueryTool:
    """Tool for database operations in agents"""

    def __init__(self):
        self.client = bigquery.Client(project='bthree-476203')
        self.dataset_id = 'brain_data'

    async def query(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute query and return results"""
        job_config = bigquery.QueryJobConfig()

        if params:
            job_config.query_parameters = [
                bigquery.ScalarQueryParameter(k, 'STRING', str(v))
                for k, v in params.items()
            ]

        # Run query
        query_job = self.client.query(sql, job_config=job_config)

        # Convert to async
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, query_job.result)

        # Convert to dict list
        return [dict(row) for row in results]

    async def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get a specific entity by ID"""
        sql = f"""
        SELECT *
        FROM `{self.client.project}.{self.dataset_id}.core_entities`
        WHERE id = @entity_id
        """

        results = await self.query(sql, {'entity_id': entity_id})
        return results[0] if results else None

    async def search_entities(
        self,
        text: str,
        entity_type: Optional[str] = None
    ) -> List[Dict]:
        """Search for entities matching text"""
        sql = f"""
        SELECT
            id,
            title,
            type,
            summary,
            confidence,
            CASE
                WHEN LOWER(title) = LOWER(@text) THEN 1.0
                WHEN LOWER(title) LIKE CONCAT('%', LOWER(@text), '%') THEN 0.8
                ELSE 0.5
            END as match_score
        FROM `{self.client.project}.{self.dataset_id}.core_entities`
        WHERE
            LOWER(title) LIKE CONCAT('%', LOWER(@text), '%')
            {f"AND type = @entity_type" if entity_type else ""}
        ORDER BY match_score DESC
        LIMIT 5
        """

        params = {'text': text}
        if entity_type:
            params['entity_type'] = entity_type

        return await self.query(sql, params)
```

### **EntityCache** (`agents/general_codes/entity_cache.py`)

```python
from typing import Dict, List, Optional
import time
import asyncio

class EntityCache:
    """In-memory cache for frequently accessed entities"""

    def __init__(self, bigquery_tool, ttl: int = 3600):
        self.bq_tool = bigquery_tool
        self.cache: Dict[str, Dict] = {}
        self.top_entities: List[Dict] = []
        self.ttl = ttl
        self.last_refresh = 0

    async def initialize(self):
        """Load top entities into cache"""
        await self.refresh_top_entities()

    async def refresh_top_entities(self):
        """Refresh the cache of top entities"""
        sql = """
        SELECT
            id,
            title,
            type,
            aliases,
            summary
        FROM `bthree-476203.brain_data.core_entities`
        ORDER BY JSON_EXTRACT_SCALAR(access_info, '$.access_count') DESC
        LIMIT 1000
        """

        self.top_entities = await self.bq_tool.query(sql)
        self.last_refresh = time.time()

        # Build cache index
        for entity in self.top_entities:
            self.cache[entity['id']] = entity

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

    def quick_match(self, text: str) -> List[str]:
        """Quick pattern match against cached entities"""
        matches = []
        text_lower = text.lower()

        for entity in self.top_entities:
            # Check title
            if text_lower in entity['title'].lower():
                matches.append(entity['id'])
                continue

            # Check aliases
            if entity.get('aliases'):
                for alias in entity['aliases']:
                    if text_lower in alias.lower():
                        matches.append(entity['id'])
                        break

        return matches
```

---

## 🔄 Waterfall Orchestrator

### **orchestrator.py**

```python
from typing import Dict, Any
import asyncio
from agents.agent_loader import AgentLoader
from agents.general_codes.bigquery_tool import BigQueryTool
from agents.general_codes.entity_cache import EntityCache
from agents.general_codes.cost_tracker import CostTracker

class B4WaterfallOrchestrator:
    """Main orchestrator for the 9-agent waterfall pipeline"""

    def __init__(self):
        # Initialize tools
        self.bq_tool = BigQueryTool()
        self.entity_cache = EntityCache(self.bq_tool)
        self.cost_tracker = CostTracker()

        # Load agents
        self.agents = {
            # Stage 1: Attention
            'attention': AgentLoader.load('attention_filter'),

            # Stage 2: Perception
            'context': AgentLoader.load('context_builder'),

            # Stage 3: Comprehension (Parallel)
            'entities': AgentLoader.load('entity_extractor'),
            'events': AgentLoader.load('event_action'),
            'concepts': AgentLoader.load('concept_sentiment'),

            # Stage 4: Consolidation
            'resolver': AgentLoader.load('entity_resolver'),
            'hypothesis': AgentLoader.load('hypothesis_generator'),

            # Stage 5: Integration
            'prioritizer': AgentLoader.load('memory_prioritizer'),
            'writer': AgentLoader.load('memory_writer')
        }

        # Initialize entity cache
        asyncio.create_task(self.entity_cache.initialize())

    async def process(self, text: str, metadata: Dict = None) -> Dict[str, Any]:
        """Process input through all 5 stages"""

        try:
            # STAGE 1: ATTENTION
            # Quick filter with cached entities
            attention_input = {
                'text': text,
                'metadata': metadata or {},
                'known_entities': self.entity_cache.top_entities[:100]
            }

            attention_result = await self.agents['attention'].process(
                input_data=str(attention_input),
                model='regex'  # Start with free option
            )

            if not attention_result['data']['should_process']:
                return {
                    'processed': False,
                    'reason': attention_result['data']['skip_reason']
                }

            # STAGE 2: PERCEPTION
            # Build context and load memories
            context_input = {
                'text': text,
                'attention_result': attention_result['data'],
                'entity_hints': attention_result['data']['known_entity_hints']
            }

            context_result = await self.agents['context'].process(
                input_data=str(context_input),
                model='gemini-2.0-flash-lite'
            )

            # STAGE 3: COMPREHENSION (Parallel)
            # Extract entities, events, and concepts simultaneously
            comprehension_tasks = [
                self.agents['entities'].process(
                    input_data=str({
                        'text': text,
                        'context': context_result['data'],
                        'bq_tool': 'available'  # Signal that DB is available
                    }),
                    model='gpt-oss-20b'
                ),
                self.agents['events'].process(
                    input_data=str({
                        'text': text,
                        'context': context_result['data']
                    }),
                    model='gemini-2.0-flash-lite'
                ),
                self.agents['concepts'].process(
                    input_data=str({
                        'text': text,
                        'context': context_result['data']
                    }),
                    model='gpt-oss-20b'
                )
            ]

            entities_result, events_result, concepts_result = await asyncio.gather(
                *comprehension_tasks
            )

            # STAGE 4: CONSOLIDATION
            # Resolve entities and generate hypotheses
            resolution_input = {
                'entities': entities_result['data'],
                'events': events_result['data'],
                'existing_knowledge': 'from_bigquery'
            }

            resolution_result = await self.agents['resolver'].process(
                input_data=str(resolution_input),
                model='gemini-2.0-flash'
            )

            hypothesis_input = {
                'extraction_results': {
                    'entities': entities_result['data'],
                    'events': events_result['data'],
                    'concepts': concepts_result['data']
                },
                'resolution': resolution_result['data']
            }

            hypothesis_result = await self.agents['hypothesis'].process(
                input_data=str(hypothesis_input),
                model='gemini-2.0-flash'
            )

            # STAGE 5: INTEGRATION
            # Prioritize and write to memory
            priority_input = {
                'all_data': {
                    'entities': resolution_result['data'],
                    'events': events_result['data'],
                    'concepts': concepts_result['data'],
                    'hypotheses': hypothesis_result['data']
                },
                'importance': attention_result['data']['importance_score']
            }

            priority_result = await self.agents['prioritizer'].process(
                input_data=str(priority_input),
                model='gpt-oss-20b'
            )

            # Only write if priority is high enough
            if priority_result['data']['memory_priority']['level'] < 4:
                writer_input = {
                    'prioritized_data': priority_result['data'],
                    'all_extracted': priority_input['all_data']
                }

                writer_result = await self.agents['writer'].process(
                    input_data=str(writer_input),
                    model='gemini-2.0-flash-lite'
                )

                return {
                    'processed': True,
                    'pipeline_complete': True,
                    'context_id': context_result['data']['context_id'],
                    'entities_found': len(entities_result['data']['entities']),
                    'events_found': len(events_result['data']['events']),
                    'records_written': writer_result['data']['written_records'],
                    'cost': self.cost_tracker.get_total_cost()
                }

            return {
                'processed': True,
                'pipeline_complete': True,
                'stored': False,
                'reason': 'Low priority - not worth storing'
            }

        except Exception as e:
            return {
                'processed': False,
                'error': str(e),
                'cost': self.cost_tracker.get_total_cost()
            }
```

---

## 🧪 Testing the Pipeline

### **Test Script**

```python
# test_waterfall.py
import asyncio
from agents.waterfall.orchestrator import B4WaterfallOrchestrator

async def test_pipeline():
    # Initialize orchestrator
    orchestrator = B4WaterfallOrchestrator()

    # Test inputs
    test_cases = [
        "Elon Musk said we will be on Mars in 2030",
        "Meeting with Sarah about the API project next Tuesday",
        "OpenAI announced GPT-5 will launch in March 2025",
        "Random spam text that should be filtered out"
    ]

    for test_input in test_cases:
        print(f"\n📝 Processing: {test_input}")
        result = await orchestrator.process(test_input)
        print(f"✅ Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
```

---

## 🚦 Next Steps

1. **Create the first 3 agents** (attention_filter, context_builder, entity_extractor)
2. **Implement BigQueryTool and EntityCache**
3. **Test Stage 1-2 pipeline**
4. **Add remaining agents incrementally**
5. **Optimize with caching and parallelization**

---

## 📚 API Endpoint Integration

Add to `app/routes/agents.py`:

```python
@router.post("/waterfall/process")
async def process_waterfall(request: WaterfallRequest):
    """Process input through complete waterfall pipeline"""

    orchestrator = B4WaterfallOrchestrator()
    result = await orchestrator.process(
        text=request.text,
        metadata=request.metadata
    )

    return {
        "success": result.get('processed', False),
        "pipeline_result": result
    }
```

---

*This guide provides the templates and structure to start implementing the waterfall agents. Begin with Stage 1-2 agents and gradually build up the complete pipeline.*