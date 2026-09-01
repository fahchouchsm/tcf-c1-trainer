# TCF Coach — C1 / B2

A focused daily terminal trainer for the **TCF Tout Public**, designed for a B2 or C1 target. It deliberately contains **no listening / audio practice**.

The trainer is based on the current public format: progressive four-choice questions for *maîtrise des structures de la langue* and *compréhension écrite*, plus the three writing-task formats. The questions and texts in this repository are original practice material, not copied exam content.

## What it gives you

- 47 original B2/C1 questions with explanations: 18 grammar/lexicon and 29 reading;
- an adaptive 10-question daily session: errors return immediately, mastered questions return later;
- focused practice or a 12-question mixed challenge;
- six TCF-style writing prompts, word counting, a self-review checklist and saved submissions;
- private local progress in `progress.json` — no account, no internet, no dependency.

## Start

```bash
cd /home/simo/MEGA/projects/tcf-c1-trainer
python3 app.py
```

Use a normal interactive terminal for the coloured interface. The app also works without colours in a redirected terminal.

## A simple daily routine

1. Complete the daily session (10 questions).
2. Read every explanation for an error, then use targeted practice for the weak area.
3. Write one task every two days. Respect the requested word range before worrying about sophisticated vocabulary.

`progress.json` contains your answer history and saved writing. Delete only that file if you deliberately want to reset your personal progress.

## Official reference

France Éducation international currently states that TCF Tout Public includes 18 questions of language structures and 29 questions of reading comprehension; its written expression test has three tasks with targets of 60–120, 120–150 and 120–180 words. Confirm the format applicable to your own registration on the [official TCF Tout Public page](https://www.france-education-international.fr/test/tcf-tout-public).

This is practice software, not an official score predictor.
