# B3 Project Summary

## Executive Overview

B3 is a comprehensive "Second Brain" knowledge management system that combines n8n workflows, relational databases, AI agent systems, and memory processing to create a human-like cognitive architecture for capturing, storing, and recalling conversational memory.

**Key Philosophy**: Build a memory-first system that mimics human cognition - from perception through disambiguation to long-term consolidation and recall.

---

## Core Components

### 1. **Backend Service** (`/backend/`)
- **FastAPI-based** webhook server deployed to Google Cloud Run
- Handles Telegram message ingestion via webhooks
- Integrates with the workflow execution system
- **Key File**: `backend/app/main.py`
- **Endpoints**: `/telegram/webhook`

### 2. **Workflow System** (`/workflows/`)
- **Python-based node workflow architecture** (similar to n8n but in pure Python)
- Node-based composition: Input → AI Processing → Output
- **Main Workflow**: `main_telegram_chat`
  - Flow: Telegram Input → Gemma AI Agent → Telegram Output
- **Executor**: Manages workflow registration and execution
- **Files**: `executor.py`, `nodes/` directory

### 3. **Agent Hierarchy** (`/agents/`)
- **Two-tier agent architecture**: Base agents + Specialized agents
- **Base Agents**:
  - `OllamaAgent` - Local AI (fast, free, private) - Recommended for simple tasks
  - `GeminiAgent` - Cloud AI (complex reasoning, latest knowledge)
  - `BaseAgent` - Kingdom framework (full-featured multi-agent system)
- **Structured directory pattern**: Each agent gets its own folder with `agent.py`, `config.yaml`, `prompt.txt`, `README.md`
- **Inheritance-based**: Specialized agents inherit from base agents
- **Single source of truth**: API keys in `.env` file

### 4. **Memory Architecture** (Brain System)
- **Comprehensive node-based memory pipeline** mimicking human cognition:
  - **Perception Layer**: News intake, conversation capture, web scraping, file ingestion
  - **Processing Layer**: Language detection, segmentation, entity extraction (people, orgs, places, events, relations)
  - **Disambiguation Layer**: Candidate generation, entity resolution, place disambiguation
  - **Valuation Layer**: Novelty estimation, importance classification, privacy classification
  - **Contradiction Handling**: Confusion manager, evidence seeker, contradiction monitor
  - **Consolidation**: Upsertor, embedder, profile summarizer
  - **Recall**: Hybrid search (SQL + vector), reasoning

### 5. **Database Schema** (`/brain/`)
- **PostgreSQL + pgvector** for relational + semantic storage
- **Core Tables**:
  - `entity` - Universal entity table (people, orgs, places, events, concepts)
  - `person`, `person_alias`, `org`, `employment`
  - `place` (with geography support)
  - `event`, `event_participant`
  - `relationship` - Typed edges (friend_of, parent_of, works_at, etc.)
  - `assertion` - Facts/claims with confidence, time validity, and provenance
  - `source` - Provenance tracking
  - `message`, `mention` - Raw text and entity mentions
- **Indexes**: GIN for text search, HNSW for vector similarity
- **Features**: Entity disambiguation, placeholder management, merge suggestions

### 6. **Connectors** (`/connectors/`)
- External platform integrations
- **Telegram** connector for messaging

### 7. **Shared Utilities** (`/shared/`)
- Common utilities and helper functions
- Reusable across all components

---

## Key Architecture Patterns

### Hierarchical Agent Development
- **Base → Specialized**: Create base agents with core functionality, extend with specialized behavior
- **Example**:
  ```python
  from gemini_agent import GeminiAgent

  class ChatAgent(GeminiAgent):
      def __init__(self):
          super().__init__(system_prompt="You are a friendly chatbot...")

      def chat(self, message):
          return self.get_response(message)
  ```

### Node-Based Workflow Composition
- **Modular Nodes**: Each node has a single responsibility
- **Chaining**: Nodes link together via `set_next_node()`
- **Async Execution**: All nodes use `async def execute()`
- **Example Flow**: TelegramInput → GemmaAgent → TelegramOutput

