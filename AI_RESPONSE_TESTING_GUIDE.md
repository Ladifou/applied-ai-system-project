# AI Response Testing & Evaluation Guide

## Overview

This guide documents a comprehensive test suite for evaluating AI-generated responses in the PawPal+ system. The tests cover **38 different evaluation criteria** across explanation generation, task recommendations, response quality, error handling, and integration scenarios.

---

## Test Suite Structure

### 1. **TestExplanationGeneratorQuality** (8 tests)
Tests that evaluate the quality of AI-generated scheduling explanations.

| Test | Purpose |
|------|---------|
| `test_explanation_is_not_empty` | Ensures explanations are generated (not null/empty) |
| `test_explanation_mentions_task_name` | Verifies explanations reference task context |
| `test_explanation_mentions_priority` | Checks that priority levels are acknowledged |
| `test_explanation_mentions_task_type_context` | Confirms task-specific context (e.g., "nutrition" for feeding) |
| `test_explanation_handles_unscheduled_tasks` | Tests graceful handling of unscheduled tasks |
| `test_explanation_is_reasonably_concise` | Validates conciseness (<1000 chars) |
| `test_schedule_summary_contains_all_scheduled_tasks` | Ensures multi-task summaries are complete |
| `test_explanation_respects_owner_preferences` | Checks that owner preferences are acknowledged |

**What it validates:**
- ✅ Response generation completeness
- ✅ Content relevance and accuracy
- ✅ Tone appropriateness (conversational, friendly)
- ✅ Context awareness (pet, owner, schedule details)

---

### 2. **TestTaskRecommenderQuality** (10 tests)
Tests that evaluate the quality of task recommendations.

| Test | Purpose |
|------|---------|
| `test_recommendations_are_not_empty` | Ensures recommendations are generated |
| `test_recommendations_have_required_fields` | Validates all required fields present |
| `test_recommendations_have_valid_task_types` | Checks task types are standardized |
| `test_recommendations_have_valid_priorities` | Validates priority levels |
| `test_recommendations_have_valid_frequencies` | Validates frequency values |
| `test_recommendations_have_confidence_scores` | Ensures confidence scores exist (0-1 range) |
| `test_recommendations_are_pet_type_specific` | Verifies pet-type-aware recommendations |
| `test_recommendations_consider_pet_age` | Checks age-appropriate recommendations |
| `test_recommendation_confidence_reflects_relevance` | Validates confidence score variation |
| `test_recommendation_ranking_by_score` | Ensures stable, reproducible ranking |

**What it validates:**
- ✅ Structured output format
- ✅ Field completeness and validity
- ✅ Pet-specific personalization
- ✅ Ranking consistency

---

### 3. **TestResponseFormatAndParsing** (5 tests)
Tests that validate response format, structure, and parsing.

| Test | Purpose |
|------|---------|
| `test_prompt_templates_are_valid` | Ensures prompt templates format correctly |
| `test_recommendation_prompt_format` | Validates recommendation prompt generation |
| `test_llm_response_parsing_with_valid_format` | Tests parsing of well-formatted responses |
| `test_llm_response_parsing_fallback` | Validates fallback handling for malformed responses |
| `test_recommendation_field_normalization` | Checks field normalization (case, formatting) |

**What it validates:**
- ✅ Prompt template correctness
- ✅ Response parsing robustness
- ✅ Data normalization
- ✅ Graceful degradation

---

### 4. **TestErrorHandlingAndFallback** (4 tests)
Tests that verify error handling and graceful fallback mechanisms.

| Test | Purpose |
|------|---------|
| `test_explanation_generator_without_llm` | Tests fallback when LLM unavailable |
| `test_task_recommender_without_llm` | Validates fallback recommendations |
| `test_fallback_explanation_has_required_content` | Ensures fallback explanations are meaningful |
| `test_default_recommendations_are_complete` | Checks default recommendations have all fields |

**What it validates:**
- ✅ Graceful degradation without LLM
- ✅ Fallback mechanism completeness
- ✅ Error recovery
- ✅ Default behavior quality

---

### 5. **TestPromptGuardrails** (4 tests)
Tests that validate input validation and safety guardrails.

