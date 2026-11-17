#!/usr/bin/env python3
"""ALU Transcript Generator.

Reads a CSV file of course grades, validates it, computes the final grade
and GPA, decides whether the student passed, and lists the failed formative
assignments that can be resubmitted.
"""
import csv
import os
import sys

REQUIRED_FIELDS = ("assignment", "group", "score", "weight")
VALID_GROUPS = ("Formative", "Summative")
FORMATIVE_WEIGHT = 60.0
SUMMATIVE_WEIGHT = 40.0
TOTAL_WEIGHT = 100.0
PASS_MARK = 50.0


def fail(message):
    """Print a clear error message and stop the program."""
    print(f"Error: {message}")
    sys.exit(1)


def load_csv_data():
    """
    Prompts the user for a filename, checks if it exists,
    and extracts all fields into a list of dictionaries.

    Every row is validated while it is read: the four columns must be
    present, the group must be Formative or Summative, and the score and
    weight must be numbers. Completely empty rows are skipped.
    """
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()

    if filename == "":
        fail("No filename was entered. Please type the name of a CSV file.")
    if not os.path.exists(filename):
        fail(f"The file '{filename}' was not found.")
    if not os.path.isfile(filename):
        fail(f"'{filename}' is not a file.")

    assignments = []

    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                fail(f"The file '{filename}' is empty.")
            missing = [f for f in REQUIRED_FIELDS if f not in reader.fieldnames]
            if missing:
                fail(f"The CSV header is missing the column(s): {', '.join(missing)}. "
                     f"Expected columns: {', '.join(REQUIRED_FIELDS)}.")

            for line_number, row in enumerate(reader, start=2):
                values = [(row.get(f) or "").strip() for f in REQUIRED_FIELDS]
                if all(v == "" for v in values):
                    continue  # blank line, ignore it
                name, group, score, weight = values
                if name == "":
                    fail(f"Line {line_number}: the assignment name is empty.")
                if group not in VALID_GROUPS:
                    fail(f"Line {line_number} ('{name}'): group must be Formative or "
                         f"Summative, got '{group}'.")
                try:
                    score = float(score)
                except ValueError:
                    fail(f"Line {line_number} ('{name}'): score must be a number, got '{score}'.")
                try:
                    weight = float(weight)
                except ValueError:
                    fail(f"Line {line_number} ('{name}'): weight must be a number, got '{weight}'.")
                assignments.append({
                    'assignment': name,
                    'group': group,
                    'score': score,
                    'weight': weight
                })
    except OSError as e:
        fail(f"An error occurred while reading the file: {e}")
    except UnicodeDecodeError:
        fail(f"'{filename}' is not a readable text file (expected UTF-8 CSV).")

    if not assignments:
        fail(f"The file '{filename}' contains no assignment rows.")
    return assignments


def validate_scores(data):
    """a) Every score must be a percentage between 0 and 100."""
    problems = [f"  - {a['assignment']}: {a['score']:g}"
                for a in data if not 0 <= a['score'] <= 100]
    if problems:
        fail("every score must be between 0 and 100. Out of range:\n" + "\n".join(problems))
    print("Score check: all scores are within 0-100.")


def validate_weights(data):
    """b) Weights must total 100, with Formative = 60 and Summative = 40."""
    negative = [a['assignment'] for a in data if a['weight'] < 0]
    if negative:
        fail("weights cannot be negative: " + ", ".join(negative))

    formative = sum(a['weight'] for a in data if a['group'] == "Formative")
    summative = sum(a['weight'] for a in data if a['group'] == "Summative")
    total = formative + summative

    problems = []
    if abs(total - TOTAL_WEIGHT) > 1e-9:
        problems.append(f"total weight is {total:g}, it must be exactly {TOTAL_WEIGHT:g}")
    if abs(formative - FORMATIVE_WEIGHT) > 1e-9:
        problems.append(f"Formative weights add up to {formative:g}, they must be exactly {FORMATIVE_WEIGHT:g}")
    if abs(summative - SUMMATIVE_WEIGHT) > 1e-9:
        problems.append(f"Summative weights add up to {summative:g}, they must be exactly {SUMMATIVE_WEIGHT:g}")
    if problems:
        fail("invalid weights:\n  - " + "\n  - ".join(problems))
    print(f"Weight check: Formative = {formative:g}, Summative = {summative:g}, Total = {total:g}.")


