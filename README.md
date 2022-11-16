# MLOps: Pytorch ML on GCP Vertex AI
## Overview

This ML-project fine-tune and deploys a [pre-trained BERT model from HuggingFace Hub](https://huggingface.co/microsoft/Multilingual-MiniLM-L12-H384) for sentiment classification task. This notebook shows how to automate and monitor a PyTorch based ML workflow by orchestrating the pipeline in a serverless manner using [Vertex AI Pipelines](https://cloud.google.com/vertex-ai/docs/pipelines/introduction).
 
The project defines a pipeline using [Kubeflow Pipelines v2 (`kfp.v2`) SDK](https://www.kubeflow.org/docs/components/pipelines/sdk-v2/) and submits the pipeline to Vertex AI Pipelines services.

### Dataset

The project uses [IMDB movie review dataset](https://huggingface.co/datasets/imdb) from [Hugging Face Datasets](https://huggingface.co/datasets).

### Objective

How to **orchestrate PyTorch ML workflows on [Vertex AI](https://cloud.google.com/vertex-ai)** and emphasize first class support for training, deploying and orchestrating PyTorch workflows on Vertex AI. 

## Set up your local development environment

**If you are using Colab or Google Cloud Notebooks**, your environment already meets
all the requirements to run this project. You can skip this step.

**Otherwise**, just run following commands to make your development environment.
```
$ make build-jupyter
and launch jupyter
$ make jupyter
```

## Prepare your GCP Resource
### Set up your Google Cloud project

**The following steps are required, regardless of your environment.**

1. [Select or create a Google Cloud project](https://console.cloud.google.com/cloud-resource-manager).
1. [Make sure that billing is enabled for your project](https://cloud.google.com/billing/docs/how-to/modify-project).
1. Enable following APIs in your project required for running the tutorial
    - [Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)
    - [Cloud Storage API](https://console.cloud.google.com/flows/enableapi?apiid=storage.googleapis.com)
    - [Container Registry API](https://console.cloud.google.com/flows/enableapi?apiid=containerregistry.googleapis.com)
    - [Cloud Build API](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com)
1. If you are running this notebook locally, you will need to install the [Cloud SDK](https://cloud.google.com/sdk).
1. Enter your project ID in the cell below. Then run the cell to make sure the Cloud SDK uses the right project for all the commands in this project.
1. Authenticate your Google Cloud account, **If you are using Google Cloud Notebooks**, your environment is already authenticated. Skip this step.

### Create a Cloud Storage bucket

When you submit a training job using the Cloud SDK, you upload a Python package containing your training code to a Cloud Storage bucket. Vertex AI runs the code from this package. In this project, Vertex AI also saves the trained model that results from your job in the same bucket. Using this model artifact, you can then create Vertex AI model and endpoint resources in order to serve online predictions.

Set the name of your Cloud Storage bucket below. It must be unique across all Cloud Storage buckets.

You may also change the `REGION` variable, which is used for operations throughout the rest of this notebook. Make sure to [choose a region where Vertex AI services are available](https://cloud.google.com/vertex-ai/docs/general/locations#available_regions). You may not use a Multi-Regional Storage bucket for training with Vertex AI.
```
$ export BUCKET_NAME = "gs://mlops-builds"
$ export REGION = "us-central1" 
$ gsutil mb -l $REGION $BUCKET_NAME
```

## Upload ML packages and files to GCP Bucket
```
$ make mlops-pipelines-preparing MLOPS_BUCKET_NAME=${BUCKET_NAME}
```
## Deploy
```
make deploy
```
