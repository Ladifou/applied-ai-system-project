from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
from enum import Enum
import os
from pathlib import Path
from pawpal_system import Pet, Owner, Task, TaskType
from prompts_manager import PromptManager

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False




def load_env_config():
    """Load configuration from .env file if available."""
    if not DOTENV_AVAILABLE:
        return

    # Try primary path first
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
        return

    # Try alternative path (current working directory)
    alt_path = Path.cwd() / ".env"
    if alt_path.exists():
        load_dotenv(alt_path, override=True)
        return


def _get_api_key() -> str:
    """Get API key from .env file or environment variable."""
    import sys

    # Debug: Show what we're looking for
    script_dir = Path(__file__).parent
    env_file_1 = script_dir / ".env"
    env_file_2 = Path.cwd() / ".env"

    # Load the config
    load_env_config()

    # Try to get the key
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    # Debug output
    if not api_key:
        print(f"[DEBUG] Looking for .env files:", file=sys.stderr)
        print(f"  Path 1: {env_file_1} (exists: {env_file_1.exists()})", file=sys.stderr)
        print(f"  Path 2: {env_file_2} (exists: {env_file_2.exists()})", file=sys.stderr)
        print(f"  DOTENV_AVAILABLE: {DOTENV_AVAILABLE}", file=sys.stderr)
        if env_file_1.exists():
            print(f"  Reading {env_file_1}...", file=sys.stderr)
            with open(env_file_1) as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("GEMINI_API_KEY"):
                        print(f"    Found line: {line[:50]}", file=sys.stderr)

    return api_key


class Model(Enum):
    """Supported AI models for inference."""
    GEMINI_3_5_FLASH = "gemini-3.5-flash"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"


