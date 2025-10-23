"""Entry point for bundle."""

import sys

# This is a bit nasty, but allows for sharing the mutators and other functions across bundles.
sys.path.append("../../")
from databricks.bundles.core import (
    Bundle,
    Resources,
    load_resources_from_current_package_module,
)

from bundles.mutators import *  # noqa: F403 - we export all mutators for reference from databricks.yml


def load_resources(_: Bundle) -> Resources:
    """Load all resources used in the bundle."""
    return load_resources_from_current_package_module()
