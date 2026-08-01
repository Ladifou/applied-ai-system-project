"""
Example: Integrating AI-powered explanations and recommendations into PawPal+
"""

from datetime import datetime
from pawpal_system import Owner, Pet, Task, TaskType, Scheduler
from ai_services import ExplanationGenerator, TaskRecommender, Model


def example_enhanced_explanations():
    """Demonstrate AI-enhanced scheduling explanations."""
    print("\n" + "="*70)
    print("EXAMPLE 1: AI-ENHANCED SCHEDULING EXPLANATIONS")
    print("="*70)

    # Create owner and pet
    owner = Owner(
        owner_id="owner_001",
        name="Sarah Johnson",
        email="sarah@example.com",
        phone="555-0123",
        address="123 Main St, Springfield"
    )
    owner.add_preference("prefer morning walks")
    owner.add_preference("only available 9-5")

    luna = Pet(
        pet_id="pet_002",
        name="Luna",
        pet_type="Cat",
        breed="Siamese",
        age=2,
        owner=owner
    )
    owner.add_pet(luna)

    # Create tasks
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    task1 = Task(
        task_id="task_001",
        name="Morning Feeding",
        description="Feed Luna her breakfast",
        task_type=TaskType.FEEDING,
        default_duration=10,
        default_frequency="daily",
        default_priority="high",
        pet=luna,
        due_date=today
    )

    task2 = Task(
        task_id="task_002",
        name="Playtime",
        description="Interactive play with toys",
        task_type=TaskType.ENRICHMENT,
        default_duration=20,
        default_frequency="daily",
        default_priority="medium",
        pet=luna,
        due_date=today
    )

    luna.add_task(task1)
    luna.add_task(task2)

    # Schedule tasks
    scheduler = Scheduler(scheduler_id="scheduler_001", pet=luna)
    daily_plan = scheduler.generate_daily_plan(today)

    # Generate AI-enhanced explanations
    explanation_gen = ExplanationGenerator(model=Model.CLAUDE_HAIKU)

    print(f"\nPet: {luna.name} ({luna.pet_type})")
    print(f"Date: {today.strftime('%A, %B %d, %Y')}")
    print(f"\nScheduled Tasks: {len(daily_plan['scheduled_tasks'])}\n")

    for task in daily_plan['scheduled_tasks']:
        print(f"Task: {task.name}")
        print(f"Time: {task.start_time.strftime('%H:%M')} - {task.end_time.strftime('%H:%M')}")

        # Get AI-enhanced explanation
        explanation = explanation_gen.generate_task_explanation(
            task, daily_plan, owner
        )
        print(f"Why: {explanation}")
        print()


def example_task_recommendations():
    """Demonstrate AI-powered task recommendations."""
    print("\n" + "="*70)
    print("EXAMPLE 2: AI-POWERED TASK RECOMMENDATIONS")
    print("="*70)

    # Create owner
    owner = Owner(
        owner_id="owner_001",
        name="John Smith",
        email="john@example.com",
        phone="555-9999",
        address="456 Oak Ave, Springfield"
    )
    owner.add_preference("prefers morning activities")
    owner.add_preference("available weekdays")

    # Create a dog
    max_dog = Pet(
        pet_id="pet_001",
        name="Max",
        pet_type="Dog",
        breed="Golden Retriever",
        age=3,
        owner=owner
    )
    owner.add_pet(max_dog)

    # Current tasks for Max
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    existing_task = Task(
        task_id="task_001",
        name="Morning Walk",
        description="Walk in the park",
        task_type=TaskType.WALK,
        default_duration=30,
        default_frequency="daily",
        default_priority="high",
        pet=max_dog,
        due_date=today
    )
    max_dog.add_task(existing_task)

    # Get AI recommendations
    recommender = TaskRecommender(model=Model.CLAUDE_HAIKU)
    recommendations = recommender.recommend_tasks(max_dog, owner)

    print(f"\nPet: {max_dog.name} ({max_dog.pet_type}, {max_dog.breed})")
    print(f"Age: {max_dog.age} years old")
    print(f"Current Tasks: {len(max_dog.tasks)}")
    print(f"\nRecommended New Tasks:\n")

    ranked = recommender.rank_recommendations(recommendations, owner)

    for i, rec in enumerate(ranked[:3], 1):
        confidence = recommender.get_recommendation_confidence(rec)
        print(f"{i}. {rec['task_name']}")
        print(f"   Type: {rec['task_type'].title()}")
        print(f"   Priority: {rec['priority'].title()}")
        print(f"   Frequency: {rec['frequency'].title()}")
        print(f"   Reason: {rec['reason']}")
        print(f"   Confidence: {confidence*100:.0f}%")
        print()


