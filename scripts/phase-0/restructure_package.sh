#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$PACKAGE_ROOT/src/mysingle"

echo "=== Phase 0: Package Restructure ==="
echo "Package root: $PACKAGE_ROOT"
echo "Source dir: $SRC_DIR"
echo ""

# 1. base → core/base 이동
echo "[1/6] Moving base/ to core/base/"
if [ -d "$SRC_DIR/base" ]; then
    mv "$SRC_DIR/base" "$SRC_DIR/core/base"
    echo "  ✓ base/ moved to core/base/"
else
    echo "  ⚠ base/ not found, skipping"
fi

# 2. logging → core/logging.py 통합
echo "[2/6] Merging logging/ to core/logging.py"
if [ -d "$SRC_DIR/logging" ]; then
    # logging/ 전체를 core/logging/로 복사 (디렉터리 유지)
    cp -r "$SRC_DIR/logging" "$SRC_DIR/core/logging"
    rm -rf "$SRC_DIR/logging"
    echo "  ✓ logging/ moved to core/logging/"
else
    echo "  ⚠ logging/ not found, skipping"
fi

# 3. metrics → core/metrics.py 통합
echo "[3/6] Merging metrics/ to core/metrics/"
if [ -d "$SRC_DIR/metrics" ]; then
    cp -r "$SRC_DIR/metrics" "$SRC_DIR/core/metrics"
    rm -rf "$SRC_DIR/metrics"
    echo "  ✓ metrics/ moved to core/metrics/"
else
    echo "  ⚠ metrics/ not found, skipping"
fi

# 4. health → core/health.py
echo "[4/6] Merging health/ to core/health/"
if [ -d "$SRC_DIR/health" ]; then
    cp -r "$SRC_DIR/health" "$SRC_DIR/core/health"
    rm -rf "$SRC_DIR/health"
    echo "  ✓ health/ moved to core/health/"
else
    echo "  ⚠ health/ not found, skipping"
fi

# 5. email → core/email.py
echo "[5/6] Merging email/ to core/email/"
if [ -d "$SRC_DIR/email" ]; then
    cp -r "$SRC_DIR/email" "$SRC_DIR/core/email"
    rm -rf "$SRC_DIR/email"
    echo "  ✓ email/ moved to core/email/"
else
    echo "  ⚠ email/ not found, skipping"
fi

# 6. audit → core/audit.py
echo "[6/6] Merging audit/ to core/audit/"
if [ -d "$SRC_DIR/audit" ]; then
    cp -r "$SRC_DIR/audit" "$SRC_DIR/core/audit"
    rm -rf "$SRC_DIR/audit"
    echo "  ✓ audit/ moved to core/audit/"
else
    echo "  ⚠ audit/ not found, skipping"
fi

echo ""
echo "=== Restructure Complete ==="
echo "Next: Run update_internal_imports.py"
