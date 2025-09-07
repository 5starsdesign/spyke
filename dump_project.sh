#!/bin/bash
set -e

OUTFILE="project_dump.txt"
> "$OUTFILE"

# Structuur opslaan
echo "### PROJECT STRUCTUUR ###" >> "$OUTFILE"
tree -I 'static|staticfiles|__pycache__|migrations|tests' >> "$OUTFILE"
echo "" >> "$OUTFILE"

# Relevante bestanden opsommen
FILES=$(find . \
  -type f \
  \( -name "*.py" -o -name "*.html" \) \
  ! -path "./static/*" \
  ! -path "./staticfiles/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/migrations/*" \
  ! -path "./tests/*" \
  ! -name "manage.py" \
)

for f in $FILES; do
  echo "### FILE: $f ###" >> "$OUTFILE"
  cat "$f" >> "$OUTFILE"
  echo -e "\n" >> "$OUTFILE"
done

# Backup
cp "$OUTFILE" ~/bakkie-op/project_dump_$(date +%F_%H-%M-%S).txt
