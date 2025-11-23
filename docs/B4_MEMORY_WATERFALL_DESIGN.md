# B4 Memory Waterfall Architecture
## Simplified Neuroscience-Inspired Extraction Pipeline

*Version 1.0 - Designed for high-volume news processing with intelligent memory formation*

---

## 🧠 Core Philosophy

B4's Memory Waterfall combines B3's neuroscience-inspired approach with cost optimization for processing high-volume news inputs. It treats each input as passing through cognitive stages that mirror how the human brain processes and stores information.

**Key Principle**: "Filter Fast, Extract Smart, Connect Deep"

---

## 📊 Existing BigQuery Schema Integration

Based on your `brain_data` dataset, we have 18 tables that form the memory foundation:

### Core Memory Tables:
- **contexts**: Environmental and situational awareness
- **core_entities**: Universal entity registry with embeddings
- **events**: Episodic memory storage
- **people_core**: Person entity specialization
- **ideas**: Conceptual knowledge
- **hypotheses**: Uncertain connections and predictions
- **preferences**: Learned patterns and biases
- **projects**: Goal-oriented memory clusters
- **tasks**: Action items and intentions
- **entity_links**: Cross-references between entities
- **entity_resolutions**: Disambiguation records
- **knowledge_facts**: Atomic truth statements

---

## 🌊 The Memory Waterfall Pipeline

### Overview: 5-Stage Cognitive Waterfall

```
INPUT → ATTENTION → PERCEPTION → COMPREHENSION → CONSOLIDATION → INTEGRATION
   ↓        ↓           ↓              ↓                ↓              ↓
 Filter   Context    Extract       Connect          Store         Update
         Awareness   Elements      Meanings        Memory        Knowledge
```

---

### 🎯 Stage 1: ATTENTION FILTER
*"What deserves processing?"*

**Purpose**: Fast triage to avoid wasting resources on irrelevant content

**Processing Layers**:
```yaml
1.1 Relevance Gate:
  - Method: Regex patterns + keyword matching (FREE)
  - Filters:
    - Domain relevance (your interests/projects)
    - Language detection
    - Duplicate detection (hash comparison)
    - Spam/noise filtering
  - Output: PASS/SKIP decision + relevance_score

1.2 Importance Scorer:
  - Method: Classical NLP (spaCy) + rules (CHEAP)
  - Scores:
    - Temporal relevance (how recent/urgent)
    - Entity relevance (mentions known entities)
    - Topic relevance (matches tracked topics)
  - Output: importance_score (0-1)
```

**Decision**: Only items with relevance_score > 0.3 proceed

**BigQuery Tables Used**:
- READ: `core_entities` (for known entity matching)
- READ: `preferences` (for interest patterns)

---

### 🔍 Stage 2: PERCEPTION LAYER
*"What context are we in?"*

**Purpose**: Establish contextual understanding before extraction

**Processing Layers**:
```yaml
2.1 Context Builder:
  - Method: Pattern matching + Gemini Flash (CHEAP)
  - Extracts:
    - Source context (news site, social media, document type)
    - Temporal context (when published, time references)
    - Social context (author, audience, tone)
    - Domain context (tech, politics, personal, etc.)
  - Output: context_frame

2.2 Memory Priming:
  - Method: Vector similarity search (MODERATE)
  - Actions:
    - Find top-5 similar past contexts
    - Load related entities from memory
    - Prepare extraction hints
  - Output: memory_hints
```

**BigQuery Tables Used**:
- WRITE: `contexts` (new context record)
- READ: `contexts` (similar contexts via embedding)
- READ: `core_entities` (related entities)

---

### 🧩 Stage 3: COMPREHENSION ENGINE
*"What are the elements and their meanings?"*

**Purpose**: Extract structured information with understanding

**Parallel Extraction Streams**:

