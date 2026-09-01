#!/usr/bin/env python3
import random
import textwrap
from datetime import date
from pathlib import Path

from trainer.content import CONNECTORS, QUESTION_BANK, WRITING_PROMPTS, Question
from trainer.storage import load_progress, record_answer, save_progress, update_streak
from trainer.ui import CYAN, DIM, GREEN, RED, YELLOW, divider, menu_choice, paint, title, wait_for_enter


PROJECT_ROOT = Path(__file__).parent
LETTERS = ("a", "b", "c", "d")


def wrap(copy: str) -> str:
    return "\n".join(textwrap.wrap(copy, width=76, break_long_words=False))


def due_questions(learner_progress: dict) -> list[Question]:
    today = date.today().isoformat()
    return [question for question in QUESTION_BANK if (history := learner_progress["answers"].get(question.identifier)) and history["due"] <= today]


def daily_questions(learner_progress: dict, count: int) -> list[Question]:
    due = due_questions(learner_progress)
    unseen = [question for question in QUESTION_BANK if question.identifier not in learner_progress["answers"]]
    pool = due + [question for question in unseen if question not in due]
    return random.sample(pool or list(QUESTION_BANK), min(count, len(pool or QUESTION_BANK)))


def ask_question(question: Question, position: int, total: int) -> bool:
    title(f"Question {position}/{total} · {question.section.upper()} · {question.level}")
    if question.passage:
        print(wrap(question.passage), "\n")
    print(paint(wrap(question.prompt), CYAN, True), "\n")
    for letter, choice in zip(LETTERS, question.choices):
        print(f"  {paint(letter.upper(), YELLOW, True)}  {choice}")
    answer = menu_choice("\nVotre réponse [a-d] : ", set(LETTERS))
    is_correct = LETTERS.index(answer) == question.correct_choice
    reveal_answer(question, is_correct)
    return is_correct


def reveal_answer(question: Question, is_correct: bool) -> None:
    color = GREEN if is_correct else RED
    verdict = "✓ Correct" if is_correct else "✗ À revoir"
    print("\n" + paint(verdict, color, True))
    if not is_correct:
        correct_letter = LETTERS[question.correct_choice].upper()
        print(paint(f"Réponse : {correct_letter} — {question.choices[question.correct_choice]}", GREEN))
    print(wrap(question.explanation))
    wait_for_enter()


def run_questions(questions: list[Question], learner_progress: dict) -> None:
    correct_answers = 0
    for position, question in enumerate(questions, start=1):
        is_correct = ask_question(question, position, len(questions))
        record_answer(learner_progress, question.identifier, is_correct)
        correct_answers += is_correct
    save_progress(PROJECT_ROOT, learner_progress)
    show_session_summary(correct_answers, len(questions))


def show_session_summary(correct_answers: int, total_questions: int) -> None:
    title("Bilan de séance")
    percentage = round(correct_answers * 100 / total_questions)
    color = GREEN if percentage >= 75 else YELLOW if percentage >= 55 else RED
    print(paint(f"{correct_answers}/{total_questions} · {percentage}%", color, True))
    advice = "Très solide : augmente progressivement la difficulté." if percentage >= 75 else "Repère les explications et reviens demain." if percentage >= 55 else "Revois les erreurs avant une nouvelle série."
    print("\n" + advice)
    wait_for_enter()


def choose_section() -> str:
    title("Entraînement ciblé", "Travaille une compétence à la fois.")
    print("  1  Structures de la langue")
    print("  2  Compréhension écrite")
    print("  3  Mélange B2/C1")
    choice = menu_choice("\nChoix : ", {"1", "2", "3"})
    return {"1": "structures", "2": "lecture", "3": "mix"}[choice]


def targeted_questions(section: str) -> list[Question]:
    available = list(QUESTION_BANK) if section == "mix" else [question for question in QUESTION_BANK if question.section == section]
    return random.sample(available, min(10, len(available)))


def read_writing() -> str:
    lines: list[str] = []
    print(paint("Écrivez votre texte. Tapez /fin seul sur une ligne pour terminer.\n", DIM))
    while True:
        line = input()
        if line.strip() == "/fin":
            return "\n".join(lines).strip()
        lines.append(line)