### Mini-Nodes (Pluggable Components)
- **Model Mini-Nodes**: Swappable AI models (Gemini, Gemma, GPT, Claude)
- **Structure Mini-Nodes**: Define output schemas
- **Benefits**: Reusability, flexibility, DRY principle
- **Example**:
  ```python
  AIAgentNode(
      model=GeminiMiniNode(model="gemini-2.0-flash"),
      structure=StructureMiniNode(schema={"category": "string"})
  )
  ```

### Memory Processing Pipeline (4 Steps)
1. **Entity Extraction** - LLM-based structured extraction from natural language
2. **Entity Linking** - Connect to existing database records via candidates + resolution
3. **Importance Assessment** - Filter and prioritize with novelty + importance scoring
4. **Knowledge Base Update** - Store with vector embeddings and provenance

### Cost-Aware Model Routing (Cascade + MoE)
- **Tier System**:
  - `quick` = Ollama Gemma3:270m (local) or Gemini 2.5 Flash
  - `standard` = OpenAI GPT-4.1 or Gemini 2.5 Pro
  - `deep` = GPT-5 (span-only escalation for hard cases)
- **Strategy**: Start cheap, escalate only struggling fields, never blanket heavy-model passes
- **Field-level escalation**: Only re-process low-confidence spans with better models

---

## Design Principles

1. **Modularity**: Each agent/node is self-contained and independently usable
2. **Inheritance**: Specialized agents inherit from base agents
3. **Single Source of Truth**: Centralized configuration (API keys in `.env`)
4. **Simplicity**: Each component does one thing well
5. **Node-based & Composable**: Strict I/O contracts, blackboard working memory
6. **Predictive Coding**: Memory probes bias perception (priors guide extractors)
7. **Union-then-Resolve**: Extract in parallel, fuse via constraints and confidence
8. **Confusion is a Feature**: Detect contradictions, open tickets, seek evidence
9. **Privacy by Design**: Sensitive attributes guarded, redaction at read time
10. **Idempotent Writes & Provenance**: Every fact has a source

---

## Technology Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL + pgvector
- **Local AI**: Ollama (Gemma3:270m, Gemma3:1b)
- **Cloud AI**: Google Gemini (2.0 Flash, 2.5 Pro), OpenAI GPT-4.1
- **Messaging**: Telegram Bot API
- **Deployment**: Google Cloud Run
- **Language**: Python (async/await)
- **Workflow**: Custom Python node-based system (inspired by n8n)

---

## Key Files & Locations

### Agent Development
- **Base Agents**: `/ollama_agent.py`, `/gemini_agent.py`
- **Agent Structure**: `/agents/{agent_name}/agent.py`
- **Example**: `/agents/classifier/agent.py`

### Workflow System
- **Executor**: `/workflows/executor.py`
- **Nodes**: `/workflows/nodes/`
  - `base_node.py` - Abstract base
  - `telegram_input.py` - Telegram receiver
  - `gemma_agent.py` - Ollama AI processing
  - `telegram_output.py` - Telegram sender
- **Mini-Nodes**: `/workflows/mini_nodes/`

### Backend
- **Main**: `/backend/app/main.py`
- **Endpoints**: `/backend/app/endpoints/telegram.py`
- **Docker**: `/backend/Dockerfile`

### Configuration
- **Environment**: `/.env` (API keys, database credentials)
- **Example**: `/.env.example`

### Documentation
- **Main Docs**: `/docs/`
  - `README.md` - Project overview
  - `hierarchy_of_agents.md` - Agent architecture (comprehensive!)
  - `new_mastePlan.md` - Memory system blueprint
  - `local_development_guide.md`
  - `testing_guide.md`

---

## Development Workflow

### Creating a New Agent

1. **Choose Base Agent**:
   - Use `OllamaAgent` for simple, fast, local tasks (recommended for most tasks)
   - Use `GeminiAgent` for complex reasoning or latest knowledge
   - Use `BaseAgent` for complex Kingdom system agents

