from databricks.bundles.pipelines import NotebookLibrary, Pipeline, PipelineLibrary

jobs_as_code_project_pipeline = Pipeline(
    name="jobs_as_code_project_pipeline_new_bundle",
    target="jobs_as_code_project_${bundle.target}",
    catalog="knowit_dabs_python_ws",

    libraries=[
        PipelineLibrary(
            notebook=NotebookLibrary(path="src/dlt_pipeline.ipynb"),
        )
    ],
    configuration={
        "bundle.sourcePath": "${workspace.file_path}/src",
    },
)
