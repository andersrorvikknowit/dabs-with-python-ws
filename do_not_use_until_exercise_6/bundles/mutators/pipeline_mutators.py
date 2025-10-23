# type: ignore[reportAttributeAccessIssue] known issue due to type structure of databricks variable classes

from databricks.bundles.core import (
    Bundle,
    pipeline_mutator,
)
from databricks.bundles.pipelines import Pipeline

from .common_mutator_functions import Variables, clean_branch


@pipeline_mutator
def adjust_pipeline_for_dev(bundle: Bundle, pipeline: Pipeline) -> Pipeline:
    """If not in production mode, adjust schema and pipeline name."""
    if bundle.target == "prod":
        return pipeline

    clean_git_branch = clean_branch(bundle.resolve_variable(Variables.git_branch))

    def adjust_schema_name(pipeline: Pipeline) -> None:
        pipeline.name = f"{pipeline.name}_${{bundle.git.branch}}"
        pipeline.schema = f"{pipeline.schema}_{clean_git_branch}_${{bundle.target}}"

    adjust_schema_name(pipeline)
    return pipeline
