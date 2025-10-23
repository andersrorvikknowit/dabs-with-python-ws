# DABS-with-python - Workshop
This workshop is a walkthrough of how [databricks asset bundles works in python](https://docs.databricks.com/aws/en/dev-tools/bundles/python/#gsc.tab=0). You will go through a set of exercises.

## Prerequisites

* You need to have databricks-cli installed. It must be version 0.248.0 or above to be able to use python for asset bundles.
* Make is required. It runs on Linux, MacOS and Windows
  * Make is a way to "reuse commands". More about this later in the workshop, but get the tool installed :)
* You can use whatever editor / IDE you want. I use Pycharm, many people prefer VSCode which is also great.
* Finally, you will need the [uv package manager](https://github.com/astral-sh/uv) for python.

## Exercise 1

Navigate to the repository folder in your terminal of choice.

Ensure you have a newer version of databricks-cli than 0.248.0 as mentioned above.
```shell
databricks --version
```

Login to the [databricks workspace](https://dbc-639f4875-165d.cloud.databricks.com/) we will be using.
When prompted, enter a name for the authentication profile. Remember this name. You
will also be able to find it in your ~/.databrickscfg file.

```shell
databricks auth login https://dbc-639f4875-165d.cloud.databricks.com/
```

Next, we will generate a new asset bundle, but with python rather than yaml.

```shell
databricks bundle init experimental-jobs-as-code
```

* When prompted, enter the name of the bundle / your project.
* Say YES to "include a stub (sample) notebook"
* Say YES to "include a stub (sample) Delta Live Tables pipeline"
* Say NO to "include a stub (sample) Python package"

Navigate to the folder of the bundle you just created.

## Exercise 2

Observe the structures that databricks bundle init has created for you.

What do you think is good?
What do you think is bad?
What happens if you create another bundle?

## Exercise 3
Bundles are not really useful without a deployment, so let us deploy the bundle.

The bundle requires packages, so we need to install them. Go ahead and do so with uv.
Ensure that you are in the folder where databricks.yml is located.
```shell
uv sync
```

Then we can deploy the bundle with the databricks-cli
```shell
databricks bundle deploy --target dev -p <your_profile_name>
```

You will get an error like:

```shell
databricks bundle deploy --target dev -p knowit_python_ws
Building default...
Uploading dist/jobs_as_code_project-0.0.1+20251022.201815-py3-none-any.whl...
Uploading bundle files to /Workspace/Users/anders.rorvik@knowit.no/.bundle/jobs_as_code_project/dev/files...
Deploying resources...
Error: terraform apply: exit status 1

Error: cannot create pipeline: Catalog 'default_catalog' does not exist.

  with databricks_pipeline.jobs_as_code_project_pipeline,
  on bundle.tf.json line 89, in resource.databricks_pipeline.jobs_as_code_project_pipeline:
  89:       }
```

This is because that catalog does not exist. We will use the catalog "knowit_dabs_python_ws" which has been created already, instead.
Find the relevant file, and update the catalog name variable.

<details>
  <summary>Show hint</summary>
Have a look at the file jobs_as_code_project_pipeline.py
</details>


## Exercise 4
Observe where the bundle has been deployed in [your workspace](https://dbc-639f4875-165d.cloud.databricks.com/browse)

## Exercise 5

So now we have used the default bundle setup. I think we can do better, and we need more python too!

Here are some things we could do:
* We do not want a .venv / pyproject.toml for each bundle
* We do not want to repeat targets / environments in each bundle
* The job and pipeline were created with JSON definitions, but it can actually be done with python instead! See the files called "jobs_as_code_project_job.py" and "jobs_as_code_project_pipeline.py" for examples of json definitions.
* And we still have YAML? Unfortunately, we cannot get rid of it all, but we can get rid of most of it.

So what can we do? We can reuse definitions and share them across bundles, but first we will "pythonify" our deployments.

In case you used the default template:

* Edit the file called jobs_as_code_project_job.py

We will now convert it from JSON to Python. See a sample below. Note that implementations on Azure and GCP will have different attributes.
Waiting for the job cluster and the job to complete is going to take about 11 minutes. Please use the serverless version below, unless you need a coffee break :)

```python

from databricks.bundles.jobs import (
    AutoScale,
    ClusterSpec,
    CronSchedule,
    DataSecurityMode,
    JobCluster,
    Job,
    PerformanceTarget,
    Task,
    NotebookTask,
    AwsAttributes,
    EbsVolumeType,
)

job = Job(
    name="jobs_as_code_project_job",
    performance_target=PerformanceTarget.PERFORMANCE_OPTIMIZED,
    schedule=CronSchedule(
        quartz_cron_expression="0 0 8 ? * * *",
        timezone_id="UTC",  # Every day at 8 clock in the morning.
    ),
    job_clusters=[
        JobCluster(
            job_cluster_key="my_awesome_job_cluster",
            new_cluster=ClusterSpec(
                spark_version="15.4.x-scala2.12",
                node_type_id="m5a.large",
                data_security_mode=DataSecurityMode.USER_ISOLATION,
                autoscale=AutoScale(min_workers=1, max_workers=4),
                aws_attributes=AwsAttributes(
                    ebs_volume_count=1,
                    ebs_volume_size=32,
                    ebs_volume_type=EbsVolumeType.GENERAL_PURPOSE_SSD,
                ),
            ),
        )
    ],
    tasks=[
        Task(
            task_key="notebook_task",
            notebook_task=NotebookTask(notebook_path="src/notebook.ipynb"),
            job_cluster_key="my_awesome_job_cluster",
        )
    ],
)

```

```python
from databricks.bundles.jobs import (
    CronSchedule,
    Job,
    PerformanceTarget,
    Task,
    NotebookTask,
)

job = Job(
    name="jobs_as_code_project_job",
    performance_target=PerformanceTarget.PERFORMANCE_OPTIMIZED,
    schedule=CronSchedule(
        quartz_cron_expression="0 0 8 ? * * *",
        timezone_id="UTC",  # Every day at 8 clock in the morning.
    ),
    tasks=[
        Task(
            task_key="notebook_task",
            notebook_task=NotebookTask(notebook_path="src/notebook.ipynb"),
        )
    ],
)

```

Run the deploy with the databricks CLI

```shell
databricks bundle deploy --target dev -p <your_profile_name>
```

Time to change the Pipeline / Delta Live Table / Spark Declarative Pipeline into python code as well. A loved child has many names
* Edit the file jobs_as_code_project_pipeline.py

```python

from databricks.bundles.pipelines import NotebookLibrary, Pipeline, PipelineLibrary

jobs_as_code_project_pipeline = Pipeline(
    name="jobs_as_code_project_pipeline",
    catalog="knowit_dabs_python_ws",
    schema="knowit_dabs_python_ws_${bundle.target}",
    libraries=[
        PipelineLibrary(
            notebook=NotebookLibrary(path="src/dlt_pipeline.ipynb"),
        )
    ],
    configuration={
        "bundle.sourcePath": "${workspace.file_path}/src",
    },
)

```

Deploy this as well with the databricks bundle deploy command.
Notice that you are using the same catalog, schema, as other users. This is not going to work in real scenario.
We will fix this later on in the workshop, if your pipeline fails, it is not an issue.

## Exercise 6
In order to save time, we will fast track to a more elegant and efficient solution to working with several bundles, where multiple users can collaborate on bundle deployment.


