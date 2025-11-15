# B4 Comprehensive Blueprint: Event-Driven World Model with Agent Orchestration

**Version**: 2.1
**Date**: November 9, 2025
**Authors**: System Architect + Claude
**Status**: Implementation Ready

---

## Executive Summary

B4 represents a synthesis of two powerful architectures:
1. **B3's Agent Orchestration System** - A hierarchical agent framework with node-based workflow composition
2. **B4's Event-Centric World Model** - A lean, cost-effective system for ingesting and structuring world information

This blueprint merges the best of both approaches: the development velocity and modularity of B3's agent system with the practical, scalable architecture of B4's event processing pipeline. The result is a system that can both understand the world (through event extraction) and act on it (through intelligent agent orchestration).

**Core Innovation**: Event-driven agent activation where world model changes trigger specialized agent workflows, creating a reactive, intelligent system that scales cost-effectively.

---

## Part 1: Unified Architecture Vision

### 1.1 System Philosophy

**From B3 (Agent-First)**:
- Hierarchical agent inheritance for rapid development
- Node-based workflow composition for flexibility
- Cost-aware model routing (start cheap, escalate when needed)
- Mini-nodes pattern for pluggable components

**From B4 (Event-First)**:
- Event as the atomic unit of world knowledge
- Waterfall processing (rules → NLP → LLM)
- Posting-list indexes for fast retrieval
- Provenance and auditability as core requirements

**New Synthesis**:
- Events trigger agent workflows
- Agents can create and modify events
- Bidirectional flow: World → Events → Agents → Actions → World

### 1.2 Key Design Principles

1. **Event-Agent Coupling**: Every significant event can trigger agent evaluation
2. **Cost Optimization**: Always try cheapest solution first (regex → NLP → local LLM → cloud LLM)
3. **Modular Composition**: Both events and agents are composable units
4. **Incremental Complexity**: Start simple, add sophistication only when proven necessary
5. **Observable & Auditable**: Every decision has a trace, every fact has a source
6. **Append-Only Truth**: Never delete, only supersede with newer evidence
7. **Developer Velocity**: Standardized patterns for adding new agents and event types

---

## Part 2: Core Components Architecture

### 2.1 Event Processing Pipeline (from B4)

```
Sources → Ingest → Normalize → Extract → Classify → Index → Store
                         ↓
                    Agent Triggers
                         ↓
                  Workflow Execution
```

**Stages**:
1. **Ingestion Layer**: Multi-source connectors (X, Reddit, News, Telegram, Email)
2. **Normalization**: Dedup, language detection, timestamp standardization
3. **Extraction Waterfall**:
   - Fast tags (regex/dictionaries)
   - NER (spaCy/Flair)
   - Event classification (small models)
   - Claim extraction (templates → LLM fallback)
4. **Canonicalization**: Entity resolution, topic assignment
5. **Storage**: Firestore for events, GCS for raw content
6. **Indexing**: Posting lists by entity/topic/predicate/time

### 2.2 Agent Orchestration System (from B3)

```
Base Agents → Specialized Agents → Workflow Nodes → Execution
                                          ↑
                                    Event Triggers
```

**Hierarchy**:
```
BaseAgent (Abstract)
├── OllamaAgent (Local, fast, free)
│   ├── ClassifierAgent
│   ├── ValidatorAgent
│   └── FormatterAgent
├── GeminiAgent (Cloud, powerful)
│   ├── AnalysisAgent
│   ├── ReasoningAgent
│   └── CreativeAgent
└── OrchestrationAgent (Multi-agent coordination)
    ├── ResearchAgent
    ├── PlanningAgent
    └── ExecutionAgent
```

### 2.3 Workflow Nodes (Enhanced from B3)

```python
class EventProcessorNode(BaseNode):
    """Processes incoming events through agent pipeline"""

    async def execute(self, event_data):
        # 1. Quick classification
        category = await self.classify_agent.process(event_data)

        # 2. Entity extraction
        entities = await self.entity_agent.extract(event_data)

        # 3. Importance scoring
        importance = await self.importance_agent.score(event_data, entities)

        # 4. Trigger specialized workflows if important
        if importance > THRESHOLD:
            await self.trigger_specialized_workflow(event_data, category)

        return {
            "event_id": event_data["id"],
            "category": category,
            "entities": entities,
            "importance": importance,
            "triggered_workflows": self.triggered
        }
```

---

## Part 3: Data Models (Unified)

### 3.1 Enhanced Event Model

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Event(BaseModel):
    """Core event model with agent metadata"""

    # Core fields (from B4)
    event_id: str
    kind: str  # statement, policy, market_move, etc.
    timespan: Dict[str, Any]
    entities: List[str]
    topics: List[str]
    claims: List[Dict[str, Any]]

    # Agent processing metadata (new)
    processing_agents: List[str] = Field(default_factory=list)
    agent_confidence: Dict[str, float] = Field(default_factory=dict)
    triggered_workflows: List[str] = Field(default_factory=list)

    # Provenance (from B4)
    evidence_doc_ids: List[str]
    source_reliability: float

    # Versioning
    version: int = 1
    created_at: datetime
    updated_at: datetime

    # Agent-generated insights (new)
    insights: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    risk_score: Optional[float] = None
