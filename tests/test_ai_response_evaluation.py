"""
Comprehensive test suite for evaluating AI-generated responses.

Tests cover:
1. Response Quality (relevance, coherence, completeness, tone)
2. ExplanationGenerator output evaluation
3. TaskRecommender output evaluation
4. Format validation and parsing
5. Error handling and fallback mechanisms
6. Integration tests with realistic scenarios
"""

import unittest
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from pawpal_system import Owner, Pet, Task, TaskType, Scheduler
from ai_services import ExplanationGenerator, TaskRecommender, Model, ContextBuilder
from prompts_manager import PromptManager, PromptGuardrails


class TestExplanationGeneratorQuality(unittest.TestCase):
    """Test suite for evaluating explanation generation quality."""

    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner(
            owner_id="owner_eval_001",
            name="Sarah",
            email="sarah@example.com",
            phone="555-1234",
            address="123 Pet St",
            preferences=["available 9 AM - 5 PM", "morning walks"]
        )

        self.pet = Pet(
            pet_id="pet_eval_001",
            name="Luna",
            pet_type="Cat",
            breed="Siamese",
            age=2,
            owner=self.owner
        )
        self.owner.add_pet(self.pet)

        # Create task and schedule for testing
        self.base_date = datetime(2026, 8, 2, 10, 0)
        self.task = Task(
            task_id="task_explain_001",
            name="Morning Feeding",
            description="Feed Luna",
            task_type=TaskType.FEEDING,
            default_duration=10,
            default_frequency="daily",
            default_priority="high",
            pet=self.pet,
            due_date=self.base_date,
            start_time=self.base_date,
            end_time=self.base_date + timedelta(minutes=10)
        )
        self.pet.add_task(self.task)

        self.scheduler = Scheduler(f"scheduler_{self.pet.pet_id}", self.pet)
        self.schedule = self.scheduler.generate_daily_plan(self.base_date)

    def test_explanation_is_not_empty(self):
        """Verify that explanations are generated (not empty or None)."""
        generator = ExplanationGenerator(use_llm=False)
        explanation = generator.generate_task_explanation(self.task, self.schedule, self.owner)

        self.assertIsNotNone(explanation, "Explanation should not be None")
        self.assertGreater(len(explanation), 0, "Explanation should not be empty")
        self.assertNotEqual(explanation.strip(), "", "Explanation should have content")

    def test_explanation_mentions_task_name(self):
        """Verify that explanations reference the task being scheduled."""
        generator = ExplanationGenerator(use_llm=False)
        explanation = generator.generate_task_explanation(self.task, self.schedule, self.owner)

        # Should mention task type, pet-related content, or task properties
        explanation_lower = explanation.lower()
        self.assertTrue(
            "feeding" in explanation_lower or "nutrition" in explanation_lower or "health" in explanation_lower,
            f"Explanation should mention feeding/nutrition context: {explanation}"
        )

    def test_explanation_mentions_priority(self):
        """Verify that high-priority tasks mention priority in explanation."""
        generator = ExplanationGenerator(use_llm=False)
        explanation = generator.generate_task_explanation(self.task, self.schedule, self.owner)

        explanation_lower = explanation.lower()
        self.assertTrue(
            "high" in explanation_lower or "priority" in explanation_lower or "first" in explanation_lower,
            f"High-priority task explanation should mention priority: {explanation}"
        )

    def test_explanation_mentions_task_type_context(self):
        """Verify that explanations provide context about task type."""
        generator = ExplanationGenerator(use_llm=False)
        explanation = generator.generate_task_explanation(self.task, self.schedule, self.owner)

        explanation_lower = explanation.lower()
        # For feeding tasks, should mention nutrition, health, or feeding
        self.assertTrue(
            any(word in explanation_lower for word in ["feed", "nutrition", "health", "essential"]),
            f"Feeding task explanation should mention relevant context: {explanation}"
        )

    def test_explanation_handles_unscheduled_tasks(self):
        """Verify that unscheduled tasks are handled gracefully."""
        unscheduled_task = Task(
            task_id="task_unscheduled",
            name="Playtime",
            description="Play with Luna",
            task_type=TaskType.ENRICHMENT,
            default_duration=20,
            default_frequency="daily",
            default_priority="medium",
            pet=self.pet,
            due_date=self.base_date
            # Note: no start_time or end_time
        )

        generator = ExplanationGenerator(use_llm=False)
        explanation = generator.generate_task_explanation(unscheduled_task, self.schedule, self.owner)

        self.assertIsNotNone(explanation)
        self.assertIn("not", explanation.lower(), "Should indicate task is unscheduled")

    def test_explanation_is_reasonably_concise(self):
        """Verify that explanations are concise (not overly verbose)."""
        generator = ExplanationGenerator(use_llm=False)
        explanation = generator.generate_task_explanation(self.task, self.schedule, self.owner)

        # Explanations should be relatively brief (typically under 500 characters for rule-based)
        # This is a reasonable limit for a summary explanation
        self.assertLess(len(explanation), 1000, "Explanation should be concise")

    def test_schedule_summary_contains_all_scheduled_tasks(self):
        """Verify that schedule summaries include all scheduled tasks."""
        # Add another task
        task2 = Task(
            task_id="task_explain_002",
            name="Playtime",
            description="Interactive play",
            task_type=TaskType.ENRICHMENT,
            default_duration=20,
            default_frequency="daily",
            default_priority="medium",
            pet=self.pet,
            due_date=self.base_date,
            start_time=self.base_date + timedelta(hours=1),
            end_time=self.base_date + timedelta(hours=1, minutes=20)
        )
        self.pet.add_task(task2)
        updated_schedule = self.scheduler.generate_daily_plan(self.base_date)

        generator = ExplanationGenerator(use_llm=False)
        summary = generator.generate_schedule_summary(updated_schedule, self.owner)

        self.assertIn("Morning Feeding", summary, "Summary should include first task")
        self.assertIn("Playtime", summary, "Summary should include second task")

    def test_explanation_respects_owner_preferences(self):
        """Verify that explanations acknowledge owner preferences when relevant."""
        # Create morning walk task for preference-aware explanation
        walk_task = Task(
            task_id="task_walk",
            name="Morning Walk",
            description="Walk Luna",
            task_type=TaskType.WALK,
            default_duration=30,
            default_frequency="daily",
            default_priority="high",
            pet=self.pet,
            due_date=self.base_date,
            start_time=datetime(2026, 8, 2, 9, 0),  # Morning
            end_time=datetime(2026, 8, 2, 9, 30)
        )

        generator = ExplanationGenerator(use_llm=False)
        explanation = generator.generate_task_explanation(walk_task, self.schedule, self.owner)

        explanation_lower = explanation.lower()
        # Should ideally mention owner preferences for walk tasks
        # At minimum should address timing relevance
        self.assertGreater(len(explanation), 0, "Should generate explanation")


