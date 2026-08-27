"""`sidecar` task collection."""

from invoke import Collection

from .toolkit import namespace as toolkit_namespace

namespace = Collection(auto_dash_names=False)
namespace.add_collection(toolkit_namespace, name="toolkit")
