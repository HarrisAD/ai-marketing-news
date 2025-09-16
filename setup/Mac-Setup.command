#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
chmod +x setup.sh start.sh start-backend.sh start-frontend.sh >/dev/null 2>&1
./setup.sh
