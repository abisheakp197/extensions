#!/usr/bin/env bash
# NTI Guard pre-task hook
#
# Verifies an NTI delegation attestation before a task runs.
# By default, if no attestation is found, it skips (exit 0).
# If NTI_REQUIRED=1 is set, a missing attestation is a hard failure (exit 2).
#
# Exit codes:
#   0 = verified (or skipped if missing and not required)
#   1 = attestation invalid (tampered, expired, etc.)
#   2 = attestation required but absent

set -euo pipefail

# Determine the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$(dirname "$(dirname "$PLUGIN_DIR")")")"

# Default attestation path (can be overridden by NTI_ATTESTATION)
ATTESTATION_PATH="${NTI_ATTESTATION:-"${REPO_ROOT}/.nti/attestation.json"}"

if [ ! -f "$ATTESTATION_PATH" ]; then
    if [ "${NTI_REQUIRED:-0}" = "1" ]; then
        echo "❌ NTI Guard: Attestation required but not found at $ATTESTATION_PATH" >&2
        exit 2
    else
        echo "⏭️ NTI Guard: No attestation found at $ATTESTATION_PATH. Skipping (set NTI_REQUIRED=1 to enforce)."
        exit 0
    fi
fi

echo "🛡️ NTI Guard: Verifying attestation at $ATTESTATION_PATH..."

# Run the Python verifier
# Use a subshell to trap the exit code without exiting the main script immediately
set +e
python3 "${PLUGIN_DIR}/scripts/verify_attestation.py" "$ATTESTATION_PATH"
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -ne 0 ]; then
    echo "❌ NTI Guard: Attestation verification failed with exit code $EXIT_CODE. Blocking task." >&2
    exit 1
fi

echo "✅ NTI Guard: Attestation verified. Proceeding with task."
exit 0
