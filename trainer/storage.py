import json
from datetime import date, timedelta
from pathlib import Path


def empty_progress() -> dict:
    return {"answers": {}, "writing": [], "streak": 0, "last_day": ""}


def progress_path(project_root: Path) -> Path:
    return project_root / "progress.json"


def load_progress(project_root: Path) -> dict:
    saved_progress = progress_path(project_root)
    if not saved_progress.exists():
        return empty_progress()
    try:
        with saved_progress.open(encoding="utf-8") as progress_file:
            loaded_progress = json.load(progress_file)
    except json.JSONDecodeError:
        saved_progress.replace(saved_progress.with_suffix(".corrupt.json"))
        return empty_progress()
    return validate_progress(loaded_progress)


def validate_progress(loaded_progress: object) -> dict:
    if not isinstance(loaded_progress, dict):
        return empty_progress()
    answers = sanitized_answers(loaded_progress.get("answers", {}))
    writing = loaded_progress.get("writing", [])
    if answers is None or not isinstance(writing, list):
        return empty_progress()
    streak = loaded_progress.get("streak", 0)
    last_day = loaded_progress.get("last_day", "")
    if not isinstance(streak, int) or streak < 0 or not isinstance(last_day, str):
        return empty_progress()
    return {"answers": answers, "writing": writing, "streak": streak, "last_day": last_day}


def sanitized_answers(candidate_answers: object) -> dict | None:
    if not isinstance(candidate_answers, dict):
        return None
    sanitized = {}
    for identifier, history in candidate_answers.items():
        cleaned_history = sanitized_history(history)
        if not isinstance(identifier, str) or cleaned_history is None:
            return None
        sanitized[identifier] = cleaned_history
    return sanitized


def sanitized_history(candidate_history: object) -> dict | None:
    if not isinstance(candidate_history, dict):
        return None
    right = candidate_history.get("right")
    wrong = candidate_history.get("wrong")
    due = candidate_history.get("due")
    if not isinstance(right, int) or not isinstance(wrong, int) or not valid_due_date(due):
        return None
    if right < 0 or wrong < 0:
        return None
    return {"right": right, "wrong": wrong, "due": due}


def valid_due_date(candidate_due: object) -> bool:
    if not isinstance(candidate_due, str):
        return False
    try:
        date.fromisoformat(candidate_due)
    except ValueError:
        return False
    return True


def save_progress(project_root: Path, learner_progress: dict) -> None:
    target_path = progress_path(project_root)
    temporary_path = target_path.with_suffix(".next.json")
    with temporary_path.open("w", encoding="utf-8") as progress_file:
        json.dump(learner_progress, progress_file, ensure_ascii=False, indent=2)
    temporary_path.replace(target_path)


def record_answer(learner_progress: dict, identifier: str, is_correct: bool) -> None:
    question_history = learner_progress["answers"].setdefault(identifier, {"right": 0, "wrong": 0, "due": ""})
    field = "right" if is_correct else "wrong"
    question_history[field] += 1
    question_history["due"] = next_review_date(question_history, is_correct)


def next_review_date(question_history: dict, is_correct: bool) -> str:
    if not is_correct:
        return date.today().isoformat()
    correct_count = question_history["right"]
    review_days = 1 if correct_count == 1 else 3 if correct_count == 2 else 7
    return (date.today() + timedelta(days=review_days)).isoformat()


def update_streak(learner_progress: dict) -> None:
    today = date.today()
    last_day = learner_progress["last_day"]
    if last_day == today.isoformat():
        return
    yesterday = (today - timedelta(days=1)).isoformat()
    learner_progress["streak"] = learner_progress["streak"] + 1 if last_day == yesterday else 1
    learner_progress["last_day"] = today.isoformat()
