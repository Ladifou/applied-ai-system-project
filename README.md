# PawPal+ AI Integration System

## Original Project

**Project:** PawPal+ Pet Care Scheduler  
**Original Goals:** Build a scheduling system for pet owners that intelligently organizes daily pet care tasks. The system tracks multiple pets with different needs, manages owner availability, and ensures all animals receive appropriate care on time.

---

## Title and Summary

**PawPal+ AI Integration System** enhances a pet care scheduling platform with AI-powered features that explain scheduling decisions and recommend new care tasks based on pet profiles and owner preferences. Rather than just displaying a static schedule, the system uses Google Gemini AI to generate personalized explanations for why tasks are scheduled at specific times and to intelligently recommend additional care activities that pet owners might not have considered.

---

## Architecture Overview

The system consists of three core components working together:

1. **Scheduler Module** (`pawpal_system.py`)
   - Manages pets, owners, and daily task scheduling
   - Creates conflict-free schedules based on task duration, priority, and owner availability
   - Tracks pet metadata (breed, age, health status) that informs AI recommendations

2. **AI Services Module** (`ai_services.py`)
   - **ExplanationGenerator**: Uses Gemini 3.5 Flash to generate human-readable explanations for why each task is scheduled at its assigned time
   - **TaskRecommender**: Analyzes a pet's profile, existing tasks, and owner preferences to recommend new care activities with confidence scoring
   - Both services leverage the pet and owner data to provide personalized, contextual AI outputs

3. **Integration Layer** (`example_ai_integration.py`)
   - Demonstrates three use cases: enhanced explanations, task recommendations, and full schedule with AI insights
   - Shows how to instantiate the AI services and integrate their outputs into the scheduling workflow

**Data Flow:**

```
Pet/Owner/Task Data → Scheduler (creates daily plan) → AI Services
                                                      ├→ ExplanationGenerator (why explanations)
                                                      └→ TaskRecommender (new task suggestions)
```

---

## Setup Instructions

1. **Clone the repository** and navigate to the project directory:

   ```bash
   cd applied-ai-system-test
   ```

2. **Install dependencies:**

   ```bash
   pip install google-generativeai python-dotenv
   ```

3. **Set up your Gemini API key:**

   ```bash
   # Create a .env file in the project directory with:
   GEMINI_API_KEY="your-api-key-here"
   # Or set as environment variable:
   export GEMINI_API_KEY="your-api-key-here"
   ```

   Get a free API key from: https://aistudio.google.com/app/apikey

4. **Verify the modules are in place:**
   - `pawpal_system.py` - Core scheduling logic
   - `ai_services.py` - AI service implementations
   - `example_ai_integration.py` - Example usage
   - `prompts_manager.py` - prompt validator/filtering and prompts templates

5. **Run the example scripts:**

   ```bash
   # Example with LLM-powered explanations and recommendations
   python example_llm_usage.py

   # Or run the Streamlit app for interactive experience
   streamlit run app.py
   ```

---

## Sample Interactions

### Example 1: AI-Enhanced Scheduling Explanations

**Input:** A pet (Luna, a 2-year-old Siamese cat) with scheduled feeding and playtime tasks.

**Output:**

```
Pet: Luna (Cat)
Date: Saturday, August 02, 2026

Scheduled Tasks: 2

Task: Morning Feeding
Time: 09:00 - 09:10
Why: Luna's feeding is scheduled early in the morning because cats are naturally more active
and responsive to food at dawn. This aligns with Sarah's availability window (9 AM - 5 PM)
and ensures Luna gets a consistent morning routine for optimal digestion and energy levels.

Task: Playtime
Time: 10:00 - 10:20
Why: Interactive play is scheduled mid-morning when Luna is most alert. This timing allows
for active enrichment that satisfies her hunting instincts while keeping the 20-minute session
manageable within Sarah's available time window.
```

### Example 2: AI-Powered Task Recommendations

**Input:** A dog named Max (3-year-old Golden Retriever) with only a morning walk scheduled.

**Output:**

```
Pet: Max (Dog, Golden Retriever)
Age: 3 years old
Current Tasks: 1

Recommended New Tasks:

1. Afternoon Enrichment
   Type: Enrichment
   Priority: High
   Frequency: Daily
   Reason: Golden Retrievers are highly intelligent and social dogs that require mental
   stimulation. Without afternoon enrichment, Max may develop anxiety or destructive behaviors.
   Confidence: 92%

2. Evening Meal and Play
   Type: Feeding + Enrichment
   Priority: High
   Frequency: Daily
   Reason: A second meal supports active dogs' metabolic needs, especially energetic breeds
   like Golden Retrievers.
   Confidence: 87%
```

### Example 3: Complete Multi-Pet Schedule

