"""
Quick example: Using LLM for AI-powered explanations and recommendations with Gemini.

Setup (3 steps):
1. Install: pip install -r requirements.txt
2. Get free API key: https://aistudio.google.com/app/apikey
3. Add to .env file: GEMINI_API_KEY=your-key-here

The code automatically loads the API key from .env file!

Available Gemini Models:
- Model.GEMINI_3_5_FLASH      (Latest, recommended)
- Model.GEMINI_1_5_FLASH      (Fast, cheaper)
- Model.GEMINI_1_5_PRO        (Best quality)

Run with: python example_llm_usage.py
"""

from datetime import datetime
from pathlib import Path
from pawpal_system import Owner, Pet, Task, TaskType, Scheduler
from ai_services import ExplanationGenerator, TaskRecommender, Model, _get_api_key

# Load .env file (optional - ai_services handles it too)
def load_env():
    try:
        from dotenv import load_dotenv  # type: ignore
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True)
    except ImportError:
        pass

load_env()


def main():
    print("\n" + "="*70)
    print("PawPal+ with AI-Powered Explanations & Recommendations")
    print("="*70)

    # Get API key (checks .env and environment variables)
    api_key = _get_api_key()

    if api_key:
        print(f"\n✓ API key found: {len(api_key)} characters")
        print(f"✓ Using Gemini API: {Model.GEMINI_3_5_FLASH.value}")
        print("✓ LLM Mode: ENABLED")
        use_llm = True
    else:
        print("\n⚠️  No API key found. Using rule-based mode.")
        print("   Add to .env: GEMINI_API_KEY=your-key-here")
        use_llm = False

    api_key_to_pass = api_key if use_llm else ""

    print(f"\nDEBUG: use_llm={use_llm}, api_key={'***' if api_key_to_pass else 'None'}")

    # Create owner
    owner = Owner(
        owner_id="o1",
        name="Sarah Johnson",
        email="sarah@example.com",
        phone="555-1234",
        address="123 Main St, Springfield"
    )
    owner.add_preference("prefer morning walks")
    owner.add_preference("only available 9 AM - 5 PM")

    # Create pets
    dog = Pet(
        pet_id="p1",
        name="Max",
        pet_type="Dog",
        breed="Golden Retriever",
        age=4,
        owner=owner
    )

    cat = Pet(
        pet_id="p2",
        name="Luna",
        pet_type="Cat",
        breed="Siamese",
        age=2,
        owner=owner
    )

    owner.add_pet(dog)
    owner.add_pet(cat)

    # Create tasks for Max
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    max_walk = Task(
        task_id="t1",
        name="Morning Walk",
        description="Walk in the park",
        task_type=TaskType.WALK,
        default_duration=30,
        default_frequency="daily",
        default_priority="high",
        pet=dog,
        due_date=today
    )

    max_meal = Task(
        task_id="t2",
        name="Breakfast",
        description="Feed Max",
        task_type=TaskType.FEEDING,
        default_duration=15,
        default_frequency="daily",
        default_priority="high",
        pet=dog,
        due_date=today
    )

    dog.add_task(max_walk)
    dog.add_task(max_meal)

    # Create tasks for Luna
    luna_meal = Task(
        task_id="t3",
        name="Breakfast",
        description="Feed Luna",
        task_type=TaskType.FEEDING,
        default_duration=10,
        default_frequency="daily",
        default_priority="high",
        pet=cat,
        due_date=today
    )

    luna_play = Task(
        task_id="t4",
        name="Playtime",
        description="Interactive play",
        task_type=TaskType.ENRICHMENT,
        default_duration=20,
        default_frequency="daily",
        default_priority="medium",
        pet=cat,
        due_date=today
    )

    cat.add_task(luna_meal)
    cat.add_task(luna_play)

    # Schedule tasks
    dog_scheduler = Scheduler(scheduler_id="s1", pet=dog)
    cat_scheduler = Scheduler(scheduler_id="s2", pet=cat)

    dog_schedule = dog_scheduler.generate_daily_plan(today)
    cat_schedule = cat_scheduler.generate_daily_plan(today)

    # --- PART 1: AI-ENHANCED EXPLANATIONS ---
    print("\n" + "-"*70)
    print("PART 1: AI-ENHANCED EXPLANATIONS")
    print("-"*70)

    explanation_gen = ExplanationGenerator(
        model=Model.GEMINI_3_5_FLASH,
        use_llm=use_llm,
        api_key=api_key_to_pass
    )

    # Other models: GEMINI_1_5_FLASH, GEMINI_1_5_PRO

    print("\nMAX'S SCHEDULE:")
    for task in dog_schedule['scheduled_tasks']:
        print(f"\n  Task: {task.name}")
        print(f"  Time: {task.start_time.strftime('%H:%M')} - {task.end_time.strftime('%H:%M')}")

        try:
            explanation = explanation_gen.generate_task_explanation(
                task, dog_schedule, owner
            )
            # Show if this is LLM or rule-based
            is_llm = "LLM" if use_llm else "Rule-based"
            print(f"  Why ({is_llm}): {explanation}")
        except Exception as e:
            print(f"  ⚠️ Error: {str(e)}")
            print(f"  Using fallback")

    print("\n\nLUNA'S SCHEDULE:")
    for task in cat_schedule['scheduled_tasks']:
        print(f"\n  Task: {task.name}")
        print(f"  Time: {task.start_time.strftime('%H:%M')} - {task.end_time.strftime('%H:%M')}")

        try:
            explanation = explanation_gen.generate_task_explanation(
                task, cat_schedule, owner
            )
            is_llm = "LLM" if use_llm else "Rule-based"
            print(f"  Why ({is_llm}): {explanation}")
        except Exception as e:
            print(f"  ⚠️ Error: {str(e)}")
            print(f"  Using fallback")

    # --- PART 2: AI TASK RECOMMENDATIONS ---
    print("\n" + "-"*70)
    print("PART 2: AI TASK RECOMMENDATIONS")
    print("-"*70)

    recommender = TaskRecommender(
        model=Model.GEMINI_3_5_FLASH,
        use_llm=use_llm,
        api_key=api_key_to_pass
    )
    print (f"\nDEBUG: use_llm={use_llm}, api_key={'***' if api_key_to_pass else 'None'}")

    # Other models: GEMINI_1_5_FLASH, GEMINI_1_5_PRO

    print("\nRECOMMENDED TASKS FOR MAX:")
    max_recs = recommender.recommend_tasks(dog, owner)
    ranked_max = recommender.rank_recommendations(max_recs, owner)

    for i, rec in enumerate(ranked_max[:3], 1):
        confidence = recommender.get_recommendation_confidence(rec)
        print(f"\n  {i}. {rec['task_name']}")
        print(f"     Type: {rec['task_type'].title()}")
        print(f"     Priority: {rec['priority'].title()}")
        print(f"     Frequency: {rec['frequency'].title()}")
        print(f"     Why: {rec['reason']}")
        print(f"     Confidence: {confidence*100:.0f}%")

    print("\n\nRECOMMENDED TASKS FOR LUNA:")
    luna_recs = recommender.recommend_tasks(cat, owner)
    ranked_luna = recommender.rank_recommendations(luna_recs, owner)

    for i, rec in enumerate(ranked_luna[:3], 1):
        confidence = recommender.get_recommendation_confidence(rec)
        print(f"\n  {i}. {rec['task_name']}")
        print(f"     Type: {rec['task_type'].title()}")
        print(f"     Priority: {rec['priority'].title()}")
        print(f"     Frequency: {rec['frequency'].title()}")
        print(f"     Why: {rec['reason']}")
        print(f"     Confidence: {confidence*100:.0f}%")


    print("\n" + "="*70)
    if use_llm:
        print("✓ Example complete! Explanations and recommendations were AI-generated.")
        print("  Using Google Gemini API from .env file.")
    else:
        print("✓ Example complete! Using rule-based explanations and recommendations.")
        print("  To enable Gemini API:")
        print("  1. Get free key: https://aistudio.google.com/app/apikey")
        print("  2. Add to .env file: GEMINI_API_KEY=your-key")
        print("  3. Restart the app")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