@dataclass
class InferenceEngine:
    """Handles actual LLM inference calls to Google Gemini API."""

    model_name: str = Model.GEMINI_3_5_FLASH.value
    max_tokens: int = 5000
    temperature: float = 0.7
    api_key: str = field(default_factory=lambda: _get_api_key())

    def __post_init__(self):
        """Initialize Gemini client if available."""
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai package is required. Install with: pip install google-generativeai"
            )
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please:\n"
                "1. Install python-dotenv: pip install python-dotenv\n"
                "2. Create .env file with: GEMINI_API_KEY=your-key-here\n"
                "3. Get free key from: https://aistudio.google.com/app/apikey"
            )
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def infer(self, prompt: str) -> str:
        """Call Gemini API and return the response."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                ),
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"API call failed: {str(e)}")

    def infer_with_context(
        self, system_prompt: str, user_prompt: str
    ) -> str:
        """Call Gemini API with system prompt for better control."""
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                ),
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"API call failed: {str(e)}")


@dataclass
class ContextBuilder:
    """Extracts and formats domain context into structured prompts."""

    def build_pet_profile(self, pet: Pet) -> Dict[str, str]:
        """Extract pet characteristics for context."""
        return {
            "name": pet.name,
            "type": pet.pet_type,
            "breed": pet.breed,
            "age": pet.age,
            "task_count": len(pet.tasks),
            "completed_tasks": len([t for t in pet.tasks if t.is_completed]),
        }

    def build_owner_profile(self, owner: Owner) -> Dict[str, str]:
        """Extract owner constraints and preferences."""
        return {
            "name": owner.name,
            "pet_count": len(owner.pets),
            "preferences": owner.preferences,
            "availability_window": self._extract_availability(owner),
        }

    def build_schedule_context(
        self, pet: Pet, owner: Owner, date: datetime
    ) -> Dict:
        """Build complete context for a scheduling decision."""
        tasks_on_date = [
            t
            for t in pet.tasks
            if t.due_date.date() == date.date() and not t.is_completed
        ]
        return {
            "pet_profile": self.build_pet_profile(pet),
            "owner_profile": self.build_owner_profile(owner),
            "date": date.strftime("%A, %B %d, %Y"),
            "pending_tasks": [
                {
                    "name": t.name,
                    "type": t.task_type.value,
                    "priority": t.default_priority,
                    "duration": t.default_duration,
                }
                for t in tasks_on_date
            ],
            "other_pets": [p.name for p in owner.pets if p.pet_id != pet.pet_id],
        }

    def build_task_context(self, task: Task, schedule: Dict) -> Dict:
        """Build context for a specific task scheduling decision."""
        return {
            "task_name": task.name,
            "task_type": task.task_type.value,
            "priority": task.default_priority,
            "duration": task.default_duration,
            "frequency": task.default_frequency,
            "pet": task.pet.name,
            "scheduled_time": f"{task.start_time.strftime('%H:%M')}-{task.end_time.strftime('%H:%M')}"
            if task.start_time
            else "Not scheduled",
            "scheduled_tasks_count": len(
                [t for t in schedule.get("scheduled_tasks", []) if t.start_time]
            ),
        }

    @staticmethod
    def _extract_availability(owner: Owner) -> str:
        """Extract time availability from owner preferences."""
        for pref in owner.preferences:
            if "available" in pref.lower():
                return pref
        return "Not specified"


@dataclass
class Retriever:
    """Retrieves similar schedules and task patterns from history."""

    schedule_history: List[Dict] = field(default_factory=list)
    task_patterns: Dict[str, int] = field(default_factory=dict)

    def retrieve_similar_schedules(
        self, pet: Pet, owner: Owner, k: int = 3
    ) -> List[Dict]:
        """Find k most similar historical schedules for the pet."""
        if not self.schedule_history:
            return []

        similarities = [
            (i, self._compute_similarity(pet, owner, schedule))
            for i, schedule in enumerate(self.schedule_history)
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [self.schedule_history[i] for i, _ in similarities[:k]]

    def retrieve_task_examples(self, task_type: TaskType, k: int = 3) -> List[str]:
        """Find k examples of successfully scheduled tasks of a given type."""
        matching = [
            task
            for task, count in self.task_patterns.items()
            if task_type.value in task.lower()
        ]
        return matching[:k] if matching else []

    def update_history(self, schedule: Dict) -> None:
        """Add a completed schedule to history."""
        self.schedule_history.append(schedule)

    def get_task_frequency_stats(self) -> Dict[str, float]:
        """Get statistics on task frequency in history."""
        if not self.task_patterns:
            return {}
        total = sum(self.task_patterns.values())
        return {
            task: freq / total for task, freq in self.task_patterns.items()
        }

    @staticmethod
    def _compute_similarity(pet: Pet, owner: Owner, schedule: Dict) -> float:
        """Compute similarity between current pet/owner and historical schedule."""
        score = 0.0
        if schedule.get("pet_type") == pet.pet_type:
            score += 0.4
        if schedule.get("pet_age") == pet.age:
            score += 0.3
        if any(pref in owner.preferences for pref in schedule.get("owner_prefs", [])):
            score += 0.3
        return score


class ExplanationGenerator:
    """Generates enhanced explanations for scheduling decisions using AI."""

    def __init__(
        self,
        model: Model = Model.GEMINI_3_5_FLASH,
        use_llm: bool = True,
        api_key: str = "",
    ):
        self.model = model
        self.use_llm = use_llm
        self.context_builder = ContextBuilder()
        self.prompt_manager = PromptManager()
        self.inference_engine = None
        
        if self.use_llm:
            try:
                final_key = api_key or os.getenv("GEMINI_API_KEY", "")
                print(f"[ExplanationGenerator] Initializing with model: {model.value}")
                print(f"[ExplanationGenerator] API key provided: {'Yes' if final_key else 'No'}")
                self.inference_engine = InferenceEngine(
                    model_name=model.value,
                    api_key=final_key,
                )
                print(f"[ExplanationGenerator] ✓ LLM enabled successfully")
            except Exception as e:
                import traceback
                print(f"[ExplanationGenerator] ✗ Failed to initialize LLM: {str(e)}")
                traceback.print_exc()
                self.use_llm = False
                self.inference_engine = None

    def generate_task_explanation(
        self, task: Task, schedule: Dict, owner: Owner
    ) -> str:
        """Generate an AI-enhanced explanation for why a task is scheduled at a specific time."""
        if not task.start_time or not task.end_time:
            return f"Task {task.name} is not yet scheduled."

        task_context = self.context_builder.build_task_context(task, schedule)
        schedule_context = self.context_builder.build_schedule_context(
            task.pet, owner, task.due_date
        )

        # Debug: Check which path we're taking
        print(f"  [DEBUG] use_llm={self.use_llm}, inference_engine={'Yes' if self.inference_engine else 'No'}")

        if self.use_llm and self.inference_engine:
            return self._generate_explanation_with_llm(
                task_context, schedule_context
            )
        else:
            print(f"  [DEBUG] Using rule-based explanation (not LLM)")
            return self._generate_explanation(task, schedule_context)

    def generate_schedule_summary(self, schedule: Dict, owner: Owner) -> str:
        """Generate a summary of the daily schedule with AI insights."""
        pet = schedule.get("pet")
        if not pet:
            return "Unable to generate summary: pet information missing."

        scheduled = schedule.get("scheduled_tasks", [])
        if not scheduled:
            return f"No tasks scheduled for {pet.name} on this date."

        summary = f"\n{'='*60}\nDAILY SCHEDULE SUMMARY FOR {pet.name.upper()}\n{'='*60}\n"
        summary += f"\nScheduled Tasks: {len(scheduled)}\n"

        for i, task in enumerate(scheduled, 1):
            explanation = self.generate_task_explanation(task, schedule, owner)
            summary += f"\n{i}. {task.name}\n"
            summary += f"   Time: {task.start_time.strftime('%H:%M')}-{task.end_time.strftime('%H:%M')}\n"
            summary += f"   Explanation: {explanation}\n"

        return summary

    def _generate_explanation_with_llm(
        self, task_context: Dict, schedule_context: Dict
    ) -> str:
        """Generate explanation using Gemini API."""
        system_prompt = """You are a pet care scheduling expert. Your job is to explain