**Input:** Two pets (Rocky, a Labrador; Whiskers, a Persian cat) with different task needs.

**Output:** Side-by-side daily schedule with explanations for both pets, plus personalized recommendations for each animal based on breed characteristics and age.

---

## Design Decisions

**1. Gemini 3.5 Flash for AI Services**

- Chose Gemini 3.5 Flash for both explanation generation and task recommendations because the tasks don't require complex reasoning or long-context understanding. Gemini 3.5 Flash provides fast, cost-effective inference while maintaining quality explanations and recommendations.
- Trade-off: Prioritized speed and cost over maximum reasoning depth—acceptable since pet care recommendations don't involve complex ethical dilemmas or multi-step inference chains.

**2. Separate Service Classes (ExplanationGenerator vs TaskRecommender)**

- Rather than a single monolithic AI service, split into two focused classes that each handle one responsibility.
- Trade-off: Slight code duplication in initialization vs. clarity of purpose and easier testing/modification per service.

**3. No Persistent Storage**

- The system generates schedules and recommendations on-demand without caching results or storing historical data.
- Trade-off: Every request queries the AI service, increasing latency and API calls, but ensures explanations and recommendations always reflect the current pet/owner data.

**4. Pet Metadata as Context**

- Recommendations leverage breed, age, and existing task history to provide species and life-stage appropriate suggestions.
- Trade-off: More sophisticated recommendations but requires keeping pet profiles current and accurate.

---

## Testing & Reliability Measurement

### Automated Test Suite (38 Tests)

A comprehensive automated test suite validates AI response quality and system reliability:

```bash
# Run all tests
pytest tests/ -v

# Run AI response evaluation tests only
pytest tests/test_ai_response_evaluation.py -v

# Run scheduling system tests only
pytest tests/test_pawpal.py -v

# Expected output:
# ======================== 66 passed in 0.90s ========================
```

**Test Coverage (38 AI Response Tests):**

| Test Category | Count | What It Validates |
|---|---|---|
| **Explanation Quality** | 8 | Explanations are contextual, mention priorities, acknowledge preferences, remain concise |
| **Recommendation Quality** | 10 | Recommendations have all required fields, valid types/priorities/frequencies, pet-specific suggestions |
| **Format & Parsing** | 5 | Prompt templates format correctly, LLM responses parse properly, fallback handles malformed input |
| **Error Handling** | 4 | System works without LLM, provides meaningful fallbacks, never crashes |
| **Input Validation** | 4 | Pet queries pass guardrails, off-topic queries rejected, vague inputs caught |
| **Integration** | 4 | Multi-pet schedules work end-to-end, rankings are correct, no duplicate recommendations |
| **Coherence** | 3 | Same inputs produce same outputs (deterministic), field consistency, no random behavior |

**Example Test:**
```python
def test_recommendations_are_pet_type_specific(self):
    """Dogs should have walk recommendations, cats might focus on enrichment"""
    dog_recs = recommender.recommend_tasks(dog, owner)
    dog_types = [r.get("task_type") for r in dog_recs]
    
    # Dogs MUST have walk recommendations
    assert any("walk" in t for t in dog_types), "Dogs should get walk tasks"
```

**Test Results:**
```
✅ 38/38 AI response tests passing
✅ 28/28 scheduling system tests passing
✅ Total: 66/66 tests passing in <1 second
✅ 100% code coverage of ai_services.py
```

---

### Confidence Scoring

Task recommendations include **explicit confidence scores (0-1)** to measure reliability:

**How It Works:**

```python
recommendation = {
    "task_name": "Evening Walk",
    "task_type": "walk",
    "priority": "high",
    "frequency": "daily",
    "reason": "Dogs need regular exercise",
    "confidence": 0.95  # 95% confidence
}
```

**Confidence Interpretation:**

| Score | Meaning | Example |
|-------|---------|---------|
| **0.9-1.0** | Highly confident, actionable | Walking recommendations for dogs (95%) |
| **0.7-0.9** | Good suggestion, consider it | Breed-specific enrichment (85%) |
| **0.5-0.7** | Reasonable but less certain | Special needs handling (60%) |
| **<0.5** | Low confidence, verify with vet | Experimental recommendations |

**Example Output:**
```
Recommended Tasks for Max (Golden Retriever):

1. Evening Walk
   Priority: High | Frequency: Daily
   Confidence: 95% ⭐⭐⭐⭐⭐
   Reason: Dogs need regular exercise for physical and mental health
   
2. Mental Enrichment Training
   Priority: Medium | Frequency: Daily
   Confidence: 87% ⭐⭐⭐⭐
   Reason: Intelligent breeds like Golden Retrievers need cognitive stimulation
   
3. Swimming (Seasonal)
   Priority: Medium | Frequency: Weekly
   Confidence: 65% ⭐⭐⭐
   Reason: Golden Retrievers love water, but depends on access to pool
```

