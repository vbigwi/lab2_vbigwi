#!/usr/bin/env python3
import csv
import os
import sys

REQUIRED_FIELDS = ("assignment", "group", "score", "weight")
VALID_GROUPS = ("Formative", "Summative")
FORMATIVE_WEIGHT = 60.0
SUMMATIVE_WEIGHT = 40.0
TOTAL_WEIGHT = 100.0
PASS_MARK = 50.0


def show_error(message):
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
        show_error("No filename was entered. Please type the name of a CSV file.")
    if not os.path.exists(filename):
        show_error(f"The file '{filename}' was not found.")
    if not os.path.isfile(filename):
        show_error(f"'{filename}' is not a file.")

    assignments = []

    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                show_error(f"The file '{filename}' is empty.")
            missing = [f for f in REQUIRED_FIELDS if f not in reader.fieldnames]
            if missing:
                show_error(f"The CSV header is missing the column(s): {', '.join(missing)}. "
                     f"Expected columns: {', '.join(REQUIRED_FIELDS)}.")

            for line_number, row in enumerate(reader, start=2):
                values = [(row.get(f) or "").strip() for f in REQUIRED_FIELDS]
                if all(v == "" for v in values):
                    continue
                name, group, score, weight = values
                if name == "":
                    show_error(f"Line {line_number}: the assignment name is empty.")
                if group not in VALID_GROUPS:
                    show_error(f"Line {line_number} ('{name}'): group must be Formative or "
                         f"Summative, got '{group}'.")
                try:
                    score = float(score)
                except ValueError:
                    show_error(f"Line {line_number} ('{name}'): score must be a number, got '{score}'.")
                try:
                    weight = float(weight)
                except ValueError:
                    show_error(f"Line {line_number} ('{name}'): weight must be a number, got '{weight}'.")
                assignments.append({
                    'assignment': name,
                    'group': group,
                    'score': score,
                    'weight': weight
                })
    except OSError as e:
        show_error(f"An error occurred while reading the file: {e}")
    except UnicodeDecodeError:
        show_error(f"'{filename}' is not a readable text file (expected UTF-8 CSV).")

    if not assignments:
        show_error(f"The file '{filename}' contains no assignment rows.")
    return assignments


def check_scores(data):
    problems = [f"  - {a['assignment']}: {a['score']:g}"
                for a in data if not 0 <= a['score'] <= 100]
    if problems:
        show_error("every score must be between 0 and 100. Out of range:\n" + "\n".join(problems))
    print("Score check: all scores are within 0-100.")


def check_weights(data):
    negative = [a['assignment'] for a in data if a['weight'] < 0]
    if negative:
        show_error("weights cannot be negative: " + ", ".join(negative))

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
        show_error("invalid weights:\n  - " + "\n  - ".join(problems))
    print(f"Weight check: Formative = {formative:g}, Summative = {summative:g}, Total = {total:g}.")


def get_points(data, group=None):
    return sum(a['score'] * a['weight'] / 100.0
               for a in data if group is None or a['group'] == group)


def evaluate_grades(data):
    """
    'data' is a list of dictionaries containing the assignment records.
    """
    print("\n--- Processing Grades ---")

    check_scores(data)

    check_weights(data)

    formative_total = get_points(data, "Formative")
    summative_total = get_points(data, "Summative")
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

    formative_passed = formative_pct >= PASS_MARK
    summative_passed = summative_pct >= PASS_MARK
    passed = formative_passed and summative_passed

    print("\n--- Category Results ---")
    print(f"Formative: {formative_pct:.2f}% -> {'pass' if formative_passed else 'FAIL'} (need {PASS_MARK:g}%)")
    print(f"Summative: {summative_pct:.2f}% -> {'pass' if summative_passed else 'FAIL'} (need {PASS_MARK:g}%)")

    failed_formatives = [a for a in data
                         if a['group'] == "Formative" and a['score'] < PASS_MARK]
    resubmission = []
    if failed_formatives:
        highest_weight = failed_formatives[0]['weight']
        for a in failed_formatives:
            if a['weight'] > highest_weight:
                highest_weight = a['weight']
        resubmission = [a for a in failed_formatives if a['weight'] == highest_weight]

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
    course_data = load_csv_data()

    evaluate_grades(course_data)