| Test | Purpose |
|------|---------|
| `test_pet_care_queries_are_valid` | Ensures valid pet queries pass validation |
| `test_off_topic_queries_are_rejected` | Verifies off-topic queries are rejected |
| `test_vague_queries_validation` | Tests rejection of vague non-pet queries |
| `test_mixed_content_queries` | Validates mixed relevant/irrelevant content |

**What it validates:**
- ✅ Input relevance filtering
- ✅ Safety guardrails effectiveness
- ✅ Appropriate scope enforcement

---

### 6. **TestIntegrationScenarios** (4 tests)
Integration tests with realistic multi-pet and multi-task scenarios.

| Test | Purpose |
|------|---------|
| `test_multi_pet_schedule_with_explanations` | Tests explanations across multiple pets |
| `test_recommendation_ranking_prioritizes_pet_needs` | Validates ranking in real scenarios |
| `test_full_schedule_summary_generation` | Tests complete schedule with all explanations |
| `test_recommendation_considers_existing_tasks` | Ensures recommendations respect current tasks |

**What it validates:**
- ✅ End-to-end workflow functionality
- ✅ Multi-pet coordination
- ✅ Real-world scenario handling

---

### 7. **TestResponseCoherence** (3 tests)
Tests that validate response consistency and coherence.

| Test | Purpose |
|------|---------|
| `test_recommendation_consistency` | Ensures deterministic recommendations |
| `test_explanation_consistency` | Validates consistent explanations for same task |
| `test_recommendation_fields_consistency` | Checks internal field consistency |

**What it validates:**
- ✅ Response determinism
- ✅ Consistency across calls
- ✅ Internal coherence

---

## Running the Tests

### Run all tests:
```bash
pytest tests/test_ai_response_evaluation.py -v
```

### Run specific test class:
```bash
pytest tests/test_ai_response_evaluation.py::TestExplanationGeneratorQuality -v
```

### Run specific test:
```bash
pytest tests/test_ai_response_evaluation.py::TestTaskRecommenderQuality::test_recommendations_are_pet_type_specific -v
```

### Run with detailed output:
```bash
pytest tests/test_ai_response_evaluation.py -v --tb=short
```

### Generate coverage report:
```bash
pytest tests/test_ai_response_evaluation.py --cov=ai_services --cov-report=html
```

---

## Test Coverage Summary

**Total Tests:** 38 ✅

| Category | Tests | Status |
|----------|-------|--------|
| Explanation Quality | 8 | ✅ |
| Recommendation Quality | 10 | ✅ |
| Format & Parsing | 5 | ✅ |
| Error Handling | 4 | ✅ |
| Input Validation | 4 | ✅ |
| Integration | 4 | ✅ |
| Coherence | 3 | ✅ |

---

## Quality Metrics Tested

### Response Quality Dimensions
1. **Relevance** - Does the response address the question?
2. **Accuracy** - Does it align with pet/owner data?
3. **Completeness** - Does it include all necessary information?
4. **Conciseness** - Is it appropriately brief?
5. **Coherence** - Is it well-structured?
6. **Tone** - Is it appropriately friendly/professional?
7. **Consistency** - Are multiple calls consistent?

### Format Validation
1. ✅ Required fields present
2. ✅ Valid field values (from enumerated sets)
3. ✅ Proper data types
4. ✅ Correct range constraints (e.g., confidence 0-1)
5. ✅ Parseable structure

### Personalization Validation
1. ✅ Pet-type aware
2. ✅ Age-appropriate
3. ✅ Owner-preference aware
4. ✅ Context-aware scheduling

---

## Extending the Test Suite

### Adding New Tests for ExplanationGenerator

```python
def test_explanation_includes_owner_name(self):
    """Test that explanations can personalize to owner."""
    generator = ExplanationGenerator(use_llm=False)
    explanation = generator.generate_task_explanation(self.task, self.schedule, self.owner)
    
    # Your assertion
    self.assertIn("Sarah", explanation)  # Owner name
```

### Adding New Tests for TaskRecommender

```python
def test_recommendations_avoid_duplicates(self):
    """Test that recommendations don't duplicate existing tasks."""
    recommender = TaskRecommender(use_llm=False)
    recommendations = recommender.recommend_tasks(self.pet, self.owner)
    
    # Check for duplicates
    task_names = [r.get("task_name") for r in recommendations]
    self.assertEqual(len(task_names), len(set(task_names)))
```

