#!/bin/bash
set -e

echo "=== Generating Python stubs from Proto files ==="

# Change to package root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PACKAGE_ROOT"

# Check buf is installed
if ! command -v buf &> /dev/null; then
    echo "❌ buf CLI not found. Install it first:"
    echo "   brew install bufbuild/buf/buf"
    exit 1
fi

# Change to protos directory for buf generate
cd protos

# Generate Python stubs
echo "Generating Python stubs..."
buf generate

# Fix nested protos directory if exists
if [ -d "src/mysingle/protos/protos" ]; then
    echo "Fixing nested protos directory..."
    mv src/mysingle/protos/protos/* src/mysingle/protos/
    rmdir src/mysingle/protos/protos
fi

# Fix import paths
echo "Fixing import paths..."
.venv/bin/python scripts/fix_proto_imports.py

# Create __init__.py files if missing
echo "Ensuring __init__.py files exist..."
find src/mysingle/protos -type d -exec touch {}/__init__.py \;

echo "✅ Proto generation complete!"
echo ""
echo "Generated files:"
find src/mysingle/protos -name "*_pb2.py" | wc -l | xargs echo "  - Python modules:"
find src/mysingle/protos -name "*_pb2_grpc.py" | wc -l | xargs echo "  - gRPC stubs:"
