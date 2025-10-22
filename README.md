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

This is because that catalog does not exist yet. We will use the catalog "knowit_dabs_python_ws" instead.
Find the relevant file, and update the catalog name.

<details>
  <summary>Show hint</summary>
Have a look at the file jobs_as_code_project_pipeline.py
</details>


## Exercise 4
Observe where the bundle has been deployed in [your workspace](https://dbc-639f4875-165d.cloud.databricks.com/browse)

## Exercise 5

So now we have used the default bundle setup. I think we can do better, and we need more python too!

Here are some things we could do:
* We do not want a pyproject.toml for each bundle
* We do not want to repeat targets / environments in each bundle
* The job and pipeline were created with JSON definitions, but it can actually be done with python instead! See the files called "jobs_as_code_project_job.py" and "jobs_as_code_project_pipeline.py" for examples of json definitions.
* And we still have YAML? Unfortunately, we cannot get rid of it all, but we can get rid of most of it.

So what can we do? We can reuse definitions and share them across bundles.

Navigate to the root of your repository.








