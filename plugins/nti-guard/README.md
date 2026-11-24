# NTI Guard

Verify a Neutral Trust Infrastructure (NTI) delegation attestation before a task runs, and record post-quantum signed receipts for every tool action.

## Features

- **Fail-Closed Security:** Blocks tasks if the attestation is missing, tampered with, or expired.
- **Post-Quantum:** Uses ML-DSA-87 (FIPS 204) for signatures and RFC 6962 for Merkle tree hashing.
- **Dependency-Free Hook:** The bash gate runs without needing Python installed, making it safe for any CI/CD environment.
- **Runtime Enforcement:** The Python guardrail intercepts bash commands, file edits, and MCP calls to generate cryptographic receipts.

## Installation

Since the runtime package is not yet on PyPI, install it directly from the repository:

```bash
pip install "openhands-nti[openhands] @ git+https://github.com/abisheakp197/Openhands---nti"