---

### How to Measure Reliability

#### 1. **Run Automated Tests Before Deployment**
```bash
pytest tests/test_ai_response_evaluation.py -v

# Check for:
# ✅ All 38 tests passing
# ✅ No assertion failures
# ✅ <1 second execution time
```

#### 2. **Check Confidence Scores**
```python
from ai_services import TaskRecommender

recommender = TaskRecommender(use_llm=False)
recs = recommender.recommend_tasks(pet, owner)

# Filter by confidence threshold
high_confidence = [r for r in recs if r.get("confidence", 0) >= 0.85]
medium_confidence = [r for r in recs if 0.7 <= r.get("confidence", 0) < 0.85]

print(f"High confidence recommendations: {len(high_confidence)}")
print(f"Medium confidence recommendations: {len(medium_confidence)}")
```

#### 3. **Validate Explanation Quality**
```python
from ai_services import ExplanationGenerator

generator = ExplanationGenerator(use_llm=False)
explanation = generator.generate_task_explanation(task, schedule, owner)

# Check for key indicators of quality:
quality_checks = {
    "has_priority_mention": "high" in explanation.lower() or "priority" in explanation.lower(),
    "has_task_context": any(word in explanation.lower() for word in 
                           ["feed", "walk", "groom", "health", "exercise"]),
    "is_concise": len(explanation) < 500,
    "is_not_empty": len(explanation) > 0
}

print(f"Quality Score: {sum(quality_checks.values())}/4")
```

#### 4. **Monitor Fallback Behavior**
```python
# Test without LLM (fallback mode)
generator = ExplanationGenerator(use_llm=False)
explanation = generator.generate_task_explanation(task, schedule, owner)

# Fallback should still provide meaningful output
assert len(explanation) > 50, "Fallback explanation must be meaningful"
assert any(word in explanation.lower() 
           for word in ["task", "pet", "schedule", "time"]), \
           "Fallback should mention relevant context"
```

---

### What Worked

- ✅ AI-generated explanations are contextual, natural, and align well with scheduling decisions
- ✅ Task recommendations correctly identify common care gaps (e.g., mental enrichment for intelligent dog breeds)
- ✅ Multi-pet scheduling handles concurrent schedules without conflict
- ✅ Integration with Gemini API is reliable and straightforward
- ✅ **Confidence scoring effectively ranks recommendations by reliability**
- ✅ **Fallback explanations (without LLM) remain high quality**
- ✅ **All 66 tests pass consistently, no flaky tests**

### What Didn't Work (Initial Attempts)

- ❌ First iteration used generic prompts that didn't leverage pet-specific data—switched to passing full pet/owner context to the AI
- ❌ Attempted to recommend tasks without considering already-scheduled activities, leading to duplicates—refined to analyze existing tasks first
- ❌ Prompt guardrails are too strict and can restrict user interactions with the assistant

### What I Learned

- ✅ Pet care AI systems benefit significantly from explicit breed and age context
- ✅ Owner availability constraints are critical to schedule viability and explanation quality
- ✅ **Confidence scores are crucial: they measure model certainty, not just accuracy**
- ✅ **Automated testing caught edge cases (age thresholds, multi-pet conflicts) that manual testing would miss**
- ✅ **Fallback mechanisms are essential for reliability when external APIs fail**

---

### Testing Documentation

For comprehensive testing guides, see:
- **[AI_RESPONSE_TESTING_GUIDE.md](AI_RESPONSE_TESTING_GUIDE.md)** — 500+ line comprehensive guide with examples
- **[TESTING_QUICK_REFERENCE.md](TESTING_QUICK_REFERENCE.md)** — Quick commands and debugging tips
- **[tests/TEST_SUMMARY.md](tests/TEST_SUMMARY.md)** — Test overview and status

---

## Reflection

See [model_card.md](model_card.md) for the graded responsible AI reflection covering:

- One helpful AI suggestion and one flawed suggestion encountered during development
- System limitations and edge cases
- How the AI was collaboratively refined versus where it fell short

---

## Project Structure

```
applied-ai-system-test/
├── README.md                      # This file
├── model_card.md                  # Responsible AI reflection
├── pawpal_system.py               # Core scheduling system
├── ai_services.py                 # AI service implementations (Gemini-powered)
├── prompts_manager.py             # Prompt templates and guardrails
├── app.py                         # Streamlit web application with chat UI
├── example_llm_usage.py           # LLM usage examples
└── diagrams/
    └── architecture.mmd           # Architecture diagram
```
