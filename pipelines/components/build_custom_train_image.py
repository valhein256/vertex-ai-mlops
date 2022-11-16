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
    base_image="gcr.io/google.com/cloudsdktool/cloud-sdk:latest",
    packages_to_install=["google-cloud-build"],
    output_component_file="./pipelines/yaml/build_custom_train_image.yaml",
)
def build_custom_train_image(
    project: str,
    gs_datasets_path: str,
    gs_train_src_path: str,
    training_image_uri: str
) -> NamedTuple("Outputs", [("training_image_uri", str)]):
    """custom pipeline component to build custom training image using
    Cloud Build and the training application code and dependencies
    defined in the Dockerfile
    """

    import logging
    import os

    from google.cloud.devtools import cloudbuild_v1 as cloudbuild
    from google.protobuf.duration_pb2 import Duration

    # initialize client for cloud build
    logging.getLogger().setLevel(logging.INFO)
    build_client = cloudbuild.services.cloud_build.CloudBuildClient()

    # parse step inputs to get path to Dockerfile and training application code
    gs_dockerfile_path = os.path.join(gs_train_src_path, "Dockerfile")
    gs_train_src_path = os.path.join(gs_train_src_path, "src/")

    logging.info(f"training_image_uri: {training_image_uri}")

    # define build steps to pull the training code and Dockerfile
    # and build/push the custom training container image
    build = cloudbuild.Build()
    build.steps = [
        {
            "name": "gcr.io/cloud-builders/gsutil",
            "args": ["cp", "-r", gs_train_src_path, "."],
        },
        {
            "name": "gcr.io/cloud-builders/gsutil",
            "args": ["cp", gs_dockerfile_path, "Dockerfile"],
        },
        # enabling Kaniko cache in a Docker build that caches intermediate
        # layers and pushes image automatically to Container Registry
        # https://cloud.google.com/build/docs/kaniko-cache
        {
            "name": "gcr.io/kaniko-project/executor:latest",
            "args": [f"--destination={training_image_uri}", "--cache=true"],
        },
    ]
    # override default timeout of 10min
    timeout = Duration()
    timeout.seconds = 7200
    build.timeout = timeout

    # create build
    operation = build_client.create_build(project_id=project, build=build)
    logging.info("IN PROGRESS:")
    logging.info(operation.metadata)

    # get build status
    result = operation.result()
    logging.info("RESULT:", result.status)

    # return step outputs
    return (training_image_uri,)
