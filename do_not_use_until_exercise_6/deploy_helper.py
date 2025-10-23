"""Helper script to make deploy work seamless on all platforms."""

import shutil
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    _, bundle, env, profile, *flags = sys.argv
    bundle_path = Path("bundles") / bundle
    if not bundle_path.exists():
        msg = "Bundle does not exist!"
        raise RuntimeError(msg)

    # Databricks deployment will look for this folder to find existing deployment to
    # delete before pushing the new one. In order to ensure deployment from different
    # branches can be done in parallel (creating two jobs or pipelines), we need
    # to remove the local metadata.
    databricks_folder = bundle_path / ".databricks"
    if databricks_folder.exists():
        shutil.rmtree(databricks_folder)

    subprocess.run(  # noqa: S603
        ["databricks", "bundle", "deploy", "-t", env, "-p", profile, *flags],  # noqa: S607
        check=True,
        cwd=Path("bundles") / bundle,
    )

    subprocess.run(  # noqa: S603
        ["databricks", "bundle", "summary", "-t", env, "-p", profile],  # noqa: S607
        check=True,
        cwd=Path("bundles") / bundle,
    )
