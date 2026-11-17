# Lab 2 - ALU Transcript Generator

Individual Coding Lab, Introduction to Python Programming and Databases.

This repository contains a Python application that turns a CSV file of
course grades into a transcript (final grade, GPA, pass/fail decision and
resubmission advice), and a Bash script that archives the grades file and
keeps a log of every archive.

## Files

| File | Purpose |
| ---- | ------- |
| `grade-evaluator.py` | The transcript generator |
| `grades.csv` | Sample grades used to test the program |
| `organizer.sh` | Archives `grades.csv`, resets the workspace and logs the action |
| `Readme.md` | This document |

## Running the transcript generator

```
python3 grade-evaluator.py
Enter the name of the CSV file to process (e.g., grades.csv): grades.csv
```

The CSV must have the header `assignment,group,score,weight`, where `group`
is `Formative` or `Summative`, `score` is a percentage between 0 and 100 and
`weight` is the share of the final grade.

What the program does, in order:

1. **Grade validation** - every score must be between 0 and 100.
2. **Weight validation** - all weights must add up to exactly 100, with the
   Formative assignments adding up to 60 and the Summative ones to 40.
3. **GPA calculation** - each assignment contributes `score x weight / 100`
   points. The final grade is the sum of those points and
   `GPA = (Total Grade / 100) x 5.0`.
4. **Final decision** - the student passes only with at least 50% in *both*
   the Formative category and the Summative category. The program prints
   `PASSED` or `FAILED`.
5. **Resubmission logic** - failed formative assignments (below 50%) are
   listed, and the one(s) with the highest weight are flagged as eligible for
   resubmission. When several share the highest weight, all of them are shown.

### Example with the provided `grades.csv`

```
Formative total: 34.00 / 60  (56.67%)
Summative total: 26.00 / 40  (65.00%)
Final grade:     60.00 / 100
GPA:             3.00 / 5.0

--- Final Decision ---
PASSED

Failed formative assignments (below 50%):
  - Group Exercise (score 40%, weight 20)
  - Functions and Debugging Lab (score 45%, weight 20)

Eligible for resubmission (highest weight = 20), the following assignments are:
  * Group Exercise
  * Functions and Debugging Lab
```

### Error handling

The program stops with a clear message, instead of crashing, when:

- no filename is given, the file does not exist, or it is not a file;
- the file is empty or its header is missing one of the four columns;
- a row has an empty assignment name, an unknown group, or a score/weight
  that is not a number (blank rows are skipped);
- a score is outside 0-100;
- the weights do not total 100 or do not respect the 60/40 split;
- the file has no assignment rows at all.

## Running the organizer

```
bash organizer.sh
```

Each run:

1. creates the `archive/` directory if it is missing;
2. renames `grades.csv` to `archive/grades_YYYYMMDD-HHMMSS.csv`;
3. creates a new, empty `grades.csv` so the workspace is ready for the next
   batch of grades;
4. appends a line with the timestamp, the original filename and the archived
   filename to `organizer.log`, which keeps growing across runs.

If `grades.csv` is missing the script reports it and exits with status 1.