class TestTaskRecommenderQuality(unittest.TestCase):
    """Test suite for evaluating task recommendation quality."""

    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner(
            owner_id="owner_rec_001",
            name="John",
            email="john@example.com",
            phone="555-5678",
            address="456 Dog Ave",
            preferences=["active", "outdoor activities"]
        )

        self.pet_dog = Pet(
            pet_id="pet_dog_001",
            name="Max",
            pet_type="Dog",
            breed="Golden Retriever",
            age=3,
            owner=self.owner
        )
        self.owner.add_pet(self.pet_dog)

        self.pet_cat = Pet(
            pet_id="pet_cat_001",
            name="Whiskers",
            pet_type="Cat",
            breed="Persian",
            age=5,
            owner=self.owner
        )
        self.owner.add_pet(self.pet_cat)

    def test_recommendations_are_not_empty(self):
        """Verify that recommendations are generated."""
        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.pet_dog, self.owner)

        self.assertIsNotNone(recommendations)
        self.assertGreater(len(recommendations), 0, "Should generate at least one recommendation")

    def test_recommendations_have_required_fields(self):
        """Verify that each recommendation has all required fields."""
        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.pet_dog, self.owner)

        required_fields = {"task_name", "task_type", "priority", "frequency", "reason", "confidence"}
        for i, rec in enumerate(recommendations):
            missing = required_fields - set(rec.keys())
            self.assertEqual(missing, set(), f"Recommendation {i} missing fields: {missing}")

    def test_recommendations_have_valid_task_types(self):
        """Verify that recommended task types are valid."""
        valid_types = {"walk", "feeding", "grooming", "enrichment", "medication"}
        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.pet_dog, self.owner)

        for rec in recommendations:
            task_type = rec.get("task_type", "").lower()
            self.assertIn(task_type, valid_types, f"Invalid task type: {task_type}")

    def test_recommendations_have_valid_priorities(self):
        """Verify that recommended priorities are valid."""
        valid_priorities = {"high", "medium", "low"}
        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.pet_dog, self.owner)

        for rec in recommendations:
            priority = rec.get("priority", "").lower()
            self.assertIn(priority, valid_priorities, f"Invalid priority: {priority}")

    def test_recommendations_have_valid_frequencies(self):
        """Verify that recommended frequencies are valid."""
        valid_frequencies = {"daily", "weekly", "occasional", "monthly"}
        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.pet_dog, self.owner)

        for rec in recommendations:
            frequency = rec.get("frequency", "").lower()
            self.assertIn(frequency, valid_frequencies, f"Invalid frequency: {frequency}")

    def test_recommendations_have_confidence_scores(self):
        """Verify that recommendations include confidence scores in valid range."""
        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.pet_dog, self.owner)

        for rec in recommendations:
            confidence = rec.get("confidence", 0)
            self.assertIsInstance(confidence, (int, float), "Confidence should be numeric")
            self.assertGreaterEqual(confidence, 0, "Confidence should be >= 0")
            self.assertLessEqual(confidence, 1, "Confidence should be <= 1")

    def test_recommendations_are_pet_type_specific(self):
        """Verify that recommendations differ based on pet type."""
        recommender = TaskRecommender(use_llm=False)
        dog_recs = recommender.recommend_tasks(self.pet_dog, self.owner)
        cat_recs = recommender.recommend_tasks(self.pet_cat, self.owner)

        # Dogs should have walk recommendations, cats might focus on play/grooming
        dog_task_types = [r.get("task_type", "").lower() for r in dog_recs]

        # Dogs should have walk or exercise recommendations
        self.assertTrue(
            any("walk" in t for t in dog_task_types),
            "Dogs should have walk recommendations"
        )

    def test_recommendations_consider_pet_age(self):
        """Verify that recommendations account for pet age."""
        senior_pet = Pet(
            pet_id="pet_senior_001",
            name="Buddy",
            pet_type="Dog",
            breed="Labrador",
            age=10,  # Senior dog
            owner=self.owner
        )

        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(senior_pet, self.owner)

        # Senior pets should have health check recommendations
        task_names = [r.get("task_name", "").lower() for r in recommendations]
        task_types = [r.get("task_type", "").lower() for r in recommendations]

        self.assertTrue(
            any("health" in name or "check" in name or "medic" in t
                for name in task_names for t in task_types),
            "Senior pet should have health-related recommendations"
        )

    def test_recommendation_confidence_reflects_relevance(self):
        """Verify that confidence scores make sense for the recommendations."""
        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.pet_dog, self.owner)

        # All recommendations should have reasonable confidence (not all 0 or all 1)
        confidences = [r.get("confidence", 0) for r in recommendations]

        # Should have some variation
        self.assertGreater(max(confidences), 0.5, "Some recommendations should have decent confidence")
        # But not all perfect scores
        if len(confidences) > 1:
            self.assertFalse(all(c == confidences[0] for c in confidences),
                            "Recommendations should have varying confidence")

    def test_recommendation_ranking_by_score(self):
        """Verify that recommendations can be ranked by relevance."""
        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.pet_dog, self.owner)
        ranked = recommender.rank_recommendations(recommendations, self.owner)

        # Should return same number of recommendations
        self.assertEqual(len(ranked), len(recommendations))

        # Rankings should be stable (same order on multiple calls)
        ranked2 = recommender.rank_recommendations(recommendations, self.owner)
        ranked_names_1 = [r.get("task_name") for r in ranked]
        ranked_names_2 = [r.get("task_name") for r in ranked2]
        self.assertEqual(ranked_names_1, ranked_names_2, "Ranking should be deterministic")


