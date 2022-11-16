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


@component(
    base_image="python:3.9",
    packages_to_install=[
        "google-cloud-pipeline-components",
        "google-cloud-aiplatform",
        "pandas",
        "fsspec",
    ],
    output_component_file="./pipelines/yaml/get_training_job_details.yaml",
)
def get_training_job_details(
    project: str,
    location: str,
    job_resource: str,
    eval_metric_key: str,
    model_display_name: str,
    metrics: Output[Metrics],
    model: Output[Model],
) -> NamedTuple(
    "Outputs", [("eval_metric", float), ("eval_loss", float), ("model_artifacts", str)]
):
    """custom pipeline component to get model artifacts and performance
    metrics from custom training job
    """
    import logging
    import shutil
    from collections import namedtuple

    import pandas as pd
    from google.cloud.aiplatform import gapic as aip
    from google.protobuf.json_format import Parse
    from google_cloud_pipeline_components.proto.gcp_resources_pb2 import \
        GcpResources

    # parse training job resource
    logging.info(f"Custom job resource = {job_resource}")
    training_gcp_resources = Parse(job_resource, GcpResources())
    custom_job_id = training_gcp_resources.resources[0].resource_uri
    custom_job_name = "/".join(custom_job_id.split("/")[-6:])
    logging.info(f"Custom job name parsed = {custom_job_name}")

    # get custom job information
    API_ENDPOINT = "{}-aiplatform.googleapis.com".format(location)
    client_options = {"api_endpoint": API_ENDPOINT}
    job_client = aip.JobServiceClient(client_options=client_options)
    job_resource = job_client.get_custom_job(name=custom_job_name)
    job_base_dir = job_resource.job_spec.base_output_directory.output_uri_prefix
    logging.info(f"Custom job base output directory = {job_base_dir}")

    # copy model artifacts
    logging.info(f"Copying model artifacts to {model.path}")
    destination = shutil.copytree(job_base_dir.replace("gs://", "/gcs/"), model.path)
    logging.info(destination)
    logging.info(f"Model artifacts located at {model.uri}/model/{model_display_name}")
    logging.info(f"Model artifacts located at model.uri = {model.uri}")

    # set model metadata
    start, end = job_resource.start_time, job_resource.end_time
    model.metadata["model_name"] = model_display_name
    model.metadata["framework"] = "pytorch"
    model.metadata["job_name"] = custom_job_name
    model.metadata["time_to_train_in_seconds"] = (end - start).total_seconds()

    # fetch metrics from the training job run
    metrics_uri = f"{model.path}/model/{model_display_name}/all_results.json"
    logging.info(f"Reading and logging metrics from {metrics_uri}")
    metrics_df = pd.read_json(metrics_uri, typ="series")
    for k, v in metrics_df.items():
        logging.info(f"     {k} -> {v}")
        metrics.log_metric(k, v)

    # capture eval metric and log to model metadata
    eval_metric = (
        metrics_df[eval_metric_key] if eval_metric_key in metrics_df.keys() else None
    )
    eval_loss = metrics_df["eval_loss"] if "eval_loss" in metrics_df.keys() else None
    logging.info(f"     {eval_metric_key} -> {eval_metric}")
    logging.info(f'     "eval_loss" -> {eval_loss}')

    model.metadata[eval_metric_key] = eval_metric
    model.metadata["eval_loss"] = eval_loss

    # return output parameters
    outputs = namedtuple("Outputs", ["eval_metric", "eval_loss", "model_artifacts"])

    return outputs(eval_metric, eval_loss, job_base_dir)
