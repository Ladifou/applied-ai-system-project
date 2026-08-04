import json
from pathlib import Path
from datetime import datetime
from pawpal_system import TaskType, Owner, Pet, Task

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)
DATA_FILE = ASSETS_DIR / "pawpal_data.json"

print(f"Data file path: {DATA_FILE}")


def serialize_owner_data(owners: dict) -> dict:
    """Convert owner data to JSON-serializable format."""
    serialized = {}
    for owner_id, owner in owners.items():
        serialized[owner_id] = {
            "name": owner.name,
            "email": owner.email,
            "phone": owner.phone,
            "address": owner.address,
            "preferences": list(owner.preferences) if hasattr(owner, 'preferences') else [],
            "pets": [
                {
                    "pet_id": pet.pet_id,
                    "name": pet.name,
                    "pet_type": pet.pet_type,
                    "breed": pet.breed,
                    "age": pet.age,
                    "tasks": [
                        {
                            "task_id": task.task_id,
                            "name": task.name,
                            "description": task.description,
                            "task_type": task.task_type.value,
                            "default_duration": task.default_duration,
                            "default_frequency": task.default_frequency,
                            "default_priority": task.default_priority,
                            "is_completed": task.is_completed,
                            "due_date": task.due_date.isoformat() if task.due_date else None,
                            "start_time": task.start_time.isoformat() if task.start_time else None,
                            "end_time": task.end_time.isoformat() if task.end_time else None
                        }
                        for task in pet.tasks
                    ]
                }
                for pet in owner.pets
            ]
        }
    return serialized


def deserialize_owner_data(data: dict) -> dict:
    """Reconstruct owner objects from JSON data."""
    owners = {}
    for owner_id, owner_data in data.items():
        owner = Owner(
            owner_id=owner_id,
            name=owner_data["name"],
            email=owner_data["email"],
            phone=owner_data["phone"],
            address=owner_data["address"]
        )
        owner.preferences = set(owner_data.get("preferences", []))

        for pet_data in owner_data.get("pets", []):
            pet = Pet(
                pet_id=pet_data["pet_id"],
                name=pet_data["name"],
                pet_type=pet_data["pet_type"],
                breed=pet_data["breed"],
                age=pet_data["age"],
                owner=owner
            )

            for task_data in pet_data.get("tasks", []):
                task = Task(
                    task_id=task_data["task_id"],
                    name=task_data["name"],
                    description=task_data["description"],
                    task_type=TaskType[task_data["task_type"].upper()],
                    default_duration=task_data["default_duration"],
                    default_frequency=task_data["default_frequency"],
                    default_priority=task_data["default_priority"],
                    pet=pet,
                    due_date=datetime.fromisoformat(task_data["due_date"]) if task_data.get("due_date") else datetime.now()
                )
                task.is_completed = task_data.get("is_completed", False)
                if task_data.get("start_time"):
                    task.start_time = datetime.fromisoformat(task_data["start_time"])
                if task_data.get("end_time"):
                    task.end_time = datetime.fromisoformat(task_data["end_time"])
                pet.add_task(task)

            owner.add_pet(pet)

        owners[owner_id] = owner

    return owners


def save_data(owners: dict, tasks: list):
    """Save current session data to file."""
    data = {
        "owners": serialize_owner_data(owners) if owners else {},
        "tasks": tasks if tasks else []
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_data() -> dict | None:
    """Load data from file if it exists."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    print("Data file is empty")
                    return None
                data = json.loads(content)
            return data
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return None
        except Exception as e:
            print(f"Could not load saved data: {str(e)}")
            return None
    else:
        print(f"Data file not found at: {DATA_FILE}")
    return None
