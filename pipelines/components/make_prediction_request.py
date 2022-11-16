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
    packages_to_install=["google-cloud-aiplatform", "google-cloud-pipeline-components"],
    output_component_file="./pipelines/yaml/make_prediction_request.yaml",
)
def make_prediction_request(project: str, bucket: str, endpoint: str, instances: list):
    """custom pipeline component to pass prediction requests to Vertex AI
    endpoint and get responses
    """
    import base64
    import logging

    from google.cloud import aiplatform
    from google.protobuf.json_format import Parse
    from google_cloud_pipeline_components.proto.gcp_resources_pb2 import \
        GcpResources

    logging.getLogger().setLevel(logging.INFO)
    aiplatform.init(project=project, staging_bucket=bucket)

    # parse endpoint resource
    logging.info(f"Endpoint = {endpoint}")
    gcp_resources = Parse(endpoint, GcpResources())
    endpoint_uri = gcp_resources.resources[0].resource_uri
    endpoint_id = "/".join(endpoint_uri.split("/")[-8:-2])
    logging.info(f"Endpoint ID = {endpoint_id}")

    # define endpoint client
    _endpoint = aiplatform.Endpoint(endpoint_id)

    # call prediction endpoint for each instance
    for instance in instances:
        if not isinstance(instance, (bytes, bytearray)):
            instance = instance.encode()
        logging.info(f"Input text: {instance.decode('utf-8')}")
        b64_encoded = base64.b64encode(instance)
        test_instance = [{"data": {"b64": f"{str(b64_encoded.decode('utf-8'))}"}}]
        response = _endpoint.predict(instances=test_instance)
        logging.info(f"Prediction response: {response.predictions}")
