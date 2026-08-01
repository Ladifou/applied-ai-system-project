"""
Quick example: Using LLM for AI-powered explanations and recommendations.

Before running this, you need:
1. pip install anthropic
2. Set ANTHROPIC_API_KEY environment variable or pass api_key to constructors

Run with: python example_llm_usage.py
"""

from datetime import datetime
from pawpal_system import Owner, Pet, Task, TaskType, Scheduler
from ai_services import ExplanationGenerator, TaskRecommender, Model
import os


def main():
    print("\n" + "="*70)
    print("PawPal+ with AI-Powered Explanations & Recommendations")
    print("="*70)

    # Check if API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  ANTHROPIC_API_KEY not set. Using rule-based explanations.")
        print("   To use LLM, set: export ANTHROPIC_API_KEY='your-key-here'")
        use_llm = False
    else:
        print("\n✓ API key found. Using Claude API for explanations.")
        use_llm = True

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
        model=Model.CLAUDE_HAIKU,
        use_llm=use_llm
    )

    print("\nMAX'S SCHEDULE:")
    for task in dog_schedule['scheduled_tasks']:
        print(f"\n  Task: {task.name}")
        print(f"  Time: {task.start_time.strftime('%H:%M')} - {task.end_time.strftime('%H:%M')}")

        explanation = explanation_gen.generate_task_explanation(
            task, dog_schedule, owner
        )
        print(f"  Why: {explanation}")

    print("\n\nLUNA'S SCHEDULE:")
    for task in cat_schedule['scheduled_tasks']:
        print(f"\n  Task: {task.name}")
        print(f"  Time: {task.start_time.strftime('%H:%M')} - {task.end_time.strftime('%H:%M')}")

        explanation = explanation_gen.generate_task_explanation(
            task, cat_schedule, owner
        )
        print(f"  Why: {explanation}")

    # --- PART 2: AI TASK RECOMMENDATIONS ---
    print("\n" + "-"*70)
    print("PART 2: AI TASK RECOMMENDATIONS")
    print("-"*70)

    recommender = TaskRecommender(
        model=Model.CLAUDE_HAIKU,
        use_llm=use_llm
    )

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
    else:
        print("✓ Example complete! Using rule-based explanations and recommendations.")
        print("  To use Claude API, set ANTHROPIC_API_KEY environment variable.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
