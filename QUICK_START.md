# Quick Start: AI-Powered Explanations & Recommendations

## 3-Minute Setup

### 1. Install
```bash
pip install google-generativeai
```

### 2. Set API Key
```bash
export GEMINI_API_KEY='your-gemini-api-key-here'
```

### 3. Enable LLM (in your code)
```python
from ai_services import ExplanationGenerator, TaskRecommender

# Just add use_llm=True!
explanation_gen = ExplanationGenerator(use_llm=True)
recommender = TaskRecommender(use_llm=True)
```

## Rule-Based vs LLM Mode

### Rule-Based (Default)
```python
# No API key needed, works offline
explanation_gen = ExplanationGenerator(use_llm=False)

# Returns structured explanations based on task logic
# Output: "High priority task scheduled first | Essential feeding time for pet health"
```

### LLM Mode (Better Quality)
```python
# Requires API key and internet
explanation_gen = ExplanationGenerator(use_llm=True)

# Returns natural language explanations
# Output: "Max's morning walk is scheduled at 6 AM to start the day with exercise 
#          before the rest of the family wakes up. This aligns with your preference
#          for morning activities and gives Max time to burn energy."
```

## Usage Examples

### Get Better Explanations
```python
from ai_services import ExplanationGenerator
from datetime import datetime

explanation_gen = ExplanationGenerator(use_llm=True)
explanation = explanation_gen.generate_task_explanation(task, schedule, owner)
print(explanation)
```

### Get Smart Recommendations
```python
from ai_services import TaskRecommender

recommender = TaskRecommender(use_llm=True)
recommendations = recommender.recommend_tasks(pet, owner)

# Returns rich task suggestions with reasons
for rec in recommendations:
    print(f"{rec['task_name']}: {rec['reason']}")
```

## Switching Models

For different speed/quality tradeoffs:

```python
from ai_services import ExplanationGenerator, Model

# Fast & cheap (recommended)
gen = ExplanationGenerator(model=Model.GEMINI_2_FLASH, use_llm=True)

# Balanced
gen = ExplanationGenerator(model=Model.GEMINI_1_5_FLASH, use_llm=True)

# Best quality but slower
gen = ExplanationGenerator(model=Model.GEMINI_1_5_PRO, use_llm=True)
```

## Fallback Behavior

If API fails for any reason, the system automatically falls back to rule-based responses:

```python
# These will work even if:
# - Internet is down
# - API key is invalid
# - API quota exceeded

explanation = explanation_gen.generate_task_explanation(task, schedule, owner)
recommendations = recommender.recommend_tasks(pet, owner)
```

## Run Examples

### Rule-Based (No API Key Needed)
```bash
python example_llm_usage.py
```

### With LLM (API Key Required)
```bash
export GEMINI_API_KEY='your-gemini-api-key'
python example_llm_usage.py
```

## What Changed?

### ExplanationGenerator
| Aspect | Rule-Based | LLM |
|--------|-----------|-----|
| Quality | Good (rule-based) | Excellent (natural language) |
| Speed | Instant | ~500ms-1s |
| Setup | None | Install google-generativeai, set API key |
| Cost | Free | ~$0.00001-0.0001 per explanation |

### TaskRecommender
| Aspect | Rule-Based | LLM |
|--------|-----------|-----|
| Recommendations | Generic (based on pet type) | Personalized to owner |
| Count | 2-3 per pet | 2-3 per pet |
| Reasoning | Predefined | Context-aware |
| Cost | Free | ~$0.00001-0.0002 per recommendation set |

## Common Questions

**Q: Do I need to use LLM?**
A: No! Rule-based works great. LLM is optional if you want better quality explanations.

**Q: What if API key is wrong?**
A: You'll get a warning and fallback to rule-based responses. No errors.

**Q: How much does it cost?**
A: With Haiku model, about $0.0005 per task. Very cheap for better UX.

**Q: Can I switch models dynamically?**
A: Yes! Create multiple generators with different models:
```python
fast_gen = ExplanationGenerator(model=Model.CLAUDE_HAIKU, use_llm=True)
quality_gen = ExplanationGenerator(model=Model.CLAUDE_OPUS, use_llm=True)
```

**Q: What if internet goes down?**
A: Automatically falls back to rule-based explanations. Your app keeps working.

## Next Steps

1. ✅ `pip install anthropic`
2. ✅ Set `ANTHROPIC_API_KEY`
3. ✅ Change `use_llm=False` → `use_llm=True` in your code
4. ✅ Run and enjoy better explanations!

## Files to Check Out

- `ai_services.py` - Core implementation
- `example_llm_usage.py` - Working example
- `LLM_SETUP_GUIDE.md` - Detailed setup guide
- `architecture.mmd` - System architecture diagram
