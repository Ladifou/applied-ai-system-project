# LLM Integration Setup Guide - Google Gemini API

This guide shows how to integrate Google Gemini API for AI-powered explanations and recommendations in PawPal+.

## Step 1: Install the Google Generative AI SDK

```bash
pip install google-generativeai
```

## Step 2: Get Your Gemini API Key

### Option A: Google AI Studio (Easiest for Development)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API key in new project"
3. Copy your API key (it's a long alphanumeric string)
4. **Note**: This free tier has rate limits - good for development/testing

### Option B: Google Cloud Console (For Production)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the "Generative Language API"
4. Create an API key in the Credentials section
5. Copy your API key

## Step 3: Set the API Key

Choose one of these methods:

### Option A: Environment Variable (Recommended)

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY='your-api-key-here'
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Mac/Linux:**
```bash
export GEMINI_API_KEY='your-api-key-here'
```

**Permanent (add to ~/.bashrc or ~/.zshrc):**
```bash
echo "export GEMINI_API_KEY='your-api-key-here'" >> ~/.bashrc
source ~/.bashrc
```

### Option B: Pass directly to constructor

```python
from ai_services import ExplanationGenerator

gen = ExplanationGenerator(
    model=Model.GEMINI_2_FLASH,
    use_llm=True,
    api_key='your-api-key-here'
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
    model=Model.GEMINI_2_FLASH,
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
    model=Model.GEMINI_2_FLASH,
    use_llm=True  # Enable LLM calls
)

recommendations = recommender.recommend_tasks(pet, owner)
ranked = recommender.rank_recommendations(recommendations, owner)

for rec in ranked[:3]:
    print(f"- {rec['task_name']}: {rec['reason']}")
```

## Available Models

Gemini offers several models with different speed/quality tradeoffs:

| Model | Best For | Speed | Cost | Availability |
|-------|----------|-------|------|--------------|
| `GEMINI_2_FLASH` | Fast responses, very low cost | Very Fast | Lowest | Latest |
| `GEMINI_1_5_FLASH` | Balanced speed & quality | Fast | Low | Stable |
| `GEMINI_1_5_PRO` | Best quality responses | Slower | Medium | Stable |

### Example: Using Different Models

```python
# Fastest & cheapest (recommended for development)
gen = ExplanationGenerator(
    model=Model.GEMINI_2_FLASH,
    use_llm=True
)

# Balanced speed and quality
gen = ExplanationGenerator(
    model=Model.GEMINI_1_5_FLASH,
    use_llm=True
)

# Best quality (but slower)
gen = ExplanationGenerator(
    model=Model.GEMINI_1_5_PRO,
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
- Rate limits are hit

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

### Error: "google-generativeai package is required"
```
pip install google-generativeai
```

### Error: "GEMINI_API_KEY environment variable not set"
Set your API key (see Step 3 above)

### Error: "API call failed: 403 Forbidden"
- Check your API key is correct
- Verify the API is enabled in Google Cloud Console
- For free tier, check if you've hit rate limits

### Error: "API call failed: 429 Too Many Requests"
You've hit rate limits. The app will automatically fall back to rule-based responses.
Free tier limits: 60 requests per minute

### Error: "API call failed: 400 Bad Request"
- Make sure you're using a valid Gemini model name
- Check that your API key is active
- Verify you're not sending too many tokens

### Explanations are still rule-based
- Make sure `use_llm=True` is set
- Check that GEMINI_API_KEY is set correctly
- Verify the API key is valid (try in [Google AI Studio](https://aistudio.google.com/app/apikey))
- Check console for error messages

## Pricing

Gemini API is **free for development** with generous rate limits:

### Free Tier (Google AI Studio)
- **60 requests per minute** (shared across all models)
- Gemini 1.5 Flash: Free
- Gemini 2.0 Flash: Free
- Great for testing and development

### Paid Tier (Google Cloud)
- **$0.075 per 1M input tokens** (Gemini 1.5 Flash)
- **$0.30 per 1M output tokens** (Gemini 1.5 Flash)
- **$1.50 per 1M input tokens** (Gemini 1.5 Pro)
- **$6.00 per 1M output tokens** (Gemini 1.5 Pro)
- Gemini 2.0 Flash: Pricing TBD

### Cost Examples
- A typical explanation = ~100-200 tokens
- A typical recommendation = ~200-300 tokens
- Cost per explanation with Flash: ~$0.00001-0.00003
- Cost per recommendation with Flash: ~$0.00002-0.00005

**Note**: Gemini is significantly cheaper than Claude!

## Comparison: Gemini vs Claude

| Aspect | Gemini 2.0 Flash | Claude 3.5 Haiku |
|--------|-----------------|-----------------|
| Input Cost | $0 (free tier) | ~$0.80/1M tokens |
| Output Cost | $0 (free tier) | ~$4/1M tokens |
| Speed | Very Fast | Fast |
| Quality | Excellent | Excellent |
| Free Tier | Yes (60 req/min) | No |
| Best For | Development | Production |

## Next Steps

1. ✅ Install google-generativeai package
2. ✅ Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
3. ✅ Set GEMINI_API_KEY environment variable
4. ✅ Update your code to use `use_llm=True`
5. Run your app and enjoy AI-powered explanations!

## More Resources

- [Google AI Studio](https://aistudio.google.com/app/apikey) - Get API keys
- [Google Cloud Console](https://console.cloud.google.com/) - Production setup
- [Gemini API Documentation](https://ai.google.dev/)
- [Gemini Models](https://ai.google.dev/models)
- [Free Tier Info](https://ai.google.dev/pricing)
