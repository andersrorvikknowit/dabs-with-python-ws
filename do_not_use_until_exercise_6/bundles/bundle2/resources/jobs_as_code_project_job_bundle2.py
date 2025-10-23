from databricks.bundles.jobs import (
    CronSchedule,
    Job,
    PerformanceTarget,
    Task,
    NotebookTask
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
        )
    ]
)