```

### 3.2 Agent Task Model

```python
class AgentTask(BaseModel):
    """Task model for agent execution"""

    task_id: str
    agent_type: str  # ollama, gemini, orchestration
    priority: int = Field(ge=1, le=10)

    # Input
    input_event_ids: List[str]
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

    # Execution
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Output
    result: Optional[Any] = None
    confidence: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None

    # Chaining
    next_tasks: List[str] = Field(default_factory=list)
    parent_task_id: Optional[str] = None
```

### 3.3 Workflow Definition Model

```python
class WorkflowDefinition(BaseModel):
    """Defines event-triggered workflows"""

    workflow_id: str
    name: str
    description: str

    # Triggers
    trigger_conditions: Dict[str, Any]  # event patterns that trigger this

    # Nodes
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, str]]  # from_node -> to_node

    # Configuration
    max_cost: Optional[float] = None
    timeout_seconds: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None

    # Metadata
    created_by: str
    created_at: datetime
    active: bool = True
```

---

## Part 4: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Basic event ingestion and storage

**Tasks**:
1. Set up GCP infrastructure (Firestore, GCS, Pub/Sub)
2. Implement basic ingestion for 1-2 sources (RSS, X/Twitter)
3. Create event normalization pipeline
4. Basic Firestore storage with simple indexes
5. Minimal REST API for event retrieval

**Deliverables**:
- `/events` endpoint working
- Raw content in GCS
- Basic deduplication

### Phase 2: Agent Integration (Weeks 3-4)
**Goal**: Connect B3's agent system to event pipeline

**Tasks**:
1. Port OllamaAgent and GeminiAgent base classes
2. Create EventClassifierAgent (using Ollama)
3. Create EntityExtractorAgent (using Gemini)
4. Implement agent task queue with Pub/Sub
5. Basic workflow executor for linear agent chains

**Deliverables**:
- Agents processing events
- Task execution logs
- Cost tracking dashboard

### Phase 3: Intelligence Layer (Weeks 5-6)
**Goal**: Smart event processing and agent triggering

**Tasks**:
1. Implement claim extraction with fallback cascade
2. Create importance scoring agent
3. Build entity canonicalization service
4. Implement topic taxonomy assignment
5. Create event-to-workflow trigger mapping

**Deliverables**:
- Structured claims in events
- Entity resolution working
- Automated workflow triggering

### Phase 4: Advanced Workflows (Weeks 7-8)
**Goal**: Complex multi-agent orchestration

**Tasks**:
1. Implement parallel node execution
2. Create conditional branching in workflows
3. Build workflow state management
4. Implement mini-nodes pattern for model swapping
5. Create workflow monitoring dashboard

**Deliverables**:
- Complex workflows running
- Real-time workflow visualization
- Performance metrics

### Phase 5: Optimization & Scale (Weeks 9-10)
**Goal**: Production-ready performance

**Tasks**:
1. Implement posting-list indexes for fast queries
2. Create 2-hop neighbor queries
3. Build event clustering and deduplication
4. Optimize agent routing for cost
5. Implement caching layers

**Deliverables**:
- Sub-second query responses
- 90% cost reduction vs naive approach
- Horizontal scaling proven

### Phase 6: Intelligence Products (Weeks 11-12)
**Goal**: User-facing intelligence features

**Tasks**:
1. Build situation brief generator
2. Create trend detection agents
3. Implement contradiction detection
4. Build alert system for important events
5. Create natural language query interface

**Deliverables**:
- Daily intelligence briefs
- Real-time alerts
- Query API

---

## Part 5: Technical Implementation Details

### 5.1 Event Processing Waterfall

```python
class EventProcessingPipeline:
    """Waterfall pattern for cost-effective processing"""

    async def process(self, raw_content: str) -> Event:
        # Level 1: Regex/Dictionary (essentially free)
        fast_entities = self.fast_tagger.extract(raw_content)
        if self.is_sufficient(fast_entities):
            return self.create_event(fast_entities)

        # Level 2: Classical NLP (very cheap)
        nlp_entities = await self.spacy_processor.extract(raw_content)
        if self.is_sufficient(nlp_entities):
            return self.create_event(nlp_entities)

        # Level 3: Local LLM (cheap)
        if self.ollama_available:
            local_result = await self.ollama_agent.extract(raw_content)
            if local_result.confidence > 0.8:
                return self.create_event(local_result)

        # Level 4: Cloud LLM (expensive, but accurate)
        cloud_result = await self.gemini_agent.extract(
            raw_content,
            schema=self.event_schema,
            max_tokens=500
        )
        return self.create_event(cloud_result)
```

### 5.2 Agent Inheritance Pattern

```python
class BaseEventAgent(ABC):
    """Abstract base for all event-processing agents"""

    @abstractmethod
    async def process_event(self, event: Event) -> Dict[str, Any]:
        """Process an event and return insights"""
        pass

    async def should_escalate(self, confidence: float) -> bool:
        """Determine if processing should escalate to more powerful agent"""
        return confidence < self.confidence_threshold

    def track_metrics(self, tokens: int, latency: float):
        """Track usage metrics for cost optimization"""
        self.metrics.record(tokens=tokens, latency=latency)

