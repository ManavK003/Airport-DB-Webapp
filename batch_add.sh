#!/bin/bash

# Directory with your CSV files
DIR="ML Data/Arrival_Departure"

# Commit message you want to use
COMMIT_MSG="downloaded and added bts on time datasets from 2018-2025. pushing files in batches because file sizes way too big to mass push"

# Find all CSV files in the directory (sorted)
FILES=("$DIR"/*.csv)

# Total number of files
TOTAL=${#FILES[@]}

# Batch size (can increase later if this works)
BATCH_SIZE=1

# Counter for batches
count=0

# Timestamp function
timestamp() {
    date +"[%Y-%m-%d %H:%M:%S]"
}

while [ $count -lt $TOTAL ]; do
    echo "$(timestamp) Adding batch $((count / BATCH_SIZE + 1))..."

    # Select next batch files
    BATCH_FILES=("${FILES[@]:count:BATCH_SIZE}")

    # Add each file with logging
    for file in "${BATCH_FILES[@]}"; do
        echo "$(timestamp) Adding $file..."
        if git add "$file"; then
            echo "$(timestamp) Successfully added $file"
        else
            echo "$(timestamp) ❌ Failed to add $file"
        fi
    done

    # Commit if there are staged changes
    if ! git diff --cached --quiet; then
        echo "$(timestamp) Committing batch..."
        if git commit -m "$COMMIT_MSG"; then
            echo "$(timestamp) ✅ Commit successful"
        else
            echo "$(timestamp) ❌ Commit failed"
        fi
    else
        echo "$(timestamp) No changes to commit for this batch."
    fi

    # Increment count
    count=$((count + BATCH_SIZE))
done

echo "$(timestamp) 🎉 All batches processed."
