from databricks.bundles.jobs import (
    CronSchedule,
    Job,
    PerformanceTarget,
    Task,
    NotebookTask,
    PipelineTask
)

from databricks.bundles.pipelines import NotebookLibrary, Pipeline, PipelineLibrary
from databricks.sdk.service.jobs import TaskDependency

jobs_as_code_project_pipeline = Pipeline(
    name="jobs_as_code_project_pipeline_bundle2",
    schema="jobs_as_code_project_bundle2",
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


job = Job(
    name="jobs_as_code_project_job_bundle2",
    performance_target=PerformanceTarget.PERFORMANCE_OPTIMIZED,
    schedule=CronSchedule(
        quartz_cron_expression="0 0 8 ? * * *",
        timezone_id="UTC" # Every day at 8 clock in the morning.
    ),
    tasks=[
        Task(
            task_key="notebook_task",
            notebook_task=NotebookTask(
                notebook_path="src/notebook.ipynb"
            ),
        ),
    ]
)