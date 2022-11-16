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
    packages_to_install=["google-cloud-build"],
    output_component_file="./pipelines/yaml/build_custom_serving_image.yaml",
)
def build_custom_serving_image(
    project: str, gs_serving_dependencies_path: str, serving_image_uri: str
) -> NamedTuple("Outputs", [("serving_image_uri", str)],):
    """custom pipeline component to build custom serving image using
    Cloud Build and dependencies defined in the Dockerfile
    """
    import logging
    import os

    from google.cloud.devtools import cloudbuild_v1 as cloudbuild
    from google.protobuf.duration_pb2 import Duration

    logging.getLogger().setLevel(logging.INFO)
    build_client = cloudbuild.services.cloud_build.CloudBuildClient()

    logging.info(f"gs_serving_dependencies_path: {gs_serving_dependencies_path}")
    gs_dockerfile_path = os.path.join(gs_serving_dependencies_path, "Dockerfile")

    logging.info(f"serving_image_uri: {serving_image_uri}")
    build = cloudbuild.Build()
    build.steps = [
        {
            "name": "gcr.io/cloud-builders/gsutil",
            "args": ["cp", gs_dockerfile_path, "Dockerfile"],
        },
        # enabling Kaniko cache in a Docker build that caches intermediate
        # layers and pushes image automatically to Container Registry
        # https://cloud.google.com/build/docs/kaniko-cache
        {
            "name": "gcr.io/kaniko-project/executor:latest",
            "args": [f"--destination={serving_image_uri}", "--cache=true"],
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
    return (serving_image_uri,)
