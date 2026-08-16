"""Make plain `pytest` work from the collection dir (dev inner loop).

ansible-test sets up sys.path itself; this just helps when you run pytest
directly. It adds two things to sys.path:
  1. this dir      -> so `import ansible_helpers` works
  2. the directory that CONTAINS `ansible_collections/`
                    -> so `import ansible_collections.workshop...` works
We find (2) by walking up until we hit the `ansible_collections` dir, so the
depth of the tree doesn't matter.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_d = HERE
while _d != os.path.dirname(_d):  # stop at filesystem root
    if os.path.basename(_d) == "ansible_collections":
        sys.path.insert(0, os.path.dirname(_d))
        break
    _d = os.path.dirname(_d)
