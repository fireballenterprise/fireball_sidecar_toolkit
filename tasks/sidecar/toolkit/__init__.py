"""`sidecar.toolkit` collection — the in-repo face of :mod:`fireball_sidecar_toolkit`.

Re-exports the task collection shipped inside the wheel (:mod:`fireball_sidecar_toolkit.tasks`)
so there's one definition. `sidecar.toolkit.{update,apply,upgrade,sync,contribute,check,release,
mdfix}` operate on the repo they're run from; `download`/`upload` are deprecated aliases. The
console script `sidecar-toolkit` (see `fireball_sidecar_toolkit/cli.py`) is the dependency-free
equivalent.
"""

from fireball_sidecar_toolkit.tasks import collection as namespace

__all__ = ["namespace"]
