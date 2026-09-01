from datetime import date

from trainer.storage import empty_progress, next_review_date, record_answer, validate_progress


def test_wrong_answer_is_due_today():
    learner_progress = empty_progress()
    record_answer(learner_progress, "s01", False)
    assert learner_progress["answers"]["s01"]["due"] == date.today().isoformat()


def test_correct_answer_is_due_tomorrow():
    learner_progress = empty_progress()
    record_answer(learner_progress, "s01", True)
    assert learner_progress["answers"]["s01"]["due"] > date.today().isoformat()


def test_invalid_saved_progress_resets_safely():
    assert validate_progress(["not", "a", "mapping"]) == empty_progress()


def test_malformed_question_history_resets_safely():
    malformed_progress = {"answers": {"s01": {"right": "many"}}, "writing": []}
    assert validate_progress(malformed_progress) == empty_progress()


def test_invalid_review_date_resets_safely():
    malformed_progress = {"answers": {"s01": {"right": 1, "wrong": 0, "due": "later"}}, "writing": []}
    assert validate_progress(malformed_progress) == empty_progress()


def test_review_spacing_increases_after_second_success():
    assert next_review_date({"right": 2}, True) > date.today().isoformat()
