"""`devkit` collection — the in-repo face of :mod:`modules.devkit`.

``devkit.download`` / ``devkit.upload`` / ``devkit.sync`` / ``devkit.check`` operate on the repo
they are run from. The console script ``devkit`` (see ``modules/devkit/cli.py``) is the
dependency-free equivalent for repos that only ``uvx`` the toolkit.
"""

from invoke import Collection

from .main import check, download, sync, upload

namespace = Collection(auto_dash_names=False)
namespace.add_task(check, name="check")
namespace.add_task(download, name="download")
namespace.add_task(sync, name="sync")
namespace.add_task(upload, name="upload")