class OllamaEventAgent(BaseEventAgent):
    """Fast, local processing for simple tasks"""

    def __init__(self):
        self.model = "gemma3:270m"  # Tiny, fast model
        self.confidence_threshold = 0.7

    async def process_event(self, event: Event) -> Dict[str, Any]:
        # Quick classification
        prompt = self.build_prompt(event)
        result = await self.ollama_client.generate(prompt)
        return self.parse_result(result)

class GeminiEventAgent(BaseEventAgent):
    """Powerful cloud processing for complex tasks"""

    def __init__(self):
        self.model = "gemini-2.0-flash"
        self.confidence_threshold = 0.9

    async def process_event(self, event: Event) -> Dict[str, Any]:
        # Complex reasoning with structured output
        result = await self.gemini_client.generate(
            prompt=self.build_prompt(event),
            response_schema=self.output_schema
        )
        return result
```

### 5.3 Workflow Node Composition

```python
class WorkflowExecutor:
    """Executes node-based workflows triggered by events"""

    def __init__(self):
        self.nodes = {}
        self.workflows = {}
        self.triggers = defaultdict(list)

    async def register_trigger(
        self,
        event_pattern: Dict[str, Any],
        workflow_id: str
    ):
        """Register event patterns that trigger workflows"""
        pattern_key = self.pattern_to_key(event_pattern)
        self.triggers[pattern_key].append(workflow_id)

    async def process_event(self, event: Event):
        """Check if event triggers any workflows"""
        triggered = []

        for pattern_key, workflow_ids in self.triggers.items():
            if self.matches_pattern(event, pattern_key):
                for workflow_id in workflow_ids:
                    task_id = await self.execute_workflow(
                        workflow_id,
                        initial_data={"event": event}
                    )
                    triggered.append(task_id)

        return triggered

    async def execute_workflow(
        self,
        workflow_id: str,
        initial_data: Dict[str, Any]
    ) -> str:
        """Execute a workflow asynchronously"""
        workflow = self.workflows[workflow_id]
        task_id = self.generate_task_id()

        # Create execution context
        context = WorkflowContext(
            task_id=task_id,
            workflow_id=workflow_id,
            data=initial_data,
            state="running"
        )

        # Execute nodes in topological order
        for node_id in workflow.topological_order:
            node = self.nodes[node_id]

            try:
                # Check if we should use cheap or expensive agent
                if context.data.get("confidence", 1.0) < 0.7:
                    node = self.escalate_node(node)

                result = await node.execute(context.data)
                context.data.update(result)

            except Exception as e:
                context.state = "failed"
                context.error = str(e)
                break

        return task_id
```

### 5.4 Mini-Nodes Pattern Implementation

```python
class MiniNode(ABC):
    """Pluggable component for workflow nodes"""

    @abstractmethod
    async def process(self, data: Any) -> Any:
        pass

class ModelMiniNode(MiniNode):
    """Swappable AI model"""

    def __init__(self, model_type: str, model_name: str):
        self.model_type = model_type  # ollama, gemini, openai
        self.model_name = model_name

    async def process(self, prompt: str) -> str:
        if self.model_type == "ollama":
            return await ollama_client.generate(self.model_name, prompt)
        elif self.model_type == "gemini":
            return await gemini_client.generate(self.model_name, prompt)
        # ... other models

class StructureMiniNode(MiniNode):
    """Enforces output structure"""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.validator = self.create_validator(schema)

    async def process(self, data: Any) -> Any:
        return self.validator.validate(data)

class AIAgentNode(BaseNode):
    """Composable AI node using mini-nodes"""

    def __init__(
        self,
        model: ModelMiniNode,
        structure: Optional[StructureMiniNode] = None,
        preprocessor: Optional[MiniNode] = None,
        postprocessor: Optional[MiniNode] = None
    ):
        self.model = model
        self.structure = structure
        self.preprocessor = preprocessor
        self.postprocessor = postprocessor

    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Preprocess
        if self.preprocessor:
            data = await self.preprocessor.process(data)

        # Generate
        result = await self.model.process(data["prompt"])

        # Structure
        if self.structure:
            result = await self.structure.process(result)

        # Postprocess
        if self.postprocessor:
            result = await self.postprocessor.process(result)

        return result
```

---

## Part 6: Novel Ideas & Enhancements

### 6.1 Predictive Event Triggering

Instead of just reacting to events, predict likely future events and pre-position agents:

```python
class PredictiveEventSystem:
    """Predicts future events based on patterns"""

    async def analyze_patterns(self, recent_events: List[Event]):
        # Identify recurring patterns
        patterns = self.pattern_detector.find_patterns(recent_events)

        # Predict next likely events
        predictions = []
        for pattern in patterns:
            next_event = self.predictor.predict_next(pattern)
            confidence = self.predictor.confidence(pattern)

            if confidence > 0.7:
                predictions.append({
                    "predicted_event_type": next_event,
                    "confidence": confidence,
                    "expected_time": pattern.next_occurrence(),
                    "pre_positioned_agents": self.select_agents(next_event)
                })

        return predictions
