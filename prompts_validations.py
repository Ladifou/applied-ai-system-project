"""Guardrails for prompt validation to ensure queries are relevant to pet care scheduling."""

from ai_services import InferenceEngine, Model
from typing import Tuple


class PromptGuardrails:
    """Validates that user prompts are relevant to the PawPal+ app's functionalities."""

    # Keywords related to pet care and scheduling
    PET_KEYWORDS = {
        'dog', 'cat', 'pet', 'puppy', 'kitten', 'animal', 'breed',
        'walk', 'feeding', 'grooming', 'medication', 'enrichment',
        'schedule', 'task', 'reminder', 'time', 'daily', 'weekly',
        'training', 'exercise', 'health', 'care', 'play', 'sleep',
        'age', 'owner', 'preferences', 'availability', 'conflict',
        'priority', 'duration', 'frequency', 'behavior', 'wellness',
        'vet', 'nutrition', 'routine', 'daycare', 'appointments',
        'pawpal', 'scheduler', 'suggest', 'recommend', 'help',
        'advice', 'tip', 'question', 'work', 'morning', 'evening'
    }

    # Topics that are explicitly out of scope
    FORBIDDEN_PATTERNS = [
        'politics', 'religion', 'violence', 'hate', 'illegal',
        'stock market', 'bitcoin', 'crypto', 'betting', 'gambling',
        'adult content', 'explicit', 'drug', 'weapon', 'hack',
        'jailbreak', 'ignore instructions', 'forget your system'
    ]

    @classmethod
    def validate_keyword_based(cls, user_input: str) -> Tuple[bool, str]:
        """
        First layer: Fast keyword-based filtering.
        Returns (is_valid, reason_if_invalid)
        """
        user_lower = user_input.lower()

        # Check for forbidden patterns
        for pattern in cls.FORBIDDEN_PATTERNS:
            if pattern in user_lower:
                return False, f"❌ I can't help with that topic. I'm designed to help with pet care and scheduling."

        # Count relevant keywords
        keyword_count = sum(1 for keyword in cls.PET_KEYWORDS if keyword in user_lower)
        total_words = len(user_input.split())

        # Rules for relevance
        if total_words <= 3:
            # Very short queries - allow only if they contain keywords
            if keyword_count == 0:
                return False, "❓ Could you ask a question related to pet care or scheduling?"
        elif total_words > 5:
            # Longer queries - require at least some pet-related content
            keyword_percentage = keyword_count / total_words
            if keyword_percentage < 0.15:  # Less than 15% relevant keywords
                return False, "❓ Your question doesn't seem related to pet care. Ask me about: pet tasks, schedules, recommendations, care tips, or your pets!"

        return True, ""

    @classmethod
    def validate_with_ai(cls, user_input: str, api_key: str) -> Tuple[bool, str]:
        """
        Second layer: Use Gemini to assess relevance intelligently.
        This catches nuanced cases the keyword filter might miss.
        Returns (is_valid, reason_if_invalid)
        """
        try:
            relevance_assessment = f"""Assess if this question is about pet care, pet behavior, pet scheduling, or pet management.

Question: "{user_input}"

Respond with:
1. "RELEVANT" if it's about pets or pet care
2. "IRRELEVANT" if it's off-topic
3. Brief reason (max 8 words)

Pet care includes: health, nutrition, training, exercise, grooming, behavior, schedules, recommendations, care tips."""

            inference_engine = InferenceEngine(
                model_name=Model.GEMINI_3_5_FLASH.value,
                api_key=api_key,
                max_tokens=50
            )
            response = inference_engine.infer(relevance_assessment)

            is_relevant = "RELEVANT" in response.upper()
            return is_relevant, response

        except Exception as e:
            # If AI check fails, default to allowing (fail-safe)
            return True, f"(AI validation skipped: {str(e)})"

    @classmethod
    def validate_prompt(cls, user_input: str, api_key: str = None, use_ai_layer: bool = True) -> Tuple[bool, str]:
        """
        Complete validation pipeline.

        Args:
            user_input: The user's prompt
            api_key: Gemini API key (required for AI layer)
            use_ai_layer: Whether to use AI-based validation (slower but more accurate)

        Returns:
            (is_valid, reason_if_invalid)
        """
        # Layer 1: Fast keyword-based validation
        is_valid, reason = cls.validate_keyword_based(user_input)

        if not is_valid:
            return False, reason

        # Layer 2: AI-based validation (optional, more thorough)
        if use_ai_layer and api_key:
            is_relevant, ai_reason = cls.validate_with_ai(user_input, api_key)
            if not is_relevant:
                return False, "❓ Your question doesn't seem related to pet care. Ask me about your pets, their schedules, care tips, or recommendations!"

        return True, ""

    @classmethod
    def get_rejection_response(cls) -> str:
        """Get a helpful message for out-of-scope queries."""
        return """I'm specifically designed to help with pet care and scheduling. I can help you with:

✅ **Pet Management**: Adding pets, viewing their profiles
✅ **Task Scheduling**: Creating daily tasks, setting frequency and priorities
✅ **Recommendations**: Suggesting tasks based on pet type, age, and breed
✅ **Schedule Optimization**: Detecting conflicts, organizing multi-pet schedules
✅ **Pet Care Advice**: Tips for dogs, cats, senior pets, training, exercise
✅ **Routine Planning**: Feeding schedules, grooming, medication reminders

Ask me something like:
- "What tasks should I add for my dog?"
- "How often should I walk my cat?"
- "What care does a senior dog need?"
- "Can you help me schedule everything?"
"""

    @classmethod
    def get_suggestions_for_scope(cls) -> str:
        """Get in-scope topic suggestions."""
        return """💡 **Try asking about:**
- Pet types and their care requirements
- Task recommendations for your pets
- Schedule optimization and conflict resolution
- Pet behavior and training tips
- Health and wellness routines
"""
