#!/usr/bin/env bash
# DocSentinel — 30s demo script (run with API at http://localhost:8000)
# Usage: ./scripts/demo.sh   or   bash scripts/demo.sh

set -e
BASE="${BASE_URL:-http://localhost:8000}"
API="${BASE}/api/v1"
SAMPLE="${SAMPLE_FILE:-examples/sample.txt}"

if [ ! -f "$SAMPLE" ]; then
  echo "Sample file not found: $SAMPLE (run from repo root)"
  exit 1
fi

echo "=== DocSentinel demo ==="
echo "1. Submitting assessment (file: $SAMPLE)..."
RESP=$(curl -s -X POST "$API/assessments" -F "files=@$SAMPLE" -F "scenario_id=default")
TASK_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('task_id',''))")
if [ -z "$TASK_ID" ]; then
  echo "Failed to get task_id. Response: $RESP"
  exit 1
fi
echo "   task_id: $TASK_ID"
echo ""
echo "2. Getting report..."
curl -s "$API/assessments/$TASK_ID" | python3 -m json.tool
echo ""
echo "=== Done ==="