2. **Create Agent Directory**:
   ```
   agents/your_agent_name/
   ├── agent.py           # REQUIRED: Main agent class
   ├── config.yaml        # Optional: Configuration
   ├── prompt.txt         # Optional: System prompt
   └── README.md          # REQUIRED: Documentation
   ```

3. **Implement Agent Class**:
   ```python
   from gemini_agent import GeminiAgent

   class YourAgent(GeminiAgent):
       def __init__(self):
           super().__init__(system_prompt="You are a ...")

       def process_task(self, task_data):
           result = self.get_response(task_data)
           return result
   ```

4. **Document**: Update agent README and `/docs/hierarchy_of_agents.md`

### Creating a Workflow

1. **Create Nodes**:
   ```python
   from workflows.nodes.base_node import BaseNode

   class MyProcessorNode(BaseNode):
       async def execute(self, data):
           # Process data
           data["processed"] = True
           return data
   ```

2. **Register Workflow**:
   ```python
   from workflows.executor import executor

   executor.register_workflow(
       workflow_id="custom_workflow",
       nodes=[input_node, processor_node, output_node],
       description="My custom workflow"
   )
   ```

3. **Execute**:
   ```python
   result = await executor.execute_workflow(
       workflow_id="custom_workflow",
       input_data=data
   )
   ```

### Local Development

```bash
# Start Ollama (for local AI)
# Ollama runs on localhost:1112

# Start backend
cd backend
python app/main.py

# Test workflow
python workflows/executor.py

# Test agent
python agents/your_agent/agent.py
```

---

## Agent Decision Guide

### When to Use Ollama (OllamaAgent)
✅ Simple classification tasks
✅ Data validation
✅ Basic Q&A
✅ Entity extraction
✅ Text formatting
✅ Quick responses needed
✅ Cost-sensitive applications
✅ Privacy-critical tasks

**Why**: Free, fast (especially gemma3:270m), private, no API key needed

### When to Use Gemini (GeminiAgent)
✅ Complex reasoning tasks
✅ Latest information needed
✅ Long conversations
✅ Detailed analysis
✅ Creative content generation

**Why**: More capable, better at complex reasoning, longer context, free tier available

### When to Use BaseAgent (Kingdom Framework)
✅ Multi-agent coordination
✅ Code execution
✅ Memory management
✅ Complex workflows

**Why**: Full-featured agent system with brain, hands, memory, communication

---

## Memory System Concepts

### Entity Resolution
- **Candidate Generation**: Find potential matches via name/alias, attributes, relationships, vector similarity
- **Entity Resolver**: Decide match/new/unsure; emit placeholder when unknown
- **Placeholders**: Anonymous entities awaiting merge with real identity
- **Merge Suggester**: Propose winner/loser pairs for consolidation

### Contradiction Handling
- **Monitor**: Detect conflicts (e.g., "hates gym" vs "goes to gym")
- **Confusion Manager**: Open hypotheses with confidence intervals
- **Evidence Seeker**: Plan targeted queries to resolve contradictions
- **Settlement**: Store competing claims with time/polarity; settle using most recent, high-confidence observations

### Hybrid Search
- **Blend**: SQL filters + relationship traversals + vector similarity
- **Example**: "Who is Jason's African-American female friend?" combines attribute filters, relationship graph, and semantic search

### Provenance Tracking
- Every assertion/edge/event references `source_id`
- Maintains audit trail of where information came from
- Enables confidence timelines and superseding of old claims

---

## Configuration Management

### Environment Variables (`.env`)
```bash
GEMINI_API_KEY="AIzaSy..."
OPENAI_API_KEY="sk-proj-..."
DATABASE_URL="postgresql://..."
```

### Agent API Keys
- **Ollama**: No API key needed! (local)
- **Gemini**: `GEMINI_API_KEY` from `.env`
- **OpenAI**: `OPENAI_API_KEY` from `.env`

**Rule**: Never hardcode API keys. Always use environment variables.

---

## Testing

