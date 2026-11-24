---
name: nti-guard
description: Verify an NTI delegation attestation before running a task.
---

# NTI Guard Command

This command triggers the NTI Guard verification process. It checks the delegation chain, validates the Merkle root, and ensures the agent has the required capabilities before allowing the task to proceed.

If the attestation is valid, the command outputs the agent's DID, the Merkle root, and grants permission to proceed. If invalid, the task is blocked.
