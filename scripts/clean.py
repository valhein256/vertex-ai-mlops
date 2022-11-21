import os
from typing import NamedTuple

import google_cloud_pipeline_components
import kfp
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
from google.cloud.aiplatform import pipeline_jobs
from google.protobuf.json_format import MessageToDict
from google_cloud_pipeline_components import aiplatform as aip_components
from google_cloud_pipeline_components.experimental import custom_job
from kfp.v2 import compiler, dsl
from kfp.v2.dsl import Input, Metrics, Model, Output, component

from config import pipeline_config as cfg


# functions to create client
def create_job_client(client_options):
    client = aip.JobServiceClient(client_options=client_options)
    return client


def create_model_client(client_options):
    client = aip.ModelServiceClient(client_options=client_options)
    return client


def create_endpoint_client(client_options):
    client = aip.EndpointServiceClient(client_options=client_options)
    return client


def create_pipeline_client(client_options):
    client = aip.PipelineServiceClient(client_options=client_options)
    return client


def list_custom_jobs(client, app_name=None):
    # client = clients["job"]
    jobs = []
    response = client.list_custom_jobs(parent=PARENT)
    for row in response:
        _row = MessageToDict(row._pb)
        jobs.append((_row["name"], _row["displayName"]))
        if app_name and _row["displayName"].startswith(app_name):
            jobs.append((_row["name"], _row["displayName"]))
        else:
            jobs.append((_row["name"], _row["displayName"]))
    return jobs


def list_hp_tuning_jobs(client, app_name=None):
    # client = clients["job"]
    jobs = []
    response = client.list_hyperparameter_tuning_jobs(parent=PARENT)
    for row in response:
        _row = MessageToDict(row._pb)
        jobs.append((_row["name"], _row["displayName"]))
        if app_name and _row["displayName"].startswith(app_name):
            jobs.append((_row["name"], _row["displayName"]))
        else:
            jobs.append((_row["name"], _row["displayName"]))
    return jobs


def list_models(client, app_name=None):
    # client = clients["model"]
    models = []
    response = client.list_models(parent=PARENT)
    for row in response:
        _row = MessageToDict(row._pb)
        models.append((_row["name"], _row["displayName"]))
        if app_name and _row["displayName"].startswith(app_name):
            models.append((_row["name"], _row["displayName"]))
        else:
            models.append((_row["name"], _row["displayName"]))
    return models


def list_endpoints(client, app_name=None):
    # client = clients["endpoint"]
    endpoints = []
    response = client.list_endpoints(parent=PARENT)
    for row in response:
        _row = MessageToDict(row._pb)
        endpoints.append((_row["name"], _row["displayName"]))
        if app_name and _row["displayName"].startswith(app_name):
            endpoints.append((_row["name"], _row["displayName"]))
        else:
            endpoints.append((_row["name"], _row["displayName"]))
    return endpoints


def list_pipelines(client, pipeline_name=None):
    # client = clients["pipeline"]
    pipelines = []
    if pipeline_name:
        request = aip.ListPipelineJobsRequest(
            parent=PARENT, filter=f'display_name="{pipeline_name}"', order_by="end_time"
        )
    else:
        request = aip.ListPipelineJobsRequest(
            parent=PARENT, order_by="end_time"
        )

    response = client.list_pipeline_jobs(request=request)

    for row in response:
        _row = MessageToDict(row._pb)
        pipelines.append(_row["name"])
    return pipelines