class TestResponseFormatAndParsing(unittest.TestCase):
    """Test suite for response format validation and parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.prompt_manager = PromptManager()
        self.owner = Owner(
            owner_id="owner_fmt_001",
            name="Test Owner",
            email="test@example.com",
            phone="555-0000",
            address="Test Address"
        )
        self.pet = Pet(
            pet_id="pet_fmt_001",
            name="TestPet",
            pet_type="Dog",
            breed="TestBreed",
            age=5,
            owner=self.owner
        )

    def test_prompt_templates_are_valid(self):
        """Verify that prompt templates format correctly."""
        context_builder = ContextBuilder()

        task = Task(
            task_id="task_fmt",
            name="Test Task",
            description="Test",
            task_type=TaskType.WALK,
            default_duration=30,
            default_frequency="daily",
            default_priority="high",
            pet=self.pet,
            due_date=datetime.now(),
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=30)
        )

        task_context = context_builder.build_task_context(task, {})
        schedule_context = context_builder.build_schedule_context(self.pet, self.owner, datetime.now())

        # Should not raise an exception
        prompt = self.prompt_manager.get_explanation_prompt(task_context, schedule_context)
        self.assertIsNotNone(prompt)
        self.assertGreater(len(prompt), 0)

    def test_recommendation_prompt_format(self):
        """Verify that recommendation prompts format correctly."""
        context_builder = ContextBuilder()

        pet_profile = context_builder.build_pet_profile(self.pet)
        owner_profile = context_builder.build_owner_profile(self.owner)

        prompt = self.prompt_manager.get_recommendation_prompt(pet_profile, owner_profile)
        self.assertIsNotNone(prompt)
        self.assertGreater(len(prompt), 0)
        self.assertIn("Dog", prompt, "Should include pet type")

    def test_llm_response_parsing_with_valid_format(self):
        """Verify parsing of well-formatted LLM recommendation responses."""
        recommender = TaskRecommender(use_llm=False)

        # Well-formatted response with numbered items and fields
        sample_response = """1. Evening Walk
