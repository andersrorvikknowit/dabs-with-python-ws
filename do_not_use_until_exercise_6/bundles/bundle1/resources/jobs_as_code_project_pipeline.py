from databricks.bundles.pipelines import NotebookLibrary, Pipeline, PipelineLibrary

jobs_as_code_project_pipeline = Pipeline(
    name="jobs_as_code_project_pipeline_new_bundle",
    schema="jobs_as_code_project",
    catalog="knowit_dabs_python_ws",
    serverless=True,

    libraries=[
        PipelineLibrary(
            notebook=NotebookLibrary(path="src/dlt_pipeline.ipynb"),
        )
    ],
    configuration={
        "bundle.sourcePath": "${workspace.file_path}/src",
    },
)
