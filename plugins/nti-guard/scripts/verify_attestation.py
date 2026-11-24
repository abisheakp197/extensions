#!/usr/bin/env python3
import sys
import json
import hashlib
from datetime import datetime, timezone

def die(msg, code=1):
    print(f"❌ NTI Guard Error: {msg}", file=sys.stderr)
    sys.exit(code)

def check_floats(data):
    if isinstance(data, dict):
        for k, v in data.items():
            check_floats(v)
    elif isinstance(data, list):
        for v in data:
            check_floats(v)
    elif isinstance(data, float):
        die("Attestation contains floats. Floats are rejected to prevent canonicalization mismatches.")

def canonicalize(data):
    return json.dumps(data, separators=(',', ':'), sort_keys=True, ensure_ascii=False).encode('utf-8')

def merkle_root(leaves):
    if not leaves:
        return b''
    nodes = [hashlib.sha256(b'\x00' + leaf).digest() for leaf in leaves]
    while len(nodes) > 1:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1]) # Odd-node promotion
        next_level = []
        for i in range(0, len(nodes), 2):
            next_level.append(hashlib.sha256(b'\x01' + nodes[i] + nodes[i+1]).digest())
        nodes = next_level
    return nodes[0]

def main():
    if len(sys.argv) < 2:
        die("Usage: verify_attestation.py <path_to_attestation.json>", code=2)
    
    path = sys.argv[1]
    try:
        with open(path, 'r') as f:
            att = json.load(f)
    except Exception as e:
        die(f"Failed to read or parse JSON: {e}")

    check_floats(att)

    # 1. Verify Merkle Root
    chain = att.get("delegation_chain", [])
    if not chain:
        die("Delegation chain is empty.")

    leaves = [canonicalize(record) for record in chain]
    computed_root = merkle_root(leaves).hex()
    declared_root = att.get("delegation_chain_root")
    
    if not declared_root or declared_root != computed_root:
        die(f"Root mismatch. Declared: {declared_root}, Computed: {computed_root}")

    # 2. Verify Validity Window
    now = datetime.now(timezone.utc)
    try:
        valid_from = datetime.fromisoformat(att["valid_from"].replace("Z", "+00:00"))
        valid_until = datetime.fromisoformat(att["valid_until"].replace("Z", "+00:00"))
    except Exception as e:
        die(f"Invalid date format: {e}")

    if now < valid_from:
        die(f"Attestation is not yet valid (valid from {valid_from}).")
    if now > valid_until:
        die(f"Attestation has expired (valid until {valid_until}).")

    # 3. Verify Capabilities
    req_caps = set(att.get("required_capabilities", []))
    agent_did = att.get("agent_did")
    granted_caps = set()

    for record in chain:
        if record.get("subject") == agent_did:
            rec_from = datetime.fromisoformat(record["valid_from"].replace("Z", "+00:00"))
            rec_until = datetime.fromisoformat(record["valid_until"].replace("Z", "+00:00"))
            if rec_from <= now <= rec_until:
                scope = record.get("scope", [])
                if isinstance(scope, str):
                    granted_caps.add(scope)
                else:
                    granted_caps.update(scope)

    missing = req_caps - granted_caps
    if missing:
        die(f"Agent {agent_did} is missing required capabilities: {missing}")

    print("✅ Attestation verified successfully.")
    print(f"   Agent: {agent_did}")
    print(f"   Root:  {computed_root}")
    sys.exit(0)

if __name__ == "__main__":
    main()