scheduling decisions in a friendly, conversational way. Keep explanations to 2-3 sentences.
Focus on why the timing makes sense for the pet and owner."""

        prompt = self.prompt_manager.get_explanation_prompt(
            task_context, schedule_context
        )

        try:
            print(f"  [LLM] Calling Gemini for: {task_context.get('task_name')}")
            response = self.inference_engine.infer_with_context(
                system_prompt=system_prompt, user_prompt=prompt
            )
            print(f"  [LLM] ✓ Got response ({len(response)} chars)")
            return response.strip()
        except Exception as e:
            print(f"  [LLM] ✗ Error: {type(e).__name__}: {str(e)}")
            return self._generate_explanation_fallback(task_context)

    def _generate_explanation_fallback(self, task_context: Dict) -> str:
        """Fallback explanation when LLM is unavailable."""
        task_name = task_context.get("task_name", "Task")
        task_type = task_context.get("task_type", "")
        priority = task_context.get("priority", "")

        if priority.lower() == "high":
            return f"{task_name} is a high-priority task scheduled early to ensure it gets done."
        else:
            return f"{task_name} ({task_type}) is scheduled during an available time slot."

    @staticmethod
    def _generate_explanation(
        task: Task, schedule_context: Dict
    ) -> str:
        """Generate a structured explanation using available information."""
        reasons = []

        if task.priority.lower() == "high":
            reasons.append(
                f"High-priority task scheduled early to ensure completion"
            )
        elif task.priority.lower() == "medium":
            reasons.append(
                f"Medium-priority task scheduled after high-priority tasks"
            )

        if task.task_type == TaskType.FEEDING:
            reasons.append("Essential for pet health and nutrition")
        elif task.task_type == TaskType.WALK:
            reasons.append("Exercise important for physical wellbeing")
        elif task.task_type == TaskType.ENRICHMENT:
            reasons.append("Mental stimulation activity")
        elif task.task_type == TaskType.GROOMING:
            reasons.append("Hygiene and health maintenance")
        elif task.task_type == TaskType.MEDICATION:
            reasons.append("Critical health requirement")

        if len(schedule_context.get("owner_profile", {}).get("preferences", [])) > 0:
            reasons.append("Aligns with owner preferences and availability")

        if schedule_context.get("other_pets"):
            reasons.append(
                f"Scheduled to avoid conflicts with other pets' activities"
            )

        return " | ".join(reasons)


class TaskRecommender:
    """Recommends new tasks for pets based on their characteristics and owner patterns."""

    def __init__(
        self,
        model: Model = Model.GEMINI_3_5_FLASH,
        use_llm: bool = False,
        api_key: str = "",
    ):
        self.model = model
        self.use_llm = use_llm and GEMINI_AVAILABLE
        self.context_builder = ContextBuilder()
        self.prompt_manager = PromptManager()
        self.retriever = Retriever()
        self.inference_engine = None

        if self.use_llm:
            try:
                final_key = api_key or os.getenv("GEMINI_API_KEY", "")
                print(f"[TaskRecommender] Initializing with model: {model.value}")
                print(f"[TaskRecommender] API key provided: {'Yes' if final_key else 'No'}")
                self.inference_engine = InferenceEngine(
                    model_name=model.value,
                    api_key=final_key,
                )
                print(f"[TaskRecommender] ✓ LLM enabled successfully")
            except Exception as e:
                import traceback
                print(f"[TaskRecommender] ✗ Failed to initialize LLM: {str(e)}")
                traceback.print_exc()
                self.use_llm = False
                self.inference_engine = None

    def recommend_tasks(self, pet: Pet, owner: Owner) -> List[Dict]:
        """Generate task recommendations for a pet."""
        pet_profile = self.context_builder.build_pet_profile(pet)
        owner_profile = self.context_builder.build_owner_profile(owner)

        if self.use_llm and self.inference_engine:
            return self._recommend_tasks_with_llm(pet_profile, owner_profile, pet)
        else:
            return self._generate_recommendations(pet)

    def rank_recommendations(
        self, recommendations: List[Dict], owner: Owner
    ) -> List[Dict]:
        """Rank recommendations by fit with owner preferences and pet needs."""
        scored = []
        for rec in recommendations:
            score = self._compute_recommendation_score(rec, owner)
            scored.append({"recommendation": rec, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return [item["recommendation"] for item in scored]

    def get_recommendation_confidence(self, recommendation: Dict) -> float:
        """Return confidence score for a recommendation (0-1)."""
        return recommendation.get("confidence", 0.7)

    def _recommend_tasks_with_llm(
        self, pet_profile: Dict, owner_profile: Dict, pet: Pet
    ) -> List[Dict]:
        """Generate recommendations using Gemini API."""
        system_prompt = """You are a pet care expert. Recommend 2-3 new tasks that would
