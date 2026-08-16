"""Make plain `pytest` work from the collection dir (dev inner loop).

Adds to sys.path:
  1. this dir      -> so `import ansible_helpers` works
  2. the directory that CONTAINS `ansible_collections/`
                    -> so `import ansible_collections.workshop...` works
Found by walking up to the `ansible_collections` dir, so tree depth doesn't matter.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_d = HERE
while _d != os.path.dirname(_d):
    if os.path.basename(_d) == "ansible_collections":
        sys.path.insert(0, os.path.dirname(_d))
        break
    _d = os.path.dirname(_d)