### Adding Integration Tests

```python
def test_e2e_schedule_generation_with_recommendations(self):
    """Test complete flow: schedule → explanations → recommendations."""
    # Setup
    scheduler = Scheduler("test_scheduler", self.pet)
    schedule = scheduler.generate_daily_plan(datetime.now())
    
    # Generate explanations
    explanation_gen = ExplanationGenerator(use_llm=False)
    summary = explanation_gen.generate_schedule_summary(schedule, self.owner)
    
    # Generate recommendations
    recommender = TaskRecommender(use_llm=False)
    recommendations = recommender.recommend_tasks(self.pet, self.owner)
    
    # Assertions
    self.assertIsNotNone(summary)
    self.assertGreater(len(recommendations), 0)
```

---

## Configuration & Dependencies

### Required Imports
```python
import unittest
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, TaskType, Scheduler
from ai_services import ExplanationGenerator, TaskRecommender
from prompts_manager import PromptManager, PromptGuardrails
```

### Test Fixtures Setup
Tests use standard fixtures:
- **Owner**: Test owner with preferences and pets
- **Pet**: Test pet (dog, cat) with various ages
- **Task**: Scheduled/unscheduled tasks
- **Scheduler**: Daily schedule generator

---

## Common Test Patterns

### Pattern 1: Basic Generation Test
```python
def test_something_is_generated(self):
    generator = ExplanationGenerator(use_llm=False)
    result = generator.generate_task_explanation(task, schedule, owner)
    self.assertIsNotNone(result)
    self.assertGreater(len(result), 0)
```

### Pattern 2: Field Validation Test
```python
def test_fields_are_valid(self):
    valid_values = {"high", "medium", "low"}
    for rec in recommendations:
        priority = rec.get("priority", "").lower()
        self.assertIn(priority, valid_values)
```

### Pattern 3: Integration Test
```python
def test_full_workflow(self):
    # Setup
    scheduler = Scheduler("id", pet)
    schedule = scheduler.generate_daily_plan(date)
    
    # Generate
    generator = ExplanationGenerator(use_llm=False)
    summary = generator.generate_schedule_summary(schedule, owner)
    
    # Validate
    self.assertIsNotNone(summary)
```

---

## Debugging Failed Tests

### Test Output Interpretation
```
FAILED test_example - AssertionError: False is not true : Custom message
```

**Steps to debug:**
1. Read the assertion message carefully
2. Check the test output for captured stdout/stderr
3. Review the actual vs expected values
4. Run the test in isolation: `pytest tests/test_ai_response_evaluation.py::TestClass::test_name -v -s`
5. Add print statements to understand data flow

### Common Failure Patterns

| Pattern | Cause | Solution |
|---------|-------|----------|
| Empty explanation | LLM disabled + no fallback | Ensure `use_llm=False` uses rule-based generation |
| Invalid field values | Parsing error | Check LLM response format |
| Consistency failure | Non-deterministic behavior | Remove randomness or mock random |
| Missing fields | Incomplete recommendation | Validate before returning |

---

## Performance Considerations

### Test Execution Time
- **Full suite (38 tests):** ~1-2 seconds
- **No LLM calls:** Uses fallback mechanisms for speed
- **Parallel execution:** Can run tests in parallel safely

### Optimization Tips
1. Use `use_llm=False` to skip API calls during testing
2. Reuse fixtures when possible
3. Mock external services if needed
4. Use `unittest.TestCase` for speed over async frameworks

---

## Future Enhancements

### Potential Areas for Extended Testing
- [ ] LLM response quality when API is available
- [ ] Latency/performance benchmarks
- [ ] Recommendation diversity metrics
- [ ] Explanation readability scores
- [ ] Multi-language support
- [ ] Edge case stress testing
- [ ] Load testing with many pets/tasks
- [ ] A/B testing different prompts

---

## Related Files

- `ai_services.py` - Main AI service implementations
- `prompts_manager.py` - Prompt templates and validation
- `pawpal_system.py` - Core scheduling system
- `tests/test_pawpal.py` - Scheduling system tests

---

## Contact & Support

For test-related questions or to report issues:
1. Review this guide for similar patterns
2. Check test output messages
3. Refer to docstrings in test methods
4. Examine fixture setup in each test class

