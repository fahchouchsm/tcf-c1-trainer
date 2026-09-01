from trainer.content import QUESTION_BANK
from trainer.storage import empty_progress
from app import due_questions


def test_question_bank_matches_written_components():
    structures = [question for question in QUESTION_BANK if question.section == "structures"]
    reading = [question for question in QUESTION_BANK if question.section == "lecture"]
    assert len(structures) == 18
    assert len(reading) == 29


def test_question_identifiers_are_unique():
    identifiers = [question.identifier for question in QUESTION_BANK]
    assert len(identifiers) == len(set(identifiers))


def test_unseen_questions_are_not_review_cards():
    assert due_questions(empty_progress()) == []
