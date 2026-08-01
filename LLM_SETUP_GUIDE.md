# LLM Integration Setup Guide

This guide shows how to integrate Claude API for AI-powered explanations and recommendations in PawPal+.

## Step 1: Install the Anthropic SDK

```bash
pip install anthropic
```

## Step 2: Get Your API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to **API Keys** section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

## Step 3: Set the API Key

Choose one of these methods:

### Option A: Environment Variable (Recommended)

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

### Option B: Pass directly to constructor

```python
from ai_services import ExplanationGenerator, Model

gen = ExplanationGenerator(
    model=Model.CLAUDE_HAIKU,
    use_llm=True,
    api_key='sk-ant-your-key-here'
)
```

## Step 4: Enable LLM in Your Code

### For Explanations

```python
from ai_services import ExplanationGenerator, Model
from pawpal_system import Owner, Pet, Task, TaskType, Scheduler
from datetime import datetime

# Create your owner, pet, and tasks
owner = Owner(...)
pet = Pet(...)
task = Task(...)

# Schedule the task
scheduler = Scheduler(scheduler_id="s1", pet=pet)
schedule = scheduler.generate_daily_plan(datetime.now())

# Generate explanation with LLM
explanation_gen = ExplanationGenerator(
    model=Model.CLAUDE_HAIKU,
    use_llm=True  # Enable LLM calls
)

explanation = explanation_gen.generate_task_explanation(
    task, schedule, owner
)
print(explanation)
```

### For Recommendations

```python
from ai_services import TaskRecommender, Model

recommender = TaskRecommender(
    model=Model.CLAUDE_HAIKU,
    use_llm=True  # Enable LLM calls
)

recommendations = recommender.recommend_tasks(pet, owner)
ranked = recommender.rank_recommendations(recommendations, owner)

for rec in ranked[:3]:
    print(f"- {rec['task_name']}: {rec['reason']}")
```

## Available Models

The SDK supports three Claude models:

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| `CLAUDE_HAIKU` | Fast responses, lower cost | Very Fast | Lowest |
| `CLAUDE_SONNET` | Balanced speed & quality | Fast | Medium |
| `CLAUDE_OPUS` | Best quality responses | Slower | Higher |

### Example: Using Different Models

```python
# Fast and cheap
gen = ExplanationGenerator(
    model=Model.CLAUDE_HAIKU,
    use_llm=True
)

# Higher quality
gen = ExplanationGenerator(
    model=Model.CLAUDE_SONNET,
    use_llm=True
)

# Best quality (but slower/more expensive)
gen = ExplanationGenerator(
    model=Model.CLAUDE_OPUS,
    use_llm=True
)
```

## Fallback Behavior

If the LLM API call fails:

1. **ExplanationGenerator** falls back to rule-based explanations
2. **TaskRecommender** falls back to type-based recommendations

So your app will still work even if:
- API key is invalid
- Network is down
- API quota is exceeded

This is handled automatically with a warning message.

## Example: Complete Integration

```python
from datetime import datetime
from pawpal_system import Owner, Pet, Task, TaskType, Scheduler
from ai_services import ExplanationGenerator, TaskRecommender, Model

# Setup
owner = Owner(
    owner_id="o1",
    name="Emma",
    email="emma@example.com",
    phone="555-1234",
    address="123 Main St"
)
owner.add_preference("prefer morning walks")

pet = Pet(
    pet_id="p1",
    name="Buddy",
    pet_type="Dog",
    breed="Golden Retriever",
    age=5,
    owner=owner
)
owner.add_pet(pet)

task = Task(
    task_id="t1",
    name="Morning Walk",
    description="Walk in the park",
    task_type=TaskType.WALK,
    default_duration=30,
    default_frequency="daily",
    default_priority="high",
    pet=pet,
    due_date=datetime.now()
)
pet.add_task(task)

# Schedule
scheduler = Scheduler(scheduler_id="s1", pet=pet)
schedule = scheduler.generate_daily_plan(datetime.now())

# Get AI-enhanced explanation
explanation_gen = ExplanationGenerator(use_llm=True)
explanation = explanation_gen.generate_task_explanation(task, schedule, owner)
print(f"Explanation: {explanation}")

# Get recommendations
recommender = TaskRecommender(use_llm=True)
recommendations = recommender.recommend_tasks(pet, owner)
ranked = recommender.rank_recommendations(recommendations, owner)

print("\nRecommended new tasks:")
for rec in ranked[:3]:
    print(f"- {rec['task_name']}: {rec['reason']}")
```

## Troubleshooting

### Error: "anthropic package is required"
```
pip install anthropic
```

### Error: "ANTHROPIC_API_KEY environment variable not set"
Set your API key (see Step 3 above)

### Error: "API call failed"
- Check your internet connection
- Verify your API key is correct
- Check if your API quota is exceeded
- The app will automatically fall back to rule-based responses

### Explanations are still rule-based
- Make sure `use_llm=True` is set
- Check that ANTHROPIC_API_KEY is set
- Verify the API key is correct
- Check console for error messages

## Pricing

Claude API charges per token used:

- **Haiku**: ~$0.80 per 1M input tokens, ~$4 per 1M output tokens
- **Sonnet**: ~$3 per 1M input tokens, ~$15 per 1M output tokens  
- **Opus**: ~$15 per 1M input tokens, ~$75 per 1M output tokens

A typical explanation = ~100-200 tokens
A typical recommendation = ~200-300 tokens

Cost per task explanation with Haiku: ~$0.0001-0.0002

## Next Steps

1. ✅ Install anthropic package
2. ✅ Get API key
3. ✅ Set environment variable
4. ✅ Update your code to use `use_llm=True`
5. Run your app and enjoy AI-powered explanations!

## More Resources

- [Anthropic Console](https://console.anthropic.com/)
- [Claude API Documentation](https://docs.anthropic.com/)
- [Pricing Calculator](https://www.anthropic.com/pricing)
