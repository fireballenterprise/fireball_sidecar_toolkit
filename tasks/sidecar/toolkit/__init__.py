"""`sidecar.toolkit` collection — the in-repo face of :mod:`modules.sidecar.toolkit`.

``sidecar.toolkit.download`` / ``.upload`` / ``.sync`` / ``.check`` operate on the repo they are
run from. ``sidecar.toolkit.release`` promotes ``development`` -> ``main`` and cuts a tag. The
console script ``sidecar-toolkit`` (see ``modules/sidecar/toolkit/cli.py``) is the dependency-free
equivalent for repos that only ``uvx`` the toolkit.
"""

from invoke import Collection

from .main import check, download, release, sync, upload

namespace = Collection(auto_dash_names=False)
namespace.add_task(check, name="check")
namespace.add_task(download, name="download")
namespace.add_task(release, name="release")
namespace.add_task(sync, name="sync")
namespace.add_task(upload, name="upload")
