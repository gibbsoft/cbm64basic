#!/usr/bin/env bash
# CBM64 BASIC Demo Script
# =======================
# Demonstrates the prompt_toolkit-based editor

set -e

cd "$(dirname "$0")"

echo "=== CBM64 BASIC Editor Demo ==="
echo ""
echo "1. Testing program entry with auto-formatting..."
echo "   Type: 10 PRINT \"HELLO WORLD\""
echo "   Output: Lines are auto-formatted and highlighted"
echo ""
echo "2. Testing syntax highlighting colors..."
echo "   Keywords: Blue (PRINT, LET, GOTO, etc.)"
echo "   Numbers: Yellow (1, 2, 3, etc.)"
echo "   Strings: Green (\"quoted text\")"
echo "   Variables: Cyan (A, B\$, C%)"
echo "   Line numbers: Orange (10, 20, 30)"
echo ""
echo "3. Starting interactive editor..."
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 -m src.cbm64_editor
