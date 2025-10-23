# type: ignore[reportAttributeAccessIssue] known issue due to type structure of databricks variable classes
from dataclasses import replace

from databricks.bundles.core import (
    Bundle,
    job_mutator,
)
from databricks.bundles.jobs import (
    Job,
    JobEmailNotifications,
    JobParameterDefinition,
    PauseStatus,
    PerformanceTarget,
)

from .common_mutator_functions import Variables, clean_branch

@job_mutator
def adjust_job_for_dev(bundle: Bundle, job: Job) -> Job:  # noqa: C901
    if bundle.target == "prod":
        return job

    def adjust_job_name(job: Job) -> None:
        job.name = str(job.name) + "_${bundle.git.branch}"

    def adjust_perf_target(job: Job) -> None:
        job.performance_target = PerformanceTarget.PERFORMANCE_OPTIMIZED

    def adjust_parameters(job: Job) -> None:
        current_params = job.parameters
        if type(current_params) is list:
            if current_schema_param := next(
                (param for param in current_params if param.name == "schema"), None
            ):
                clean_git_branch = clean_branch(
                    bundle.resolve_variable(Variables.git_branch)
                )
                current_schema_param.default = f"{current_schema_param.default}_{clean_git_branch}_${{bundle.target}}"

            if current_job_name_param := next(
                (param for param in current_params if param.name == "job_name"), None
            ):
                current_job_name_param.default = job.name

    def adjust_triggers(job: Job):
        if job.trigger:
            job.trigger.pause_status = PauseStatus.PAUSED

    def adjust_schedules(job: Job) -> None:
        if job.schedule is not None:
            job.schedule.pause_status = PauseStatus.PAUSED

    adjust_job_name(job)
    adjust_perf_target(job)
    adjust_parameters(job)
    adjust_triggers(job)
    adjust_schedules(job)
    return job
