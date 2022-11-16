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
    packages_to_install=["torch-model-archiver"],
    output_component_file="./pipelines/yaml/generate_mar_file.yaml",
)
def generate_mar_file(
    model_display_name: str,
    model_version: str,
    handler: str,
    model: Input[Model],
    model_mar: Output[Model],
) -> NamedTuple("Outputs", [("mar_env_var", list), ("mar_export_uri", str)]):
    """custom pipeline component to package model artifacts and custom
    handler to a model archive file using Torch Model Archiver tool
    """
    import logging
    import os
    import subprocess
    import time
    from collections import namedtuple
    from pathlib import Path

    logging.getLogger().setLevel(logging.INFO)

    # create directory to save model archive file
    logging.info(f"Model Path: {model.path}")
    model_output_root = model.path
    mar_output_root = model_mar.path
    export_path = f"{mar_output_root}/model-store"
    try:
        Path(export_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.warning(e)
        # retry after pause
        time.sleep(2)
        Path(export_path).mkdir(parents=True, exist_ok=True)

    # parse and configure paths for model archive config
    handler_path = (
        handler.replace("gs://", "/gcs/") + "predictor/custom_handler.py"
        if handler.startswith("gs://")
        else handler
    )
    model_artifacts_dir = f"{model_output_root}/model/{model_display_name}"
    extra_files = [
        os.path.join(model_artifacts_dir, f)
        for f in os.listdir(model_artifacts_dir)
        if f != "pytorch_model.bin"
    ]

    # define model archive config
    mar_config = {
        "MODEL_NAME": model_display_name,
        "HANDLER": handler_path,
        "SERIALIZED_FILE": f"{model_artifacts_dir}/pytorch_model.bin",
        "VERSION": model_version,
        "EXTRA_FILES": ",".join(extra_files),
        "EXPORT_PATH": f"{model_mar.path}/model-store",
    }

    # generate model archive command
    archiver_cmd = (
        "torch-model-archiver --force "
        f"--model-name {mar_config['MODEL_NAME']} "
        f"--serialized-file {mar_config['SERIALIZED_FILE']} "
        f"--handler {mar_config['HANDLER']} "
        f"--version {mar_config['VERSION']}"
    )
    if "EXPORT_PATH" in mar_config:
        archiver_cmd += f" --export-path {mar_config['EXPORT_PATH']}"
    if "EXTRA_FILES" in mar_config:
        archiver_cmd += f" --extra-files {mar_config['EXTRA_FILES']}"
    if "REQUIREMENTS_FILE" in mar_config:
        archiver_cmd += f" --requirements-file {mar_config['REQUIREMENTS_FILE']}"

    # run archiver command
    logging.warning("Running archiver command: %s", archiver_cmd)
    with subprocess.Popen(
        archiver_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as p:
        _, err = p.communicate()
        if err:
            raise ValueError(err)

    # set output variables
    mar_env_var = [{"name": "MODEL_NAME", "value": model_display_name}]
    mar_export_uri = f"{model_mar.uri}/model-store/"

    outputs = namedtuple("Outputs", ["mar_env_var", "mar_export_uri"])
    return outputs(mar_env_var, mar_export_uri)
