# Pattern Filter - AI-Powered Interest Detection

## Overview

The Pattern Filter has been upgraded from simple regex matching to a sophisticated AI-powered interest detection system that identifies meaningful content across 14 categories of personal relevance.

## Architecture

### Components Created

1. **Interest Detector Agent** (`/backend/agents/agent_definitions/interest_detector/`)
   - `info.txt` - Agent metadata
   - `prompt.txt` - Comprehensive prompt with 14 interest categories
   - `structure_output.json` - Structured output schema

2. **Updated PatternFilterNode** (`/backend/modules/pattern_filter.py`)
   - Uses BaseAgent infrastructure
   - Lazy-loads the interest_detector agent
   - Processes input through Gemini AI
   - Returns structured output

## The 14 Interest Categories

1. **LIFE_EVENTS** - Personal life changes, moves, accidents
2. **WORK_OR_PROJECTS** - Project updates, decisions, deadlines
3. **OPENBOOK_RELATED** - Healthcare transparency, data pipelines, business strategy
4. **HEALTH_INFORMATION** - Symptoms, diagnoses, treatments, medications
5. **PEOPLE** - Updates about people's actions, roles, relationships
6. **ORGANIZATIONS** - Companies, hospitals, insurers, agencies
7. **PLACES** - Cities, addresses, destinations, travel
8. **TASKS** - To-dos, commitments, action items
9. **TECHNICAL_OR_SCIENTIFIC_KNOWLEDGE** - New concepts, methods, insights
10. **REFLECTION** - Thoughts, feelings, emotional insights
11. **FINANCE_OR_BUSINESS** - Money, investments, deals, budgets
12. **PLANS_OR_DECISIONS** - Future commitments, choices, intentions
13. **INSIGHTFUL_QUESTIONS** - Meaningful questions revealing knowledge needs
14. **OTHER_INSIGHT** - Any other informative or meaningful content

## Output Format

```json
{
  "interesting": [
    {
      "interesting_field": "PEOPLE",
      "interesting_score": 65,
      "reason": "John is moving to San Francisco.",
      "text_snippet": "He's moving to San Francisco next month"
    }
  ]
}
```

### Field Descriptions

- **interesting_field**: Category enum (one of the 14 categories)
- **interesting_score**: Confidence score 0-100
  - 80-100: Highly actionable, urgent, life-changing
  - 60-79: Important updates, decisions, meaningful insights
  - 40-59: Noteworthy information worth remembering
  - 20-39: Mildly interesting, contextual
  - 0-19: Barely relevant, trivial
- **reason**: Brief explanation of why it's interesting
- **text_snippet**: Relevant portion of text that triggered detection

## Test Results

Test input containing multiple categories detected **13 interesting items**:
- 3x OPENBOOK_RELATED (scores: 70, 60, 70)
- 2x PEOPLE (scores: 60, 65)
- 1x TASKS (score: 80)
- 1x WORK_OR_PROJECTS (score: 50)
- 1x REFLECTION (score: 50)
- 1x HEALTH_INFORMATION (score: 75)
- 1x FINANCE_OR_BUSINESS (score: 60)
- 1x PLANS_OR_DECISIONS (score: 40)
- 1x INSIGHTFUL_QUESTIONS (score: 70)
- 1x TECHNICAL_OR_SCIENTIFIC_KNOWLEDGE (score: 40)

## AI Model

- **Default Model**: `gemini-2.0-flash-exp`
- **Provider**: Google Gemini via GeminiAgent
- **Processing**: Structured output with JSON schema validation

## Integration

The Pattern Filter is integrated into the Memory Waterfall workflow as the first node after Text Input. It filters incoming information to identify what's worth processing through the rest of the pipeline.

## Usage

The node automatically loads and uses the AI agent. No configuration required - it works out of the box with the 14 predefined categories.

## Files Modified/Created

### Created:
- `/backend/agents/agent_definitions/interest_detector/info.txt`
- `/backend/agents/agent_definitions/interest_detector/prompt.txt`
- `/backend/agents/agent_definitions/interest_detector/structure_output.json`
- `/backend/test_pattern_filter.py` (test script)

### Modified:
- `/backend/modules/pattern_filter.py` (complete rewrite to use AI)

## Next Steps

The Pattern Filter now provides rich, structured output that can be used by downstream nodes:
- Context Builder can use the detected categories
- Entity Extractor can focus on mentioned people/organizations/places
- Memory Prioritizer can use the interesting_score for ranking
- Memory Writer can tag memories with detected categories
