#!/usr/bin/env bash

ARCHIVE_DIR="archive"
GRADES_FILE="grades.csv"
LOG_FILE="organizer.log"

if [ ! -d "$ARCHIVE_DIR" ]; then
    mkdir -p "$ARCHIVE_DIR" || { echo "Error: could not create the '$ARCHIVE_DIR' directory."; exit 1; }
    echo "Created the '$ARCHIVE_DIR' directory."
else
    echo "The '$ARCHIVE_DIR' directory already exists."
fi

if [ ! -f "$GRADES_FILE" ]; then
    echo "Error: '$GRADES_FILE' was not found in $(pwd). Nothing to archive."
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVED_NAME="grades_${TIMESTAMP}.csv"

if ! mv "$GRADES_FILE" "$ARCHIVE_DIR/$ARCHIVED_NAME"; then
    echo "Error: could not move '$GRADES_FILE' into '$ARCHIVE_DIR'."
    exit 1
fi
echo "Archived '$GRADES_FILE' as '$ARCHIVE_DIR/$ARCHIVED_NAME'."

if ! : > "$GRADES_FILE"; then
    echo "Error: could not create a new empty '$GRADES_FILE'."
    exit 1
fi
echo "Created a new empty '$GRADES_FILE'."

echo "[$TIMESTAMP] archived '$GRADES_FILE' -> '$ARCHIVE_DIR/$ARCHIVED_NAME'" >> "$LOG_FILE"
echo "Logged the operation in '$LOG_FILE'."
