#!/usr/bin/env python3
import csv
import os
import sys

COLUMNS = ["assignment", "group", "score", "weight"]
GROUPS = ["Formative", "Summative"]
FORMATIVE_WEIGHT = 60
SUMMATIVE_WEIGHT = 40
TOTAL_WEIGHT = 100
PASS_MARK = 50


def show_error(message):
    print("Error: " + message)
    sys.exit(1)


def ask_for_filename():
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ")
    filename = filename.strip()
    if filename == "":
        show_error("no filename was entered, please type the name of a CSV file.")
    if not os.path.exists(filename):
        show_error("the file '" + filename + "' was not found.")
    if not os.path.isfile(filename):
        show_error("'" + filename + "' is not a file.")
    return filename


def check_header(reader, filename):
    if reader.fieldnames is None:
        show_error("the file '" + filename + "' is empty.")
    for column in COLUMNS:
        if column not in reader.fieldnames:
            show_error("the CSV header is missing the column '" + column + "'. "
                       "Expected columns: " + ", ".join(COLUMNS) + ".")


def row_is_blank(row):
    for column in COLUMNS:
        value = row.get(column)
        if value is not None and value.strip() != "":
            return False
    return True


def to_number(value, what, line):
    try:
        return float(value)
    except ValueError:
        show_error("line " + str(line) + ": " + what + " must be a number, got '" + value + "'.")


def read_row(row, line):
    name = (row.get("assignment") or "").strip()
    group = (row.get("group") or "").strip()
    score = (row.get("score") or "").strip()
    weight = (row.get("weight") or "").strip()

    if name == "":
        show_error("line " + str(line) + ": the assignment name is empty.")
    if group not in GROUPS:
        show_error("line " + str(line) + " (" + name + "): group must be Formative "
                   "or Summative, got '" + group + "'.")

    return {
        "assignment": name,
        "group": group,
        "score": to_number(score, "score", line),
        "weight": to_number(weight, "weight", line),
    }


def load_csv_data():
    """
    Prompts the user for a filename, checks if it exists,
    and extracts all fields into a list of dictionaries.
    """
    filename = ask_for_filename()
    assignments = []

    try:
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            check_header(reader, filename)
            line = 1
            for row in reader:
                line = line + 1
                if row_is_blank(row):
                    continue
                assignments.append(read_row(row, line))
    except OSError as error:
        show_error("the file could not be read: " + str(error))
    except UnicodeDecodeError:
        show_error("'" + filename + "' is not a readable text file (expected a UTF-8 CSV).")

    if len(assignments) == 0:
        show_error("the file '" + filename + "' contains no assignment rows.")
    return assignments


def check_scores(data):
    bad_scores = []
    for item in data:
        if item["score"] < 0 or item["score"] > 100:
            bad_scores.append("  - " + item["assignment"] + ": " + str(item["score"]))
    if len(bad_scores) > 0:
        show_error("every score must be between 0 and 100. Out of range:\n" + "\n".join(bad_scores))
    print("Score check: all scores are within 0-100.")


def sum_weights(data, group):
    total = 0
    for item in data:
        if item["group"] == group:
            total = total + item["weight"]
    return total


def check_weights(data):
    for item in data:
        if item["weight"] < 0:
            show_error("the weight of '" + item["assignment"] + "' is negative.")

    formative = sum_weights(data, "Formative")
    summative = sum_weights(data, "Summative")
    total = formative + summative

    problems = []
    if total != TOTAL_WEIGHT:
        problems.append("total weight is " + str(total) + ", it must be exactly " + str(TOTAL_WEIGHT))
    if formative != FORMATIVE_WEIGHT:
        problems.append("Formative weights add up to " + str(formative) + ", they must be exactly " + str(FORMATIVE_WEIGHT))
    if summative != SUMMATIVE_WEIGHT:
        problems.append("Summative weights add up to " + str(summative) + ", they must be exactly " + str(SUMMATIVE_WEIGHT))
    if len(problems) > 0:
        show_error("invalid weights:\n  - " + "\n  - ".join(problems))
    print("Weight check: Formative = " + str(formative) + ", Summative = " + str(summative) + ", Total = " + str(total) + ".")


def points_for(item):
    return item["score"] * item["weight"] / 100


def sum_points(data, group):
    total = 0
    for item in data:
        if item["group"] == group:
            total = total + points_for(item)
    return total


def print_transcript(data):
    print("\n--- Transcript ---")
    print(f"{'Assignment':<38} {'Group':<10} {'Score':>6} {'Weight':>7} {'Points':>7}")
    for item in data:
        print(f"{item['assignment']:<38} {item['group']:<10} {item['score']:>6.1f} "
              f"{item['weight']:>7.1f} {points_for(item):>7.2f}")


def find_failed_formatives(data):
    failed = []
    for item in data:
        if item["group"] == "Formative" and item["score"] < PASS_MARK:
            failed.append(item)
    return failed


def find_resubmissions(failed):
    if len(failed) == 0:
        return []
    highest_weight = failed[0]["weight"]
    for item in failed:
        if item["weight"] > highest_weight:
            highest_weight = item["weight"]
    resubmissions = []
    for item in failed:
        if item["weight"] == highest_weight:
            resubmissions.append(item)
    return resubmissions


def print_resubmissions(failed, resubmissions):
    if len(failed) == 0:
        print("\nNo formative assignment needs to be resubmitted.")
        return
    print("\nFailed formative assignments (below " + str(PASS_MARK) + "%):")
    for item in failed:
        print("  - " + item["assignment"] + " (score " + str(item["score"]) + "%, weight " + str(item["weight"]) + ")")
    print("\nEligible for resubmission (highest weight = " + str(resubmissions[0]["weight"]) + "):")
    for item in resubmissions:
        print("  * " + item["assignment"])


def evaluate_grades(data):
    """
    'data' is a list of dictionaries containing the assignment records.
    """
    print("\n--- Processing Grades ---")
    check_scores(data)
    check_weights(data)

    formative_points = sum_points(data, "Formative")
    summative_points = sum_points(data, "Summative")
    final_grade = formative_points + summative_points
    gpa = (final_grade / 100) * 5.0

    formative_percent = formative_points / FORMATIVE_WEIGHT * 100
    summative_percent = summative_points / SUMMATIVE_WEIGHT * 100

    print_transcript(data)
    print(f"\nFormative total: {formative_points:.2f} / {FORMATIVE_WEIGHT}  ({formative_percent:.2f}%)")
    print(f"Summative total: {summative_points:.2f} / {SUMMATIVE_WEIGHT}  ({summative_percent:.2f}%)")
    print(f"Final grade:     {final_grade:.2f} / 100")
    print(f"GPA:             {gpa:.2f} / 5.0")

    formative_ok = formative_percent >= PASS_MARK
    summative_ok = summative_percent >= PASS_MARK

    print("\n--- Category Results ---")
    print("Formative: " + f"{formative_percent:.2f}" + "% -> " + ("pass" if formative_ok else "FAIL"))
    print("Summative: " + f"{summative_percent:.2f}" + "% -> " + ("pass" if summative_ok else "FAIL"))

    print("\n--- Final Decision ---")
    if formative_ok and summative_ok:
        print("PASSED")
    else:
        print("FAILED")

    failed = find_failed_formatives(data)
    resubmissions = find_resubmissions(failed)
    print_resubmissions(failed, resubmissions)


if __name__ == "__main__":
    course_data = load_csv_data()
    evaluate_grades(course_data)