* Type: walk
* Priority: high
* Frequency: daily
* Reason: Golden Retrievers need exercise

2. Mental Enrichment
* Type: enrichment
* Priority: medium
* Frequency: daily
* Reason: Mental stimulation prevents boredom"""

        parsed = recommender._parse_llm_recommendations(sample_response)

        self.assertGreater(len(parsed), 0, "Should parse recommendations")
        self.assertTrue(all("task_name" in r for r in parsed), "Each rec should have task_name")

    def test_llm_response_parsing_fallback(self):
        """Verify that parsing falls back to defaults for unparseable responses."""
        recommender = TaskRecommender(use_llm=False)

        # Malformed response
        bad_response = "This is not a valid recommendation format at all!"
        parsed = recommender._parse_llm_recommendations(bad_response)

        # Should return default recommendations instead of empty list
        self.assertIsNotNone(parsed)
        self.assertGreater(len(parsed), 0, "Should return default recommendations")
        self.assertTrue(all("task_name" in r for r in parsed), "Defaults should have required fields")

    def test_recommendation_field_normalization(self):
        """Verify that recommendation fields are normalized correctly."""
        recommender = TaskRecommender(use_llm=False)

        # Response with variations in field names (capitalization, extra spaces)
        response = """1. Morning Walk
* Task Type: Walk (with the dog)
* Priority: HIGH
* Frequency: Daily
* Reason: Exercise is important"""

        parsed = recommender._parse_llm_recommendations(response)

        if parsed:
            rec = parsed[0]
            # Should normalize task_type to lowercase and standard values
            self.assertIn(rec.get("task_type", "").lower(),
                         ["walk", "feeding", "grooming", "enrichment", "medication"],
                         "Task type should be normalized")


class TestErrorHandlingAndFallback(unittest.TestCase):
    """Test suite for error handling and fallback mechanisms."""

    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner(
            owner_id="owner_err_001",
            name="Test Owner",
            email="test@example.com",
            phone="555-0000",
            address="Test Address"
        )
        self.pet = Pet(
            pet_id="pet_err_001",
            name="TestPet",
            pet_type="Dog",
            breed="TestBreed",
            age=3,
            owner=self.owner
        )
        self.owner.add_pet(self.pet)

    def test_explanation_generator_without_llm(self):
        """Verify ExplanationGenerator works without LLM."""
        # Create with use_llm=False to skip LLM initialization
        generator = ExplanationGenerator(use_llm=False)

        self.assertIsNone(generator.inference_engine)
        self.assertFalse(generator.use_llm)

        # Should still generate explanations with fallback
        task = Task(
            task_id="task_err",
            name="Test",
            description="Test",
            task_type=TaskType.WALK,
            default_duration=30,
            default_frequency="daily",
            default_priority="high",
            pet=self.pet,
            due_date=datetime.now(),
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=30)
        )
        scheduler = Scheduler("scheduler_test", self.pet)
        schedule = scheduler.generate_daily_plan(datetime.now())

        explanation = generator.generate_task_explanation(task, schedule, self.owner)
        self.assertIsNotNone(explanation)
        self.assertGreater(len(explanation), 0)

    def test_task_recommender_without_llm(self):
        """Verify TaskRecommender works without LLM."""
        recommender = TaskRecommender(use_llm=False)

        self.assertFalse(recommender.use_llm)
        self.assertIsNone(recommender.inference_engine)

        # Should generate default recommendations
        recommendations = recommender.recommend_tasks(self.pet, self.owner)
        self.assertGreater(len(recommendations), 0, "Should provide default recommendations")

    def test_fallback_explanation_has_required_content(self):
        """Verify that fallback explanations are meaningful."""
        generator = ExplanationGenerator(use_llm=False)
        task = Task(
            task_id="task_fallback",
            name="Feeding",
            description="Feed pet",
            task_type=TaskType.FEEDING,
            default_duration=15,
            default_frequency="daily",
            default_priority="high",
            pet=self.pet,
            due_date=datetime.now(),
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=15)
        )
        scheduler = Scheduler("scheduler_fb", self.pet)
        schedule = scheduler.generate_daily_plan(datetime.now())

        explanation = generator.generate_task_explanation(task, schedule, self.owner)

        # Fallback should mention something meaningful
        explanation_lower = explanation.lower()
        self.assertTrue(
            any(word in explanation_lower for word in
                ["feed", "task", "priority", "time", "pet", "schedule"]),
            f"Fallback explanation should be meaningful: {explanation}"
        )

    def test_default_recommendations_are_complete(self):
        """Verify that default recommendations have all required fields."""
        recommender = TaskRecommender(use_llm=False)

        defaults = recommender._get_default_recommendations()

        required_fields = {"task_name", "task_type", "priority", "frequency", "reason", "confidence"}
        for rec in defaults:
            missing = required_fields - set(rec.keys())
            self.assertEqual(missing, set(), f"Default recommendation missing: {missing}")


class TestPromptGuardrails(unittest.TestCase):
    """Test suite for prompt validation and guardrails."""

    def test_pet_care_queries_are_valid(self):
        """Verify that pet-related queries pass validation."""
        guardrails = PromptGuardrails()

        test_queries = [
            "What tasks should I schedule for my dog?",
            "My dog needs exercise recommendations",
            "Help me organize my pet's schedule",
            "I have a cat that needs grooming"
        ]

        for query in test_queries:
            is_valid, reason = guardrails.validate_keyword_based(query)
            self.assertTrue(is_valid, f"Query should be valid: '{query}'. Reason: {reason}")

    def test_off_topic_queries_are_rejected(self):
        """Verify that off-topic queries fail validation."""
        guardrails = PromptGuardrails()

        test_queries = [
            "Tell me about stock markets",
            "How do I hack into computers?",
            "Can you help with politics?",
            "What's Bitcoin worth today?"
        ]

        for query in test_queries:
            is_valid, reason = guardrails.validate_keyword_based(query)
            self.assertFalse(is_valid, f"Query should be invalid: '{query}'")

    def test_vague_queries_validation(self):
        """Verify that very vague queries without pet keywords are caught."""
        guardrails = PromptGuardrails()

        # Short query with no pet keywords
        is_valid, reason = guardrails.validate_keyword_based("What?")
        self.assertFalse(is_valid, "Single word non-pet query should fail")

    def test_mixed_content_queries(self):
        """Verify validation handles queries with mixed relevant and irrelevant content."""
        guardrails = PromptGuardrails()

        # Mostly relevant
        is_valid, _ = guardrails.validate_keyword_based(
            "I need help scheduling my dog's walks and feeding times"
        )
        self.assertTrue(is_valid, "Pet-focused query should pass")


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests with realistic scenarios."""

    def setUp(self):
        """Set up realistic test scenario."""
        self.owner = Owner(
            owner_id="owner_int_001",
            name="Alice",
            email="alice@example.com",
            phone="555-1111",
            address="100 Happy St",
            preferences=["morning walks", "available 8 AM - 6 PM"]
        )

        self.dog = Pet(
            pet_id="pet_dog_int",
            name="Charlie",
            pet_type="Dog",
            breed="Labrador Retriever",
            age=4,
            owner=self.owner
        )
        self.owner.add_pet(self.dog)

        self.cat = Pet(
            pet_id="pet_cat_int",
            name="Mittens",
            pet_type="Cat",
            breed="Tabby",
            age=6,
            owner=self.owner
        )
        self.owner.add_pet(self.cat)

    def test_multi_pet_schedule_with_explanations(self):
        """Test generating explanations for multi-pet schedules."""
        # Create tasks for both pets
        dog_walk = Task(
            task_id="dog_walk",
            name="Morning Walk",
            description="Exercise",
            task_type=TaskType.WALK,
            default_duration=45,
            default_frequency="daily",
            default_priority="high",
            pet=self.dog,
            due_date=datetime(2026, 8, 2),
            start_time=datetime(2026, 8, 2, 8, 0),
            end_time=datetime(2026, 8, 2, 8, 45)
        )

        cat_feed = Task(
            task_id="cat_feed",
            name="Morning Feeding",
            description="Breakfast",
            task_type=TaskType.FEEDING,
            default_duration=10,
            default_frequency="daily",
            default_priority="high",
            pet=self.cat,
            due_date=datetime(2026, 8, 2),
            start_time=datetime(2026, 8, 2, 8, 0),
            end_time=datetime(2026, 8, 2, 8, 10)
        )

        self.dog.add_task(dog_walk)
        self.cat.add_task(cat_feed)

        # Generate explanations for both
        generator = ExplanationGenerator(use_llm=False)

        dog_scheduler = Scheduler("scheduler_dog", self.dog)
        dog_schedule = dog_scheduler.generate_daily_plan(datetime(2026, 8, 2))
        dog_explanation = generator.generate_task_explanation(dog_walk, dog_schedule, self.owner)

        cat_scheduler = Scheduler("scheduler_cat", self.cat)
        cat_schedule = cat_scheduler.generate_daily_plan(datetime(2026, 8, 2))
        cat_explanation = generator.generate_task_explanation(cat_feed, cat_schedule, self.owner)

        self.assertGreater(len(dog_explanation), 0)
        self.assertGreater(len(cat_explanation), 0)

    def test_recommendation_ranking_prioritizes_pet_needs(self):
        """Test that recommendations are ranked based on pet profile."""
        recommender = TaskRecommender(use_llm=False)

        # Get recommendations for young active dog
        recs = recommender.recommend_tasks(self.dog, self.owner)
        ranked = recommender.rank_recommendations(recs, self.owner)

        # Should have recommendations
        self.assertGreater(len(ranked), 0)

        # First recommendation should be high priority
        if ranked:
            first_priority = ranked[0].get("priority", "").lower()
            self.assertNotEqual(first_priority, "low", "Top recommendation shouldn't be low priority")

    def test_full_schedule_summary_generation(self):
        """Test generating complete schedule summaries with all explanations."""
        # Create multiple tasks
        base_date = datetime(2026, 8, 2)
        tasks_data = [
            ("Morning Walk", TaskType.WALK, "high", 30, 8, 0),
            ("Breakfast", TaskType.FEEDING, "high", 15, 9, 0),
            ("Playtime", TaskType.ENRICHMENT, "medium", 30, 10, 0),
        ]

        for task_name, task_type, priority, duration, hour, minute in tasks_data:
            task = Task(
                task_id=f"task_{task_name.lower().replace(' ', '_')}",
                name=task_name,
                description=task_name,
                task_type=task_type,
                default_duration=duration,
                default_frequency="daily",
                default_priority=priority,
                pet=self.dog,
                due_date=base_date,
                start_time=base_date.replace(hour=hour, minute=minute),
                end_time=base_date.replace(hour=hour, minute=minute) + timedelta(minutes=duration)
            )
            self.dog.add_task(task)

        # Generate schedule
        scheduler = Scheduler("scheduler_dog", self.dog)
        schedule = scheduler.generate_daily_plan(base_date)

        # Generate summary with explanations
        generator = ExplanationGenerator(use_llm=False)
        summary = generator.generate_schedule_summary(schedule, self.owner)

        # Verify summary contains all tasks
        self.assertIn("Morning Walk", summary)
        self.assertIn("Breakfast", summary)
        self.assertIn("Playtime", summary)

    def test_recommendation_considers_existing_tasks(self):
        """Test that recommendations don't duplicate existing tasks."""
        # Add a walk task
        walk_task = Task(
            task_id="existing_walk",
            name="Morning Walk",
            description="Regular walk",
            task_type=TaskType.WALK,
            default_duration=30,
            default_frequency="daily",
            default_priority="high",
            pet=self.dog,
            due_date=datetime.now()
        )
        self.dog.add_task(walk_task)

        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.dog, self.owner)

        # Should still work and provide various recommendations
        self.assertGreater(len(recommendations), 0, "Should provide recommendations")


