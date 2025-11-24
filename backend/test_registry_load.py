import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from registry import NodeRegistry

print("Testing registry load...")
try:
    registry = NodeRegistry()
    print(f"Loaded {len(registry.nodes)} nodes.")
    for node in registry.nodes:
        print(f" - {node['id']}")

    # Check specifically for wm-pattern-filter
    ids = [n['id'] for n in registry.nodes]
    if "wm-pattern-filter" in ids:
        print("SUCCESS: wm-pattern-filter loaded.")
    else:
        print("FAILURE: wm-pattern-filter NOT loaded.")
        
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