def writing_word_count(submission: str) -> int:
    return len([word for word in submission.replace("’", " ").split() if word])


def run_writing(learner_progress: dict) -> None:
    prompt = random.choice(WRITING_PROMPTS)
    title(prompt.task, f"Objectif officiel : {prompt.target_words}")
    print(wrap(prompt.prompt), "\n")
    print(paint("Checklist", YELLOW, True))
    for point in prompt.checklist:
        print(f"  • {point}")
    submission = read_writing()
    save_writing(learner_progress, prompt.identifier, submission)
    review_writing(prompt, submission)


def save_writing(learner_progress: dict, prompt_id: str, submission: str) -> None:
    learner_progress["writing"].append({"date": date.today().isoformat(), "prompt": prompt_id, "words": writing_word_count(submission), "text": submission})
    save_progress(PROJECT_ROOT, learner_progress)


def review_writing(prompt, submission: str) -> None:
    title("Auto-évaluation", "La correction humaine reste indispensable pour une note fiable.")
    print(paint(f"{writing_word_count(submission)} mots — objectif : {prompt.target_words}", CYAN, True))
    print("\nVérifiez : consigne traitée · paragraphes · connecteurs · nuances · accords.")
    print("Connecteurs à employer avec justesse : " + ", ".join(random.sample(CONNECTORS, 4)))
    wait_for_enter()


def show_progress(learner_progress: dict) -> None:
    title("Progression")
    attempts = learner_progress["answers"]
    right = sum(history["right"] for history in attempts.values())
    wrong = sum(history["wrong"] for history in attempts.values())
    total = right + wrong
    accuracy = f"{round(right * 100 / total)}%" if total else "—"
    print(f"Série actuelle : {paint(str(learner_progress['streak']) + ' jour(s)', GREEN, True)}")
    print(f"Questions répondue(s) : {total} · Réussite : {accuracy}")
    print(f"Cartes à revoir aujourd'hui : {len(due_questions(learner_progress))}")
    print(f"Productions écrites sauvegardées : {len(learner_progress['writing'])}")
    divider()
    show_weak_topics(attempts)
    wait_for_enter()


def show_weak_topics(attempts: dict) -> None:
    weak_identifiers = [identifier for identifier, history in attempts.items() if history["wrong"] > history["right"]]
    if not weak_identifiers:
        print("Aucun point faible net pour le moment. Continue à alimenter tes statistiques.")
        return
    labels = {question.identifier: f"{question.section} {question.level}" for question in QUESTION_BANK}
    print(paint("À reprendre en priorité :", YELLOW, True))
    print(" · ".join(labels[identifier] for identifier in weak_identifiers[:6]))


def show_home(learner_progress: dict) -> None:
    title("Coach quotidien C1 / B2", "TCF Tout Public · entraînement sans compréhension orale")
    print(paint(f"Série : {learner_progress['streak']} jour(s)  |  À revoir : {len(due_questions(learner_progress))}", GREEN))
    print("\n  1  Séance du jour — 10 questions intelligemment sélectionnées")
    print("  2  Entraînement ciblé — structures, lecture ou mélange")
    print("  3  Défi express — 12 questions mixtes")
    print("  4  Expression écrite — sujets, compteur de mots, checklist")
    print("  5  Ma progression")
    print("  q  Quitter")


def run_app() -> None:
    learner_progress = load_progress(PROJECT_ROOT)
    update_streak(learner_progress)
    while True:
        show_home(learner_progress)
        choice = menu_choice("\nChoix : ", {"1", "2", "3", "4", "5", "q"})
        if choice == "q":
            save_progress(PROJECT_ROOT, learner_progress)
            print(paint("À demain. Régularité > perfection.", GREEN, True))
            return
        if choice == "1":
            run_questions(daily_questions(learner_progress, 10), learner_progress)
        elif choice == "2":
            run_questions(targeted_questions(choose_section()), learner_progress)
        elif choice == "3":
            run_questions(daily_questions(learner_progress, 12), learner_progress)
        elif choice == "4":
            run_writing(learner_progress)
        else:
            show_progress(learner_progress)


if __name__ == "__main__":
    run_app()