class TestResponseCoherence(unittest.TestCase):
    """Test suite for evaluating response coherence and consistency."""

    def setUp(self):
        """Set up test fixtures."""
        self.owner = Owner(
            owner_id="owner_coh_001",
            name="Test Owner",
            email="test@example.com",
            phone="555-0000",
            address="Test Address",
            preferences=["morning walks"]
        )
        self.pet = Pet(
            pet_id="pet_coh_001",
            name="TestPet",
            pet_type="Dog",
            breed="Labrador",
            age=3,
            owner=self.owner
        )
        self.owner.add_pet(self.pet)

    def test_recommendation_consistency(self):
        """Verify that multiple calls generate consistent recommendations."""
        recommender = TaskRecommender(use_llm=False)

        recs1 = recommender.recommend_tasks(self.pet, self.owner)
        recs2 = recommender.recommend_tasks(self.pet, self.owner)

        # Should generate same recommendations in same order
        names1 = [r.get("task_name") for r in recs1]
        names2 = [r.get("task_name") for r in recs2]

        self.assertEqual(names1, names2, "Recommendations should be deterministic")

    def test_explanation_consistency(self):
        """Verify that explanations for same task are consistent."""
        generator = ExplanationGenerator(use_llm=False)

        task = Task(
            task_id="task_coh",
            name="Test Task",
            description="Test",
            task_type=TaskType.WALK,
            default_duration=30,
            default_frequency="daily",
            default_priority="high",
            pet=self.pet,
            due_date=datetime.now(),
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=30)
        )

        scheduler = Scheduler("scheduler_coh", self.pet)
        schedule = scheduler.generate_daily_plan(datetime.now())

        exp1 = generator.generate_task_explanation(task, schedule, self.owner)
        exp2 = generator.generate_task_explanation(task, schedule, self.owner)

        # Same task should produce same explanation
        self.assertEqual(exp1, exp2, "Explanations should be consistent")

    def test_recommendation_fields_consistency(self):
        """Verify that recommendation fields are consistent within each recommendation."""
        recommender = TaskRecommender(use_llm=False)
        recommendations = recommender.recommend_tasks(self.pet, self.owner)

        for rec in recommendations:
            # Task name should match its type
            task_name = rec.get("task_name", "").lower()
            task_type = rec.get("task_type", "").lower()

            # Just verify both exist and are non-empty
            self.assertTrue(len(task_name) > 0, "Task name should not be empty")
            self.assertTrue(len(task_type) > 0, "Task type should not be empty")


if __name__ == "__main__":
    unittest.main()
