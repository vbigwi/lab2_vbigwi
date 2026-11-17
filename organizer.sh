#!/usr/bin/env bash
# organizer.sh - archives grades.csv with a timestamp, resets the workspace
# and records what it did in organizer.log.

ARCHIVE_DIR="archive"
GRADES_FILE="grades.csv"
LOG_FILE="organizer.log"

# 1. Archive directory: create it if it does not exist yet.
if [ ! -d "$ARCHIVE_DIR" ]; then
    mkdir -p "$ARCHIVE_DIR" || { echo "Error: could not create the '$ARCHIVE_DIR' directory."; exit 1; }
    echo "Created the '$ARCHIVE_DIR' directory."
else
    echo "The '$ARCHIVE_DIR' directory already exists."
fi

# 2. Archival process: the grades file must exist before it can be moved.
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

# 3. Workspace reset: start a fresh, empty grades file for the next batch.
if ! : > "$GRADES_FILE"; then
    echo "Error: could not create a new empty '$GRADES_FILE'."
    exit 1
fi
echo "Created a new empty '$GRADES_FILE'."

# 4. Logging: append the details of this run to the log file.
echo "[$TIMESTAMP] archived '$GRADES_FILE' -> '$ARCHIVE_DIR/$ARCHIVED_NAME'" >> "$LOG_FILE"
echo "Logged the operation in '$LOG_FILE'."