```

### 6.2 Adaptive Agent Routing

Learn which agents perform best for different event types:

```python
class AdaptiveAgentRouter:
    """Routes to best-performing agents based on historical performance"""

    def __init__(self):
        self.performance_history = defaultdict(list)
        self.routing_model = self.train_routing_model()

    async def route(self, event: Event) -> BaseAgent:
        # Get agent recommendations
        features = self.extract_features(event)
        agent_scores = self.routing_model.predict(features)

        # Consider cost constraints
        for agent_id, score in agent_scores.items():
            agent = self.agents[agent_id]

            if self.within_budget(agent):
                # Use this agent and track performance
                result = await agent.process(event)
                self.track_performance(agent_id, event, result)
                return result

        # Fallback to cheapest agent
        return await self.cheapest_agent.process(event)

    def track_performance(self, agent_id: str, event: Event, result: Any):
        """Track agent performance for future routing decisions"""
        self.performance_history[agent_id].append({
            "event_type": event.kind,
            "accuracy": result.get("confidence", 0),
            "latency": result.get("latency", 0),
            "cost": result.get("cost", 0),
            "timestamp": datetime.now()
        })

        # Retrain routing model periodically
        if len(self.performance_history[agent_id]) % 100 == 0:
            self.routing_model = self.train_routing_model()
