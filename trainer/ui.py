import os
import shutil
import sys


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"


def supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


def paint(text: str, color: str = "", emphasis: bool = False) -> str:
    if not supports_color():
        return text
    style = f"{BOLD if emphasis else ''}{color}"
    return f"{style}{text}{RESET}"


def clear_screen() -> None:
    if supports_color():
        print("\033[2J\033[H", end="")


def divider() -> None:
    print(paint("─" * min(shutil.get_terminal_size((80, 20)).columns, 72), CYAN))


def title(heading: str, subtitle: str = "") -> None:
    clear_screen()
    divider()
    print(paint(f"  TCF | {heading}", MAGENTA, True))
    if subtitle:
        print(paint(f"  {subtitle}", DIM))
    divider()


def menu_choice(prompt: str, accepted_choices: set[str]) -> str:
    while True:
        answer = input(paint(prompt, CYAN)).strip().lower()
        if answer in accepted_choices:
            return answer
        print(paint(f"Choisissez : {', '.join(sorted(accepted_choices))}", YELLOW))


def wait_for_enter() -> None:
    input(paint("\nAppuyez sur Entrée pour continuer…", DIM))
