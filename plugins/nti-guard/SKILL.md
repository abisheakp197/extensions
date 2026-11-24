---
name: nti-guard
description: Enforce Neutral Trust Infrastructure (NTI) post-quantum attestation and receipt generation.
triggers:
  - /nti-guard
---

# NTI Guard

Neutral Trust Infrastructure (NTI) provides post-quantum runtime enforcement and cryptographic receipts for OpenHands. Under TAC review for LF Decentralized Trust Lab status, aligned with W3C APCG.

This plugin gates a task on a verified delegation attestation and records a signed receipt for each tool action.

## What it enforces

An NTI attestation is a JSON file that states what the task needs, and a delegation chain authorized by a root (RFC 6962) whose root is committed as `delegation_chain_root`.

The `hooks/pre-task.sh` gate refuses to start unless:

1. The declared `delegation_chain_root` matches the computed `delegation_chain`. A mismatch means the chain was tampered with.
2. Every capability in `required_capabilities` is granted to `agent_did`, and that record is valid.
3. The attestation itself is inside its validity window.

The hook is fail-closed: any verification failure blocks the task. It is dependency-free, so it works even if Python packages were never installed.

Wire the hook into whatever runs your task runner that supports a pre-task step can call it:

```bash
NTI_REQUIRED=1 bash plugins/nti-guard/hooks/pre-task.sh
