# DABS-with-python - Workshop
This workshop is a walkthrough of how [databricks asset bundles works in python](https://docs.databricks.com/aws/en/dev-tools/bundles/python/#gsc.tab=0). You will go through a set of exercises.

## Prerequisites

* You need to have databricks-cli installed. It must be version 0.248.0 or above to be able to use python for asset bundles.
* Make is required. It runs on Linux, macOS and Windows
  * Make is a way to "reuse commands". More about this later in the workshop, but get the tool installed :)
* You can use whatever editor / IDE you want. I use Pycharm, many people prefer VSCode which is also great.
* Finally, you will need the [uv package manager](https://github.com/astral-sh/uv) for python.

In case you use brew for macOS:

```shell
brew install databricks/tap/databricks make uv
```

For windows, in case you use 
```shell
choco install databricks-cli make uv
```

For Linux, use your distro's package manager.


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
        timezone_id="UTC",  # Every day at 8 o'clock in the morning.
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
        timezone_id="UTC",  # Every day at 8 o'clock in the morning.
    ),
    tasks=[
        Task(
            task_key="notebook_task",
            notebook_task=NotebookTask(notebook_path="src/notebook.ipynb"),
        )
    ],
)

```

Run the deployment with the databricks CLI

```shell
databricks bundle deploy --target dev -p <your_profile_name>
```

Time to change the Pipeline / Delta Live Table / Spark Declarative Pipeline into python code as well. A beloved child has many names
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
In order to save time, we will fast track to a more elegant and efficient solution to working with several bundles, where multiple users can collaborate on code within a single bundle.

Go to the folder [do_not_use_until_exercise_6](do_not_use_until_exercise_6).

We need to get our packages for everything to work:

```shell
uv sync
```

## Exercise 7

Observe - what is different with the bundles, compared to the "out of the box experience" you get when running the default databricks bundle ?
* What is the purpose of the Makefile ? [Makefile](do_not_use_until_exercise_6/Makefile)
* What is the purpose of the mutators? [Mutators](do_not_use_until_exercise_6/bundles/mutators)

## Exercise 8

Update the [targets.yml file](do_not_use_until_exercise_6/bundles/targets.yml) . Replace my username with yours. Normally we would use service principal accounts for deploys, but it is cumbersome in a workshop setting.

## Exercise 9

Create a branch. Call it whatever you want, e.g. feat/working_with_bundles

## Exercise 10

Retyping the same commands all the time is tedious, and error-prone. We use Makefile targets to help us.
Try doing a deployment of bundle1 with the following command. make is the program that invokes targets in a Makefile.

```shell
make deploy BUNDLE=bundle1 PROFILE=<your_profile_name>
```

If everything was done correctly, you should have a working deploy.
Run the pipeline in the databricks GUI. Note that the name of the pipeline is unique for your user, also note the name of the schema is based on your branch name, which lets you work in isolation, but still access other important data in your workspace.

## Exercise 11

Have a look at [bundle2](do_not_use_until_exercise_6/bundles/bundle2) Compare it to the bundle you made in Exercise 1. 
What are your thoughts? In my opinion It has less "cruft", less yaml, and our mutators can be reused across bundles, and we only have a single project file, a single .venv, and so on. 
You can work with the bundles locally, in your own IDE or make use of databricks-connect to work with the bundles. Another option is to use a dev container with spark support.

## Summary and final thoughts

In this set of exercises we went through setting up a "vanilla" databricks asset bundle, with python support
We observe how it works, tested it, and then gradually refined the approach.

I hope you found the workshop useful, thanks so much for coming! The team I work for use this approach on a day-to-day basis,
and it is the best approach we have found for working with Databricks so far.

I plan on doing another workshop where we can use DABS with python as a basis, and then implement a full CI/CD pipeline for Databricks, using GitHub Actions.