```yaml
3.1 Entity Stream (WHO/WHAT):
  Level 1: NER with spaCy (CHEAP)
    → People, Organizations, Products, Places
  Level 2: Gemini Flash for ambiguous (MODERATE)
    → Unnamed references, pronouns, roles
  Output: entity_candidates[]

3.2 Event Stream (WHAT HAPPENED):
  Level 1: Verb phrase extraction (CHEAP)
    → Action verbs + subjects/objects
  Level 2: Event templates (MODERATE)
    → Who did what to whom when where why
  Output: event_frames[]

3.3 Idea Stream (WHAT IT MEANS):
  Level 1: Key phrase extraction (CHEAP)
    → Technical concepts, definitions, claims
  Level 2: GPT-4 for complex ideas (EXPENSIVE - only if importance > 0.7)
    → Abstract concepts, implications, predictions
  Output: idea_concepts[]

3.4 Task Stream (WHAT TO DO):
  Level 1: Imperative detection (CHEAP)
    → Commands, deadlines, action items
  Level 2: Intent classification (MODERATE)
    → Implicit tasks, opportunities, warnings
  Output: task_items[]

3.5 Sentiment Stream (HOW IT FEELS):
  Level 1: Rule-based sentiment (FREE)
    → Positive/negative words
  Level 2: Contextual sentiment (CHEAP)
    → Sarcasm, nuance, stance
  Output: sentiment_signals[]
```

**Escalation Strategy**:
```python
def should_escalate(extraction, importance):
    if extraction.confidence < 0.5 and importance > 0.7:
        return True  # Important but uncertain
    if extraction.ambiguity_count > 3:
        return True  # Too many unknowns
    if "contradiction" in extraction.flags:
        return True  # Conflicts with memory
    return False
```

**BigQuery Tables Used**:
- READ: All tables for entity resolution
- PREPARE: Staged writes (not committed yet)

---

### 💡 Stage 4: CONSOLIDATION LAYER
*"How does it connect to what we know?"*

**Purpose**: Resolve entities, detect patterns, and form memories

**Processing Modules**:

```yaml
4.1 Entity Resolution:
  - Match extracted entities to existing records
  - Create placeholders for unknowns
  - Build confidence scores
  Actions:
    - Fuzzy matching on names/aliases
    - Context-based disambiguation
    - Relationship-based inference
  Output: resolved_entities{}

4.2 Hypothesis Generation:
  - When confidence < 0.7, generate hypotheses
  - Track multiple possibilities
  Examples:
    - "The CEO mentioned" → might be person_id_123
    - "Next quarter" → might be Q2 2025
  Output: hypothesis_set[]

4.3 Contradiction Detection:
  - Compare new facts vs existing knowledge
  - Flag conflicts for resolution
  Types:
    - Direct contradiction (A is B vs A is not B)
    - Temporal impossibility (can't be in two places)
    - Logical inconsistency (child older than parent)
  Output: contradictions[]

4.4 Pattern Recognition:
  - Identify recurring themes
  - Spot emerging trends
  - Connect related events
  Patterns:
    - Temporal (things happening in sequence)
    - Causal (A leads to B)
    - Structural (similar events, different contexts)
  Output: patterns[]
```

**Conflict Resolution Strategy**:
```python
if contradictions:
    if source_reliability > existing_reliability:
        update_fact()
    elif timestamp_new > timestamp_old:
        create_hypothesis("possible_update")
    else:
        flag_for_review()
```

**BigQuery Tables Used**:
- READ/WRITE: `entity_resolutions`
- WRITE: `hypotheses`
- READ/WRITE: `entity_links`

---

### 🔗 Stage 5: INTEGRATION LAYER
*"How do we remember this?"*

**Purpose**: Commit to long-term memory with proper indexing

**Storage Operations**:

```yaml
5.1 Memory Prioritization:
  Criteria:
    - Novelty (how new/different)
    - Importance (how relevant)
    - Connectivity (how many links)
  Decision:
    - Priority 1: Store immediately with full indexing
    - Priority 2: Store with basic indexing
    - Priority 3: Store compressed
    - Priority 4: Skip (not memorable)

5.2 Memory Writing:
  For each priority level:
    - Core entities → core_entities table
    - People → people_core + people_relationships
    - Events → events table
    - Ideas → ideas table
    - Tasks → tasks table
    - Facts → knowledge_facts
    - Context → contexts (already written)

5.3 Relationship Building:
  - Create bidirectional links
  - Update relationship strengths
  - Build knowledge graph edges
  Types:
    - Entity-to-Entity (person knows person)
    - Entity-to-Event (person attended meeting)
    - Entity-to-Idea (person proposed concept)
    - Event-to-Event (meeting led to decision)

5.4 Memory Indexing:
  - Generate embeddings for semantic search
  - Update inverted indexes
  - Refresh knowledge graph
  - Update statistics/counts
```