def example_full_schedule_with_ai():
    """Demonstrate complete schedule with AI explanations and recommendations."""
    print("\n" + "="*70)
    print("EXAMPLE 3: COMPLETE SCHEDULE WITH AI INSIGHTS")
    print("="*70)

    # Setup
    owner = Owner(
        owner_id="owner_001",
        name="Emma Davis",
        email="emma@example.com",
        phone="555-1234",
        address="789 Pine St, Springfield"
    )
    owner.add_preference("prefer morning walks")
    owner.add_preference("only available 9-5")

    # Two pets
    rocky = Pet(
        pet_id="pet_001",
        name="Rocky",
        pet_type="Dog",
        breed="Labrador",
        age=4,
        owner=owner
    )

    whiskers = Pet(
        pet_id="pet_002",
        name="Whiskers",
        pet_type="Cat",
        breed="Persian",
        age=5,
        owner=owner
    )

    owner.add_pet(rocky)
    owner.add_pet(whiskers)

    # Tasks for Rocky
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    rocky_walk = Task(
        task_id="task_001",
        name="Morning Walk",
        description="Walk in the park",
        task_type=TaskType.WALK,
        default_duration=30,
        default_frequency="daily",
        default_priority="high",
        pet=rocky,
        due_date=today
    )

    rocky_meal = Task(
        task_id="task_002",
        name="Breakfast",
        description="Feed Rocky",
        task_type=TaskType.FEEDING,
        default_duration=15,
        default_frequency="daily",
        default_priority="high",
        pet=rocky,
        due_date=today
    )

    rocky.add_task(rocky_walk)
    rocky.add_task(rocky_meal)

    # Tasks for Whiskers
    whiskers_meal = Task(
        task_id="task_003",
        name="Breakfast",
        description="Feed Whiskers",
        task_type=TaskType.FEEDING,
        default_duration=10,
        default_frequency="daily",
        default_priority="high",
        pet=whiskers,
        due_date=today
    )

    whiskers_play = Task(
        task_id="task_004",
        name="Playtime",
        description="Interactive play",
        task_type=TaskType.ENRICHMENT,
        default_duration=20,
        default_frequency="daily",
        default_priority="medium",
        pet=whiskers,
        due_date=today
    )

    whiskers.add_task(whiskers_meal)
    whiskers.add_task(whiskers_play)

    # Schedule both pets
    rocky_scheduler = Scheduler(scheduler_id="scheduler_001", pet=rocky)
    whiskers_scheduler = Scheduler(scheduler_id="scheduler_002", pet=whiskers)

    rocky_plan = rocky_scheduler.generate_daily_plan(today)
    whiskers_plan = whiskers_scheduler.generate_daily_plan(today)

    # Generate explanations for all tasks
    explanation_gen = ExplanationGenerator()

    print(f"\n{'ROCKY (Dog)':<40} {'WHISKERS (Cat)':<40}")
    print("-" * 80)

    for rocky_task, whiskers_task in zip(
        rocky_plan['scheduled_tasks'], whiskers_plan['scheduled_tasks']
    ):
        rocky_exp = explanation_gen.generate_task_explanation(
            rocky_task, rocky_plan, owner
        )
        whiskers_exp = explanation_gen.generate_task_explanation(
            whiskers_task, whiskers_plan, owner
        )

        print(f"\n{rocky_task.name:<40} {whiskers_task.name:<40}")
        print(
            f"{rocky_task.start_time.strftime('%H:%M'):<40} "
            f"{whiskers_task.start_time.strftime('%H:%M'):<40}"
        )

    # Show recommendations for each pet
    print(f"\n\n{'='*80}")
    print("RECOMMENDED NEW TASKS")
    print("="*80)

    recommender = TaskRecommender()

    for pet in [rocky, whiskers]:
        recommendations = recommender.recommend_tasks(pet, owner)
        ranked = recommender.rank_recommendations(recommendations, owner)

        print(f"\nFor {pet.name}:")
        for rec in ranked[:2]:
            print(f"  • {rec['task_name']} ({rec['priority'].upper()}) - {rec['reason']}")


if __name__ == "__main__":
    example_enhanced_explanations()
    example_task_recommendations()
    example_full_schedule_with_ai()

    print("\n" + "="*70)
    print("Examples complete!")
    print("="*70 + "\n")