improve the pet's wellbeing. For each task, provide:
1. Task name
2. Task type (walk, feeding, grooming, enrichment, medication)
3. Priority (high, medium, low)
4. Frequency (daily, weekly, occasional)
5. Brief reason (1 sentence)

Format as a numbered list. Be specific and actionable."""

        prompt = self.prompt_manager.get_recommendation_prompt(
            pet_profile, owner_profile
        )

        try:
            print(f"  [LLM] Generating recommendations for {pet.name}")
            response = self.inference_engine.infer_with_context(
                system_prompt=system_prompt, user_prompt=prompt
            )
            print(f"  [LLM] ✓ Got response ({len(response)} chars)")
            print(f"  [LLM] Response:\n{response[:200]}...")  # Print first 200 chars for debug
            return self._parse_llm_recommendations(response)
        except Exception as e:
            print(f"  [LLM] ✗ Error: {type(e).__name__}: {str(e)}")
            return self._generate_recommendations(pet)

    def _parse_llm_recommendations(self, llm_response: str) -> List[Dict]:
        """Parse LLM markdown-formatted response into structured recommendations."""
        import re
        recommendations = []
        lines = llm_response.strip().split("\n")

        current_rec = {}

        for line in lines:
            # Remove markdown formatting
            clean_line = line.replace("**", "").strip()

            if not clean_line or clean_line.startswith("#"):
                continue

            # Look for numbered items (1., 2., etc.) - start of new recommendation
            if re.match(r"^\d+\.", clean_line):
                # Save previous recommendation if complete
                if current_rec and current_rec.get("task_name"):
                    self._complete_recommendation(current_rec)
                    recommendations.append(current_rec)

                # Extract task name - remove numbering
                task_match = re.match(r"^\d+\.\s*(.+?)(?:\s*\*|$)", clean_line)
                if task_match:
                    current_rec = {"task_name": task_match.group(1).strip()}
                continue

            # Handle bullet points with field: value format
            if line.strip().startswith("*") and ":" in clean_line:
                if not current_rec:
                    continue

                # Remove bullet point marker and clean
                field_line = clean_line.lstrip("* -").strip()
                if ":" not in field_line:
                    continue

                key, value = field_line.split(":", 1)
                key_lower = key.strip().lower()
                value = value.strip()

                if "name" in key_lower and not current_rec.get("task_name"):
                    current_rec["task_name"] = value
                elif "type" in key_lower:
                    # Normalize task type
                    task_type = value.lower()
                    if any(t in task_type for t in ["walk", "exercise", "morning", "sniffari"]):
                        current_rec["task_type"] = "walk"
                    elif any(t in task_type for t in ["feed", "meal", "breakfast"]):
                        current_rec["task_type"] = "feeding"
                    elif any(t in task_type for t in ["groom", "brush", "bath"]):
                        current_rec["task_type"] = "grooming"
                    elif any(t in task_type for t in ["train", "play", "enrichment", "mental"]):
                        current_rec["task_type"] = "enrichment"
                    elif any(t in task_type for t in ["medic", "health", "vet"]):
                        current_rec["task_type"] = "medication"
                    else:
                        current_rec["task_type"] = task_type

                elif "priority" in key_lower:
                    current_rec["priority"] = value.lower().split()[0]
                elif "frequency" in key_lower:
                    freq = value.lower().split()[0]
                    if freq in ["daily", "weekly", "monthly", "occasional"]:
                        current_rec["frequency"] = freq
                    else:
                        current_rec["frequency"] = "daily"
                elif any(k in key_lower for k in ["reason", "why", "benefit", "description"]):
                    current_rec["reason"] = value

        # Add last recommendation
        if current_rec and current_rec.get("task_name"):
            self._complete_recommendation(current_rec)
            recommendations.append(current_rec)

        print(f"  [LLM] Parsed {len(recommendations)} recommendations from LLM response" if recommendations else "  [LLM] No valid recommendations parsed from LLM response")
        return recommendations if recommendations else self._get_default_recommendations()

    def _complete_recommendation(self, rec: Dict) -> None:
        """Ensure recommendation has all required fields with sensible defaults."""
        if not rec.get("task_type"):
            rec["task_type"] = "enrichment"
        if not rec.get("priority"):
            rec["priority"] = "medium"
        if not rec.get("frequency"):
            rec["frequency"] = "daily"
        if not rec.get("reason"):
            rec["reason"] = "Recommended based on pet profile and schedule"
        if not rec.get("confidence"):
            rec["confidence"] = 0.85

    @staticmethod
    def _get_default_recommendations() -> List[Dict]:
        """Return default recommendations when parsing fails."""
        return [
            {
                "task_name": "Regular Exercise",
                "task_type": "walk",
                "priority": "high",
                "frequency": "daily",
                "reason": "Maintains physical health and energy levels",
                "confidence": 0.8,
            }
        ]

    @staticmethod
    def _generate_recommendations(pet: Pet) -> List[Dict]:
        """Generate task recommendations based on pet type and characteristics."""
        recommendations = []

        if pet.pet_type.lower() == "dog":
            recommendations.extend(
                [
                    {
                        "task_name": "Evening Walk",
                        "task_type": "walk",
                        "priority": "high",
                        "frequency": "daily",
                        "reason": "Dogs need regular exercise for physical health and behavioral balance",
                        "confidence": 0.95,
                    },
                    {
                        "task_name": "Training Session",
                        "task_type": "enrichment",
                        "priority": "medium",
                        "frequency": "weekly",
                        "reason": "Mental stimulation and obedience training",
                        "confidence": 0.85,
                    },
                    {
                        "task_name": "Brush Coat",
                        "task_type": "grooming",
                        "priority": "medium",
                        "frequency": "weekly",
                        "reason": "Maintain coat health and reduce shedding",
                        "confidence": 0.8,
                    },
                ]
            )

        elif pet.pet_type.lower() == "cat":
            recommendations.extend(
                [
                    {
                        "task_name": "Interactive Play",
                        "task_type": "enrichment",
                        "priority": "high",
                        "frequency": "daily",
                        "reason": "Cats need mental stimulation and physical activity indoors",
                        "confidence": 0.9,
                    },
                    {
                        "task_name": "Litter Box Cleaning",
                        "task_type": "grooming",
                        "priority": "high",
                        "frequency": "daily",
                        "reason": "Essential for hygiene and pet comfort",
                        "confidence": 0.95,
                    },
                    {
                        "task_name": "Claw Trimming",
                        "task_type": "grooming",
                        "priority": "medium",
                        "frequency": "weekly",
                        "reason": "Maintain healthy claws and prevent overgrowth",
                        "confidence": 0.75,
                    },
                ]
            )

        if pet.age > 7:
            recommendations.append(
                {
                    "task_name": "Health Check",
                    "task_type": "medication",
                    "priority": "high",
                    "frequency": "weekly",
                    "reason": "Senior pets require more frequent health monitoring",
                    "confidence": 0.9,
                }
            )

        return recommendations

    @staticmethod
    def _compute_recommendation_score(recommendation: Dict, owner: Owner) -> float:
        """Score recommendation based on owner preferences and pet needs."""
        score = recommendation.get("confidence", 0.5)

        task_type = recommendation.get("task_type", "").lower()
        for pref in owner.preferences:
            if task_type in pref.lower():
                score += 0.2

        return min(score, 1.0)