**Privacy & Access Control**:
```yaml
privacy_classifier:
  - Public: No restrictions
  - Professional: Work-related only
  - Personal: High security
  - Sensitive: Encrypted + audit log
```

**BigQuery Tables Written**:
- WRITE: All relevant tables based on extracted content
- UPDATE: Relationship tables
- UPDATE: Index tables

---

## 🎛️ Model Escalation Strategy

### Cost-Optimized Tier System

| Tier | Model | Cost/1M tokens | Use Case | Escalation Trigger |
|------|-------|----------------|----------|-------------------|
| 0 | Regex/Rules | $0 | Known patterns | Always try first |
| 1 | spaCy/NLP | $0.01 | Basic extraction | If pattern not found |
| 2 | Gemini Flash | $0.075 | Simple reasoning | If confidence < 0.6 |
| 3 | Gemini Pro | $1.25 | Complex extraction | If importance > 0.7 |
| 4 | GPT-4 | $10 | Deep reasoning | If critical + uncertain |

### Smart Escalation Rules

```python
class EscalationManager:
    def should_escalate(self, current_tier, extraction_result, context):
        # Never escalate if we're confident
        if extraction_result.confidence > 0.8:
            return False

        # Always escalate critical information
        if context.importance > 0.9 and current_tier < 3:
            return True

        # Escalate if too many unknowns
        if extraction_result.unknown_entities > 3:
            return True

        # Escalate if contradiction detected
        if extraction_result.contradictions:
            return True

        # Cost gate - don't escalate if over budget
        if self.daily_spend > self.daily_budget * 0.8:
            return False

        return extraction_result.confidence < 0.5
```

---

## 📈 Memory Formation Examples

### Example 1: Tech News Article

**Input**: "OpenAI announced GPT-5 will launch in March 2025 with improved reasoning"

**Waterfall Processing**:
```yaml
Stage 1 - Attention:
  - Relevance: 0.9 (AI topic, major announcement)
  - Importance: 0.8 (future event, industry impact)

Stage 2 - Perception:
  - Context: tech_news, future_event, product_launch
  - Memory hints: [GPT-4, OpenAI previous launches, AI models]

Stage 3 - Comprehension:
  - Entities: [OpenAI (org), GPT-5 (product)]
  - Event: {type: "announcement", subject: "OpenAI", action: "will launch", object: "GPT-5", time: "March 2025"}
  - Ideas: ["improved reasoning capability"]

Stage 4 - Consolidation:
  - Resolved: OpenAI → entity_id_openai
  - New: GPT-5 → create new entity
  - Hypothesis: GPT-5 reasoning > GPT-4 reasoning

Stage 5 - Integration:
  - Write: core_entities (GPT-5)
  - Write: events (product launch)
  - Write: knowledge_facts (GPT-5 launch date)
  - Link: OpenAI --develops--> GPT-5
```

### Example 2: Personal Message

**Input**: "Meeting with Sarah next Tuesday about the API project"

**Waterfall Processing**:
```yaml
Stage 1 - Attention:
  - Relevance: 0.8 (personal schedule)
  - Importance: 0.7 (upcoming commitment)

Stage 2 - Perception:
  - Context: personal_planning, work_related
  - Memory hints: [Sarah (colleague), API project (current)]

Stage 3 - Comprehension:
  - Entities: [Sarah (person), API project (project)]
  - Event: {type: "meeting", participants: ["self", "Sarah"], time: "next Tuesday", topic: "API project"}
  - Task: {action: "attend meeting", deadline: "next Tuesday"}

Stage 4 - Consolidation:
  - Resolved: Sarah → person_id_sarah_chen
  - Resolved: API project → project_id_api_v2

Stage 5 - Integration:
  - Write: events (meeting)
  - Write: tasks (attend meeting)
  - Update: projects (add meeting reference)
  - Link: Sarah --discusses--> API project
```

---

## 🔄 Feedback Loops

### Continuous Learning