### Agent Testing
```python
if __name__ == "__main__":
    agent = YourAgent()
    result = agent.main_method("test input")
    print(f"Result: {result}")
    if 'metrics' in result:
        print(f"Tokens used: {result['metrics']['total_tokens']}")
```

### Workflow Testing
```bash
python workflows/executor.py
```

### Integration Testing
- Send message to Telegram bot
- Verify webhook reception
- Check workflow execution
- Confirm response delivery

---

## Deployment

### Backend Deployment (Google Cloud Run)
```bash
cd backend
sh deploy.sh
```

### Telegram Webhook Setup
```bash
python setup_telegram_webhook.py
```

### Considerations
- **Local Dev**: Ollama works perfectly (localhost:1112)
- **Cloud Run**: Can't access localhost - need to deploy Ollama as separate service or use Gemini instead

---

## Best Practices

### DO:
✅ Keep agents simple and focused
✅ Use inheritance to avoid code duplication
✅ Use environment variables for configuration
✅ Track metrics (tokens, cost, performance)
✅ Document your agents
✅ Test agents independently
✅ Handle errors gracefully
✅ Default to Ollama for simple tasks (faster and free)
✅ Use field-level escalation (not whole-doc reprocessing)
✅ Record provenance for all facts

### DON'T:
❌ Hardcode API keys
❌ Create monolithic agents that do everything
❌ Duplicate base functionality
❌ Skip error handling
❌ Forget to update documentation
❌ Over-engineer simple solutions
❌ Use heavy models for simple tasks
❌ Erase conflicting data (supersede instead)

---

## Roadmap (from B3)

1. **People Memory MVP** - Webhook → extraction → Postgres upsert → response
2. **Places Extension** - Attach place knowledge and maintain links from people
3. **Context Retrieval** - Fetch chat history, relevant people, optional documents before extraction
4. **Vector & Analytics Layer** - Connect embeddings and build summarization/recall endpoints

---

## Key Insights for B4

### What to Keep (Essential Patterns)
1. **Hierarchical Agent Architecture** - Base agents + inheritance model
2. **Node-based Workflow Composition** - Modular, composable nodes with strict I/O
3. **Cost-aware Model Routing** - Start cheap (Ollama), escalate only when needed
4. **Mini-Nodes Pattern** - Pluggable components (model, structure, context)
5. **Agent Directory Structure** - Standardized folder layout per agent
6. **Configuration Management** - Single source `.env` file

### What to Simplify for B4
1. **Skip Complex Memory System** - No entity resolution, contradiction handling, evidence seeking
2. **Skip Database Layer** - No PostgreSQL, pgvector, complex schema
3. **Skip Memory Consolidation** - No upsertor, embedder, merge suggester
4. **Focus on Workflow + Agents** - Keep the execution model, drop the memory persistence

### Core B4 Focus
- **Fast agent development** via hierarchical inheritance
- **Simple workflow orchestration** with node composition
- **Cost-effective AI** with Ollama-first approach
- **Pluggable architecture** using mini-nodes
- **Clean abstractions** without memory complexity

---

## File Count & Complexity

B3 is a **comprehensive system** with:
- 54 files in root directory
- Extensive docs (60+ markdown files)
- Complex memory pipeline (30+ node types)
- Full database schema with 15+ tables
- Multiple agent types and specializations
- Production deployment infrastructure

**B4 Goal**: Reduce to core patterns that enable fast agent and workflow development without the memory persistence complexity.

---

## Summary

B3 represents a **full-stack second brain** implementation with human-like memory processing. It demonstrates:
- How to build hierarchical agent systems
- How to compose node-based workflows
- How to handle entity resolution and disambiguation
- How to manage contradictions and evidence
- How to route across models cost-effectively
- How to maintain provenance and privacy

For **B4**, we extract the **development velocity patterns** (hierarchical agents, node composition, mini-nodes, cost-aware routing) while **dropping the memory persistence layer** to create a simpler, faster system focused on agent orchestration rather than knowledge management.

---

**Document Created**: 2025-11-02
**Source**: B3 Project Analysis
**Purpose**: Foundation document for B4 simplified implementation