if __name__ == '__main__':
    PROJECT_ID = cfg.PROJECT_ID
    BUCKET_NAME = cfg.BUCKET
    REGION = cfg.REGION
    APP_NAME = cfg.APP_NAME
    PIPELINE_NAME = cfg.PIPELINE_NAME
    # API Endpoint
    API_ENDPOINT = "{}-aiplatform.googleapis.com".format(REGION)

    # Vertex AI location root path for your dataset, model and endpoint resources
    PARENT = f"projects/{PROJECT_ID}/locations/{REGION}"

    client_options = {"api_endpoint": API_ENDPOINT}

    # Initialize Vertex SDK
    aiplatform.init(project=PROJECT_ID, staging_bucket=BUCKET_NAME)

    # clients = {}
    # clients["job"] = create_job_client(client_options)
    # clients["model"] = create_model_client(client_options)
    # clients["endpoint"] = create_endpoint_client(client_options)
    # clients["pipeline"] = create_pipeline_client(client_options)


    delete_custom_job = True
    print("Delete the custom training using the Vertex AI fully qualified identifier for the custom training")
    try:
        if delete_custom_job:
            client = create_job_client(client_options)
            custom_jobs = list_custom_jobs(client, app_name=APP_NAME)
            for job_id, job_name in custom_jobs:
                try:
                    print(f"Deleting job {job_id} [{job_name}]")
                    client.delete_custom_job(name=job_id)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)


    delete_hp_tuning_job = True
    print("Delete the hyperparameter tuning jobs using the Vertex AI fully qualified identifier for the hyperparameter tuning job")
    try:
        if delete_hp_tuning_job:
            client = create_job_client(client_options)
            hp_tuning_jobs = list_hp_tuning_jobs(client, app_name=APP_NAME)
            for job_id, job_name in hp_tuning_jobs:
                try:
                    print(f"Deleting job {job_id} [{job_name}]")
                    client.delete_hyperparameter_tuning_job(name=job_id)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)


    delete_endpoint = True
    print("Delete the endpoint using the Vertex AI fully qualified identifier for the endpoint")
    try:
        if delete_endpoint:
            client = create_endpoint_client(client_options)
            endpoints = list_endpoints(client, app_name=APP_NAME)
            for endpoint_id, endpoint_name in endpoints:
                try:
                    endpoint = aiplatform.Endpoint(endpoint_id)
                    # undeploy models from the endpoint
                    print(f"Undeploying all deployed models from the endpoint {endpoint_name}")
                    endpoint.undeploy_all(sync=True)
                    # deleting endpoint
                    print(f"Deleting endpoint {endpoint_id} [{endpoint_name}]")
                    client.delete_endpoint(name=endpoint_id)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)


    delete_model = True
    print("Delete the model using the Vertex AI fully qualified identifier for the model")
    try:
        if delete_model:
            client = create_model_client(client_options)
            models = list_models(client, app_name=APP_NAME)
            for model_id, model_name in models:
                print(f"Deleting model {model_id} [{model_name}]")
                client.delete_model(name=model_id)
    except Exception as e:
        print(e)

    delete_pipeline_job = True
    print("Delete the pipeline execution using the Vertex AI fully qualified identifier for the pipeline job")
    try:
        if delete_pipeline_job:
            pipeline_client = create_pipeline_client(client_options)
            pipelines = list_pipelines(pipeline_client, pipeline_name=PIPELINE_NAME)
            print(f"Start delete pipeline run {PIPELINE_NAME}")
            for pipeline_name in pipelines:
                print(f"Deleting pipeline run {pipeline_name}")
                if delete_custom_job:
                    print("\t Deleting underlying custom jobs")
                    pipeline_job = pipeline_client.get_pipeline_job(name=pipeline_name)
                    pipeline_job = MessageToDict(pipeline_job._pb)
                    task_details = pipeline_job["jobDetail"]["taskDetails"]
                    job_client = create_job_client(client_options)
                    for task in task_details:
                        if "containerDetail" in task["executorDetail"]:
                            custom_job_id = task["executorDetail"]["containerDetail"][
                                "mainJob"
                            ]
                            print(
                                f"\t Deleting custom job {custom_job_id} for task {task['taskName']}"
                            )
                            try:
                                job_client.delete_custom_job(name=custom_job_id)
                            except Exception as e:
                                print("delete_custom_job error:", e)
                pipeline_client.delete_pipeline_job(name=pipeline_name)
    except Exception as e:
        print(e)

    print("Delete the metadata artifact using the Vertex AI fully qualified identifier for the pipeline job")
    try:
        aiplatform.init(project=PROJECT_ID, staging_bucket=BUCKET_NAME, location=REGION)
        # combined_filters = f"{display_name_fitler} AND {create_date_filter}"
        metadata_artifacts = aiplatform.Artifact.list()
        for metadata in metadata_artifacts:
            artifact = aiplatform.Artifact.get(
                resource_id=metadata.name, project=PROJECT_ID, location=REGION
            )
            artifact.delete()
    except Exception as e:
        print(e)
    # delete_image = False
