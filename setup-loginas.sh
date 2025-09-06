#!/bin/bash
set -e

BACKUP_DIR="$HOME/bakkie-op"
REPORT_FILE="cleanup_report.txt"

echo "📦 Backup maken..."
tar -czf "$BACKUP_DIR/cleanup_$(date +%Y%m%d_%H%M%S).tar.gz" . >/dev/null 2>&1
echo "✅ Backup opgeslagen in $BACKUP_DIR"

echo "🔍 Project scannen op overbodige code..."

{
  echo "=== MERGE CONFLICT MARKERS ==="
  grep -R --line-number '<<<<<<<\|=======\|>>>>>>>' . || echo "Geen gevonden."

  echo -e "\n=== DUBBELE Profile CLASSES ==="
  grep -R --line-number "class Profile" accounts/ || echo "Geen dubbele Profile classes."

  echo -e "\n=== DUBBELE IMPORTS ==="
  grep -R --line-number "import " dashboards/ accounts/ | sort | uniq -d || echo "Geen dubbele imports."

  echo -e "\n=== MEERDERE login_required ==="
  grep -R --line-number "login_required" dashboards/ || echo "Geen dubbele decorators gevonden."
} > "$REPORT_FILE"

echo "📄 Rapport klaar: $REPORT_FILE"
echo "👉 Bekijk dit bestand en beslis wat er nog handmatig weg kan."