```

### 6.3 Event Graph Construction

Build a knowledge graph from events for deeper insights:

```python
class EventGraphBuilder:
    """Builds and queries a knowledge graph from events"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.embeddings = {}

    async def add_event(self, event: Event):
        # Add entities as nodes
        for entity in event.entities:
            self.graph.add_node(entity, type="entity")

        # Add claims as edges
        for claim in event.claims:
            if claim.get("structured"):
                s = claim["structured"]
                if s.get("actor") and s.get("object"):
                    self.graph.add_edge(
                        s["actor"],
                        s["object"],
                        predicate=s.get("predicate"),
                        event_id=event.event_id,
                        timestamp=event.created_at,
                        confidence=claim.get("confidence", 0.5)
                    )

        # Store embedding for semantic search
        self.embeddings[event.event_id] = await self.embed(event.summary)

    async def query_path(self, start: str, end: str, max_hops: int = 3):
        """Find connection between entities"""
        try:
            paths = list(nx.all_simple_paths(
                self.graph, start, end, cutoff=max_hops
            ))
            return self.rank_paths(paths)
        except nx.NetworkXNoPath:
            return []

    async def find_communities(self):
        """Detect communities of related entities"""
        communities = nx.community.louvain_communities(
            self.graph.to_undirected()
        )
        return [list(c) for c in communities]
```

### 6.4 Self-Improving System

System that learns from corrections and improves over time:

```python
class SelfImprovingPipeline:
    """Pipeline that learns from corrections"""

    def __init__(self):
        self.corrections = []
        self.improvement_agents = []

    async def process_with_learning(self, content: str) -> Event:
        # Normal processing
        event = await self.process(content)

        # Check for corrections from human review
        if corrections := self.get_pending_corrections(event.event_id):
            await self.learn_from_corrections(corrections)

        # Apply learned improvements
        event = await self.apply_improvements(event)

        return event

    async def learn_from_corrections(self, corrections: List[Dict]):
        """Learn from human corrections"""
        for correction in corrections:
            # Extract what went wrong
            error_type = self.classify_error(correction)

            # Create improvement rule
            rule = self.create_improvement_rule(
                error_type,
                correction["original"],
                correction["corrected"]
            )

            # Train agents on this example
            for agent in self.improvement_agents:
                await agent.add_training_example(
                    input=correction["original"],
                    expected=correction["corrected"],
                    error_type=error_type
                )

        # Retrain models if enough corrections accumulated
        if len(self.corrections) >= 100:
            await self.retrain_models()
```

### 6.5 Cross-Event Reasoning

Detect patterns and contradictions across multiple events:

```python
class CrossEventReasoner:
    """Reasons across multiple events to find insights"""

    async def find_contradictions(
        self,
        events: List[Event],
        time_window: timedelta
    ) -> List[Dict]:
        """Find contradicting claims within time window"""
        contradictions = []

        # Group events by entity
        entity_events = defaultdict(list)
        for event in events:
            for entity in event.entities:
                entity_events[entity].append(event)

        # Check for contradictions per entity
        for entity, entity_event_list in entity_events.items():
            claims = []
            for event in entity_event_list:
                for claim in event.claims:
                    claims.append({
                        "claim": claim,
                        "event_id": event.event_id,
                        "timestamp": event.created_at
                    })

            # Find contradicting claims
            for i, claim1 in enumerate(claims):
                for claim2 in claims[i+1:]:
                    if self.are_contradictory(claim1, claim2):
                        contradictions.append({
                            "entity": entity,
                            "claim1": claim1,
                            "claim2": claim2,
                            "confidence": self.contradiction_confidence(
                                claim1, claim2
                            )
                        })

        return contradictions

    async def find_causality(
        self,
        events: List[Event]
    ) -> List[Dict]:
        """Detect potential causal relationships"""
        causal_chains = []

        # Sort events by time
        sorted_events = sorted(events, key=lambda e: e.created_at)

        # Look for patterns
        for i, event1 in enumerate(sorted_events[:-1]):
            for event2 in sorted_events[i+1:]:
                # Check if events might be causally related
                if self.might_be_causal(event1, event2):
                    chain = {
                        "cause": event1.event_id,
                        "effect": event2.event_id,
                        "confidence": self.causal_confidence(event1, event2),
                        "time_delta": event2.created_at - event1.created_at,
                        "shared_entities": list(
                            set(event1.entities) & set(event2.entities)
                        )
                    }
                    causal_chains.append(chain)

        return causal_chains
```

---

## Part 7: Operational Considerations

### 7.1 Cost Management Strategy

```yaml
cost_tiers:
  tier_0:
    name: "Free/Regex"
    cost_per_1k: $0.00
    use_for: ["known_patterns", "simple_extraction"]

  tier_1:
    name: "Classical NLP"
    cost_per_1k: $0.01
    use_for: ["named_entity_recognition", "pos_tagging"]

  tier_2:
    name: "Local LLM"
    cost_per_1k: $0.10
    use_for: ["classification", "simple_reasoning"]

  tier_3:
    name: "Cloud LLM - Fast"
    cost_per_1k: $1.00
    use_for: ["complex_extraction", "structured_output"]

  tier_4:
    name: "Cloud LLM - Powerful"
    cost_per_1k: $10.00
    use_for: ["deep_reasoning", "creative_generation"]

escalation_rules:
  - if: confidence < 0.5
    then: escalate_one_tier
  - if: importance > 0.8
    then: use_tier_3_minimum
  - if: cost_today > daily_budget
    then: cap_at_tier_2
```

### 7.2 Monitoring & Observability

```python
class SystemMonitor:
    """Comprehensive monitoring for the entire system"""

    def __init__(self):
        self.metrics = {
            "events_processed": Counter(),
            "agents_executed": Counter(),
            "workflows_triggered": Counter(),
            "processing_latency": Histogram(),
            "cost_by_tier": Counter(),
            "errors_by_type": Counter()
        }

    async def dashboard_data(self) -> Dict:
        """Real-time dashboard data"""
        return {
            "current_rate": {
                "events_per_second": self.current_eps(),
                "agents_per_second": self.current_aps(),
                "cost_per_hour": self.current_cost_rate()
            },
            "daily_totals": {
                "events": self.metrics["events_processed"].daily(),
                "unique_entities": self.unique_entities_today(),
                "workflows_triggered": self.metrics["workflows_triggered"].daily(),
                "total_cost": self.total_cost_today()
            },
            "performance": {
                "p50_latency": self.metrics["processing_latency"].quantile(0.5),
                "p95_latency": self.metrics["processing_latency"].quantile(0.95),
                "error_rate": self.error_rate(),
                "escalation_rate": self.escalation_rate()
            },
            "top_entities": self.top_entities(10),
            "top_topics": self.top_topics(10),
            "active_workflows": self.active_workflows()
        }
```

### 7.3 Testing Strategy

```python
class TestingFramework:
    """Comprehensive testing for events and agents"""

    def __init__(self):
        self.golden_events = self.load_golden_set()
        self.test_scenarios = self.load_scenarios()

    async def test_extraction_accuracy(self):
        """Test event extraction accuracy"""
        results = []

        for golden in self.golden_events:
            # Process with pipeline
            extracted = await self.pipeline.process(golden["raw"])

            # Compare
            accuracy = self.compare_events(golden["expected"], extracted)
            results.append({
                "test_id": golden["id"],
                "accuracy": accuracy,
                "errors": self.find_errors(golden["expected"], extracted)
            })

        return {
            "mean_accuracy": np.mean([r["accuracy"] for r in results]),
            "failed_tests": [r for r in results if r["accuracy"] < 0.9],
            "by_category": self.group_by_category(results)
        }

    async def test_agent_consistency(self):
        """Ensure agents produce consistent results"""
        inconsistencies = []

        for scenario in self.test_scenarios:
            # Run same input multiple times
            results = []
            for _ in range(3):
                result = await self.agent.process(scenario["input"])
                results.append(result)

            # Check consistency
            if not self.are_consistent(results):
                inconsistencies.append({
                    "scenario": scenario["id"],
                    "results": results,
                    "variance": self.calculate_variance(results)
                })

        return inconsistencies

    async def test_cost_optimization(self):
        """Verify cost optimization is working"""
        test_batch = self.generate_test_batch(1000)

        # Process with optimization
        with_opt = await self.process_batch_with_optimization(test_batch)

        # Process without optimization (always use expensive models)
        without_opt = await self.process_batch_without_optimization(test_batch)

        return {
            "cost_savings": (without_opt["cost"] - with_opt["cost"]) / without_opt["cost"],
            "accuracy_delta": with_opt["accuracy"] - without_opt["accuracy"],
            "latency_improvement": without_opt["latency"] - with_opt["latency"]
        }
```

---

## Part 8: Deployment Architecture

### 8.1 Infrastructure Setup

```yaml
# terraform/main.tf structure
infrastructure:
  compute:
    - cloud_run:
        - event_processor
        - agent_executor
        - api_server
        - workflow_orchestrator

    - cloud_functions:
        - event_triggers
        - scheduled_tasks
        - webhook_handlers

  storage:
    - firestore:
        collections:
          - events
          - entities
          - workflows
          - tasks
        indexes:
          - entity_date
          - topic_date
          - workflow_status

    - gcs_buckets:
        - raw_content
        - processed_events
        - agent_artifacts
        - model_cache

    - bigquery:
        datasets:
          - analytics
          - edges
          - metrics

  messaging:
    - pubsub_topics:
        - event_ingestion
        - agent_tasks
        - workflow_triggers
        - system_alerts

  networking:
    - load_balancer:
        - api_endpoints
        - webhook_endpoints

    - vpc:
        - private_subnet
        - nat_gateway
```

### 8.2 Security Configuration

```yaml
security:
  authentication:
    - service_accounts:
        - event_processor@
        - agent_executor@
        - api_server@

    - api_keys:
        - stored_in: secret_manager
        - rotation: 90_days

  authorization:
    - iam_roles:
        - event_processor:
            - firestore.write
            - gcs.write
            - pubsub.publish

        - agent_executor:
            - firestore.read
            - secret_manager.read
            - aiplatform.predict

        - api_server:
            - firestore.read
            - bigquery.read

  network:
    - firewall_rules:
        - allow_webhooks
        - allow_api
        - deny_all_else

    - vpc_service_controls:
        - perimeter: production
        - restricted_services:
            - firestore
            - secret_manager
```

---

## Part 9: Migration Strategy from B3

### 9.1 Preservation Strategy

**Keep from B3**:
1. All base agent classes (OllamaAgent, GeminiAgent)
2. Node-based workflow system
3. Agent directory structure
4. Mini-nodes pattern
5. Configuration management via .env

**Simplify**:
1. Remove complex memory consolidation
2. Skip PostgreSQL/pgvector
3. Simplify entity resolution to basic canonicalization
4. Remove contradiction handling (make it a separate agent)

### 9.2 Migration Steps

```python
# Week 1: Port core agent classes
cp B3/agents/base_agent.py B4/agents/
cp B3/agents/ollama_agent.py B4/agents/
cp B3/agents/gemini_agent.py B4/agents/

# Week 2: Adapt workflow system for events
# Modify workflow executor to accept event triggers
# Add event-specific nodes

# Week 3: Integrate with new event pipeline
# Create EventProcessorAgent
# Create WorkflowTriggerAgent

# Week 4: Test and optimize
# Run parallel systems
# Compare outputs
# Optimize for cost/performance
```

---

## Part 10: Success Metrics & KPIs

### 10.1 Technical Metrics

```yaml
performance_kpis:
  latency:
    - p50_event_processing: < 500ms
    - p95_event_processing: < 2s
    - p50_agent_execution: < 1s
    - p95_agent_execution: < 5s

  throughput:
    - events_per_second: > 100
    - concurrent_workflows: > 50

  accuracy:
    - entity_extraction: > 90%
    - event_classification: > 85%
    - claim_extraction: > 80%

  cost:
    - cost_per_1k_events: < $5
    - daily_budget_adherence: 100%
    - optimization_savings: > 70%
```

### 10.2 Business Metrics

```yaml
business_kpis:
  coverage:
    - unique_entities_tracked: > 10,000
    - events_per_day: > 50,000
    - sources_integrated: > 10

  insights:
    - actionable_alerts_per_day: > 20
    - prediction_accuracy: > 70%
    - contradiction_detection: > 90%

  user_satisfaction:
    - api_uptime: > 99.9%
    - query_response_time: < 1s
    - brief_quality_score: > 4/5
```

---

## Part 11: Future Enhancements & Research Areas

### 11.1 Advanced Capabilities

1. **Multi-Modal Event Processing**
   - Image analysis from social media
   - Video event extraction
   - Audio transcription and analysis

2. **Federated Learning**
   - Learn from corrections without sharing raw data
   - Collaborate with other deployments
   - Privacy-preserving improvements

3. **Quantum-Ready Algorithms**
   - Prepare for quantum advantage in pattern matching
   - Design quantum-compatible search algorithms

4. **Neuromorphic Processing**
   - Event-driven processing inspired by brain architecture
   - Sparse, energy-efficient computation

### 11.2 Research Questions

1. **Optimal Agent Scheduling**
   - How to optimally schedule agents given cost/latency constraints?
   - Can we predict agent execution time from input characteristics?

2. **Emergent Intelligence**
   - Can simple agents compose to show emergent intelligence?
   - How to measure and encourage beneficial emergence?

3. **Causal Discovery**
   - Can we automatically discover causal relationships from events?
   - How to validate discovered causality?

4. **Temporal Reasoning**
   - How to reason about event sequences over time?
   - Can we predict event cascades?

---

## Part 12: Concrete Implementation Examples

### 12.1 Complete Event Processing Example

```python
# Full implementation of event processing from source to storage

async def process_news_article(url: str):
    """Complete pipeline for processing a news article"""

    # 1. Fetch and normalize
    raw_content = await fetch_article(url)
    normalized = normalize_text(raw_content)

    # 2. Quick extraction (free)
    quick_entities = regex_extract_entities(normalized)

    # 3. NLP extraction (cheap)
    nlp_result = await spacy_extract(normalized)

    # 4. Determine if we need LLM
    if confidence(nlp_result) < 0.7:
        # 5. Try local LLM first
        ollama_result = await ollama_agent.extract(
            normalized,
            context={"entities": quick_entities}
        )

        if ollama_result.confidence < 0.8:
            # 6. Use cloud LLM as last resort
            gemini_result = await gemini_agent.extract(
                normalized,
                schema=EVENT_SCHEMA,
                max_tokens=500
            )
            final_result = gemini_result
        else:
            final_result = ollama_result
    else:
        final_result = nlp_result

    # 7. Create event
    event = Event(
        event_id=generate_event_id(),
        kind=final_result.event_type,
        entities=final_result.entities,
        claims=final_result.claims,
        evidence_doc_ids=[store_raw(raw_content)],
        processing_agents=final_result.agents_used,
        created_at=datetime.now()
    )

    # 8. Store event
    await firestore.collection("events").document(event.event_id).set(
        event.dict()
    )

    # 9. Update indexes
    await update_posting_lists(event)

    # 10. Trigger workflows
    triggered = await workflow_executor.check_triggers(event)

    return {
        "event_id": event.event_id,
        "triggered_workflows": triggered,
        "processing_cost": calculate_cost(final_result)
    }
```

### 12.2 Complete Workflow Example

```python
# Implementation of a complex multi-agent workflow

class MarketAnalysisWorkflow:
    """Analyzes market-moving events with multiple agents"""

    def __init__(self):
        self.nodes = [
            EventClassifierNode(),
            EntityExtractorNode(),
            SentimentAnalysisNode(),
            MarketImpactPredictorNode(),
            AlertGeneratorNode()
        ]

        # Connect nodes
        for i in range(len(self.nodes) - 1):
            self.nodes[i].set_next(self.nodes[i + 1])

    async def execute(self, event: Event):
        """Execute the workflow"""
        context = {
            "event": event,
            "timestamp": datetime.now(),
            "confidence_threshold": 0.7
        }

        # Run through all nodes
        current_node = self.nodes[0]
        while current_node:
            try:
                # Execute node
                result = await current_node.execute(context)
                context.update(result)

                # Check if we should stop
                if context.get("stop_workflow", False):
                    break

                # Move to next
                current_node = current_node.next

            except Exception as e:
                # Handle errors gracefully
                context["error"] = str(e)
                context["failed_node"] = current_node.__class__.__name__
                break

        # Generate final output
        if not context.get("error"):
            if context.get("market_impact_score", 0) > 0.8:
                await self.send_alert(context)

        return context

class MarketImpactPredictorNode(BaseNode):
    """Predicts market impact of events"""

    def __init__(self):
        self.models = {
            "quick": OllamaAgent(model="gemma3:270m"),
            "accurate": GeminiAgent(model="gemini-2.0-flash")
        }

    async def execute(self, context: Dict) -> Dict:
        event = context["event"]

        # Determine which model to use
        if self.is_high_priority(event):
            model = self.models["accurate"]
        else:
            model = self.models["quick"]

        # Analyze impact
        prompt = self.build_analysis_prompt(event)
        result = await model.analyze(prompt)

        return {
            "market_impact_score": result.impact_score,
            "affected_sectors": result.sectors,
            "predicted_direction": result.direction,
            "confidence": result.confidence,
            "reasoning": result.reasoning
        }
```

### 12.3 Human-in-the-Loop (HITL) Correction Workflow

```python
# Example of a web endpoint for human corrections

class CorrectionAPI:
    """API for submitting and processing human corrections"""

    @app.post("/corrections")
    async def submit_correction(self, correction: Correction):
        """Receives a correction from a human reviewer"""

        # 1. Validate the correction
        if not await self.is_valid(correction):
            raise HTTPException(status_code=400, detail="Invalid correction data")

        # 2. Store the correction for auditing
        await db.corrections.insert_one(correction.dict())

        # 3. Trigger a learning workflow
        await workflow_executor.execute_workflow(
            workflow_id="self_improvement_workflow",
            initial_data={"correction": correction}
        )

        # 4. Immediately apply a high-priority fix if needed
        if correction.is_critical:
            await self.apply_hotfix(correction)

        return {"status": "Correction received and is being processed."}

    async def apply_hotfix(self, correction: Correction):
        """Applies a critical correction immediately"""
        # Example: Correct a misidentified entity in a recent event
        event = await db.events.find_one({"event_id": correction.event_id})
        if event:
            # Find and replace the incorrect entity
            corrected_entities = [
                correction.new_value if e == correction.old_value else e
                for e in event["entities"]
            ]
            await db.events.update_one(
                {"event_id": correction.event_id},
                {"$set": {"entities": corrected_entities, "last_corrected_by": "human_hotfix"}}
            )
```

---

## Part 13: Operational Tooling & Environments

### 13.1 Agent Sandbox Environment

To ensure safe development and testing, a sandboxed environment will be provided. This environment mirrors the production setup but uses mock data and isolated resources.

**Features**:
- **Isolated Data**: Runs on a separate, ephemeral Firestore instance.
- **Mock Services**: Mocks external APIs and services to prevent side-effects.
- **Resource Limits**: Strict CPU, memory, and cost limits are enforced.
- **"Dry Run" Mode**: Agents can be run in a "dry run" mode where they declare their intended actions without executing them.
- **Scenario Runner**: Allows developers to replay historical events or custom scenarios against their new agent to test its behavior.

```python
class AgentSandbox:
    """A context manager for safely testing agents"""

    def __init__(self, agent_code: str, scenario_id: str):
        self.agent_code = agent_code
        self.scenario = self.load_scenario(scenario_id)
        self.mock_db = MockFirestore()
        self.mock_gcs = MockGCS()

    async def __aenter__(self):
        # Set up the sandboxed environment
        self.original_db = db
        db.switch_to(self.mock_db)
        # ... mock other services
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Tear down the sandbox
        db.switch_to(self.original_db)

    async def run_test(self) -> Dict:
        """Runs the agent against the scenario and returns results"""
        agent = self.load_agent_from_code(self.agent_code)
        results = await agent.process(self.scenario['input'])
        
        # Compare results against expected output
        report = self.generate_report(results, self.scenario['expected'])
        return report
```

### 13.2 Dynamic Configuration Management

To allow for real-time adjustments without redeployment, system configurations will be stored in a centralized, dynamic configuration store (like Firestore or a dedicated service).

**Managed Configurations**:
- **Agent Settings**: Model names, system prompts, confidence thresholds.
- **Workflow Definitions**: Trigger conditions, node graphs, timeout settings.
- **Cost Controls**: Budgets, tier-locking rules, escalation policies.
- **Feature Flags**: Enable or disable experimental features on the fly.

A simple UI or CLI will be provided for administrators to update these configurations safely. All changes will be versioned and auditable.

```python
class DynamicConfig:
    """Provides access to dynamic system configuration"""

    def __init__(self):
        self.cache = {}
        self.last_updated = {}

    async def get(self, key: str, default: Any = None) -> Any:
        """Gets a configuration value, refreshing from source if stale"""
        if self.is_stale(key):
            self.cache[key] = await self.fetch_from_source(key)
        return self.cache.get(key, default)

    async def fetch_from_source(self, key: str) -> Any:
        """Fetches the latest config from Firestore"""
        doc = await db.configurations.document(key).get()
        if doc.exists:
            self.last_updated[key] = doc.update_time
            return doc.to_dict()['value']
        return None
```

---

## Part 14: Conclusion & Next Steps

This comprehensive blueprint merges the best aspects of B3's agent orchestration system with B4's lean event processing architecture. The result is a system that can:

1. **Efficiently process world information** through cost-aware waterfall processing
2. **Orchestrate intelligent agents** using hierarchical inheritance and composition
3. **Incorporate human feedback** through a dedicated HITL review and correction workflow
4. **Scale economically** by starting with cheap solutions and escalating only when needed
5. **Learn and improve** through feedback loops and performance tracking
6. **Provide actionable intelligence** through event-triggered workflows

### Immediate Action Items

1. **Week 1**: Set up basic infrastructure (including dynamic config store) and port core agent classes from B3.
2. **Week 2**: Implement event ingestion pipeline and the Agent Sandbox.
3. **Week 3**: Connect agents to events and implement first workflows.
4. **Week 4**: Build the first version of the HITL correction UI and API.
5. **Week 5**: Add intelligence features (importance scoring, entity resolution).
6. **Week 6**: Optimize for cost and performance, then deploy MVP and start collecting feedback.

### Key Success Factors

1. **Maintain Simplicity**: Start simple, add complexity only when proven necessary.
2. **Monitor Costs**: Track every token, optimize aggressively.
3. **Embrace the Loop**: Prioritize building and refining the human-in-the-loop feedback system.
4. **Focus on Value**: Prioritize features that provide immediate intelligence value.
5. **Iterate Quickly**: Ship early, get feedback, improve.
6. **Document Everything**: Clear documentation accelerates development.

This system represents a significant step forward in creating intelligent, reactive systems that can understand and respond to world events while maintaining operational efficiency and cost-effectiveness.

---

**Document Version**: 2.1
**Last Updated**: November 9, 2025
**Status**: Ready for Implementation
**Next Review**: Week 2 of implementation