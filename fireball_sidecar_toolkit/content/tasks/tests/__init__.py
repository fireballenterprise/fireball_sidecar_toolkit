"""`tests` collection — one file per check (was a single flat `tasks/tests.py`), still registered
as one flat `tests.*` namespace (`tests.actionlint`, `tests.pytest`, etc.) so nothing that calls
these tasks needs to change. Re-exports each task function at package level too, so
`tasks/common/main.py`'s `test` task can keep calling `actionlint(context)` etc. exactly like it
did when this was one file.
"""

from invoke import Collection

from .actionlint import actionlint
from .pylint import pylint
from .pytest import run_pytest as pytest
from .rufflint import rufflint
from .yamllint import yamllint

namespace = Collection(auto_dash_names=False)
namespace.add_task(actionlint, name="actionlint")
namespace.add_task(pylint, name="pylint")
namespace.add_task(pytest, name="pytest")
namespace.add_task(rufflint, name="rufflint")
namespace.add_task(yamllint, name="yamllint")