```yaml
Daily Analysis:
  - Which extractions required escalation?
  - Which patterns appeared multiple times?
  - Which hypotheses were confirmed/rejected?

Weekly Optimization:
  - Adjust confidence thresholds
  - Update extraction patterns
  - Refine escalation rules

Monthly Evolution:
  - Retrain classifiers on corrected data
  - Update entity resolution rules
  - Optimize query patterns
```

### Self-Improvement Metrics

```python
class MemoryMetrics:
    def __init__(self):
        self.metrics = {
            'extraction_accuracy': [],  # How often we're right
            'escalation_rate': [],      # How often we need expensive models
            'resolution_confidence': [], # How sure we are about entities
            'memory_retrieval_relevance': [], # How useful retrieved memories are
            'contradiction_rate': [],   # How often we find conflicts
            'hypothesis_confirmation_rate': [] # How often guesses are right
        }

    def optimize_thresholds(self):
        # Adjust based on performance
        if avg(self.escalation_rate) > 0.3:
            lower_confidence_thresholds()  # Escalating too much
        if avg(self.extraction_accuracy) < 0.8:
            raise_confidence_thresholds()  # Need better accuracy
```

---

## 🚀 Implementation Priorities

### Phase 1: Core Pipeline (Week 1-2)
1. Implement Attention Filter with regex/keywords
2. Set up Context Builder with basic classification
3. Create Entity Extractor with spaCy
4. Build simple Entity Resolution with fuzzy matching
5. Implement BigQuery writers for core tables

### Phase 2: Intelligence (Week 3-4)
1. Add Memory Priming with vector search
2. Implement Event and Idea extractors
3. Build Hypothesis Generation
4. Create Contradiction Detection
5. Add Pattern Recognition

### Phase 3: Optimization (Week 5-6)
1. Implement smart model escalation
2. Add confidence scoring throughout
3. Build feedback loops
4. Optimize query patterns
5. Add performance monitoring

### Phase 4: Advanced Features (Week 7-8)
1. Implement relationship graph building
2. Add temporal reasoning
3. Create causal inference
4. Build preference learning
5. Add privacy classification

---

## 💰 Cost Projections

### Per 1000 News Articles

```yaml
Baseline (No Escalation):
  - Attention Filter: $0.00 (regex)
  - Context Builder: $0.08 (Gemini Flash)
  - Entity Extraction: $0.01 (spaCy)
  - Simple Storage: $0.00 (BigQuery)
  Total: ~$0.09

Typical (20% Escalation):
  - Baseline: $0.09
  - 200 escalations to Gemini Pro: $0.25
  - 50 escalations to GPT-4: $0.50
  Total: ~$0.84

Maximum (100% Escalation to GPT-4):
  - Everything through GPT-4: $10.00
  (This should never happen with proper filtering)
```

### Cost Optimization Strategies

1. **Batch Processing**: Group similar articles for batch extraction
2. **Caching**: Cache extracted entities for reuse
3. **Progressive Enhancement**: Only escalate uncertain parts, not whole documents
4. **Time-based Priorities**: Process important news immediately, others in batch
5. **Sampling**: For low-importance items, only extract samples

---

## 🔮 Future Enhancements

### Near-term (3 months)
- Multi-modal processing (images in news)
- Real-time streaming pipeline
- Automated knowledge graph visualization
- API for memory queries
- Integration with B3's deeper memory layers

### Long-term (6+ months)
- Predictive memory (anticipate what will be important)
- Dream consolidation (offline memory reorganization)
- Emotional memory tagging
- Episodic memory replay
- Cross-language memory formation

---

## 📝 Summary

This simplified B4 Memory Waterfall provides:

1. **Neuroscience-inspired stages** that mirror human cognition
2. **Cost optimization** through intelligent escalation
3. **Rich memory formation** using your existing BigQuery schema
4. **Scalability** for high-volume news processing
5. **Intelligence** through pattern recognition and hypothesis generation

The key insight is treating memory formation as a **progressive enhancement process** where we:
- Start with the cheapest extraction methods
- Only escalate when uncertain about important information
- Build rich connections between memories
- Learn from patterns to improve over time

This design balances the sophistication of B3's memory model with B4's need for cost-effective, high-volume processing.