def weighted_total(data, group=None):
    """Sum of score * weight / 100 for the given group (or all rows)."""
    return sum(a['score'] * a['weight'] / 100.0
               for a in data if group is None or a['group'] == group)


def evaluate_grades(data):
    """
    'data' is a list of dictionaries containing the assignment records.
    """
    print("\n--- Processing Grades ---")

    # a) Check if all scores are percentage based (0-100)
    validate_scores(data)

    # b) Validate total weights (Total=100, Summative=40, Formative=60)
    validate_weights(data)

    # c) Calculate the Final Grade and GPA
    formative_total = weighted_total(data, "Formative")
    summative_total = weighted_total(data, "Summative")
    final_grade = formative_total + summative_total
    gpa = (final_grade / 100.0) * 5.0

    formative_pct = formative_total / FORMATIVE_WEIGHT * 100.0
    summative_pct = summative_total / SUMMATIVE_WEIGHT * 100.0

    print("\n--- Transcript ---")
    print(f"{'Assignment':<38} {'Group':<10} {'Score':>6} {'Weight':>7} {'Points':>7}")
    for a in data:
        points = a['score'] * a['weight'] / 100.0
        print(f"{a['assignment']:<38} {a['group']:<10} {a['score']:>6.1f} "
              f"{a['weight']:>7.1f} {points:>7.2f}")
    print(f"\nFormative total: {formative_total:.2f} / {FORMATIVE_WEIGHT:g}  ({formative_pct:.2f}%)")
    print(f"Summative total: {summative_total:.2f} / {SUMMATIVE_WEIGHT:g}  ({summative_pct:.2f}%)")
    print(f"Final grade:     {final_grade:.2f} / 100")
    print(f"GPA:             {gpa:.2f} / 5.0")

    # d) Determine Pass/Fail status (>= 50% in BOTH categories)
    formative_passed = formative_pct >= PASS_MARK
    summative_passed = summative_pct >= PASS_MARK
    passed = formative_passed and summative_passed

    print("\n--- Category Results ---")
    print(f"Formative: {formative_pct:.2f}% -> {'pass' if formative_passed else 'FAIL'} (need {PASS_MARK:g}%)")
    print(f"Summative: {summative_pct:.2f}% -> {'pass' if summative_passed else 'FAIL'} (need {PASS_MARK:g}%)")

    # e) Check for failed formative assignments (< 50%) and find the
    #    one(s) with the highest weight for resubmission.
    failed_formatives = [a for a in data
                         if a['group'] == "Formative" and a['score'] < PASS_MARK]
    resubmission = []
    if failed_formatives:
        highest_weight = failed_formatives[0]['weight']
        for a in failed_formatives:
            if a['weight'] > highest_weight:
                highest_weight = a['weight']
        resubmission = [a for a in failed_formatives if a['weight'] == highest_weight]

    # f) Print the final decision and the resubmission options
    print("\n--- Final Decision ---")
    print("PASSED" if passed else "FAILED")

    if failed_formatives:
        print(f"\nFailed formative assignments (below {PASS_MARK:g}%):")
        for a in failed_formatives:
            print(f"  - {a['assignment']} (score {a['score']:g}%, weight {a['weight']:g})")
        label = "assignment is" if len(resubmission) == 1 else "assignments are"
        print(f"\nEligible for resubmission (highest weight = {resubmission[0]['weight']:g}), "
              f"the following {label}:")
        for a in resubmission:
            print(f"  * {a['assignment']}")
    else:
        print("\nNo formative assignment needs to be resubmitted.")

    return passed


if __name__ == "__main__":
    # 1. Load the data
    course_data = load_csv_data()

    # 2. Process the features
    evaluate_grades(course_data)
