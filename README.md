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

it would run folling command to build jupyter image resource
$ export SERVICE=vertex-ai-mlops
$ export JUPYTER_DOCKERFILES_PATH=jupyter_dockerfiles
$ export JUPYTER_IMAGE=${SERVICE}-jupyter
$ docker build -f ./${JUPYTER_DOCKERFILES_PATH}/jupyter.Dockerfile . -t ${JUPYTER_IMAGE}
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
1. Authenticate your Google Cloud account, **If you are using Google Cloud Notebooks**, your environment is already authenticated. Skip this step.
1. TBD How to setup up google cloud account locally. 

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

## Reference
Orchestrating PyTorch ML Workflows on Vertex AI Pipelines: https://cloud.google.com/blog/topics/developers-practitioners/orchestrating-pytorch-ml-workflows-vertex-ai-pipelines

Build pipelines component custom container image:
* Container-Registry Managing images: https://cloud.google.com/container-registry/docs/managing
* kaniko-cache: https://cloud.google.com/build/docs/optimize-builds/kaniko-cache
* Artifact-Registry - configure-cloud-build: https://cloud.google.com/artifact-registry/docs/configure-cloud-build
* Container-Registry Pushing and pulling images: https://cloud.google.com/container-registry/docs/pushing-and-pulling
 
vertex-ai-samples:
* PyTorch on Google Cloud: Text Classification: https://github.com/GoogleCloudPlatform/vertex-ai-samples/tree/main/community-content/pytorch_text_classification_using_vertex_sdk_and_gcloud
* Training, Tuning and Deploying a PyTorch Text Classification Model on Vertex AI: https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/community-content/pytorch_text_classification_using_vertex_sdk_and_gcloud/pytorch-text-classification-vertex-ai-train-tune-deploy.ipynb
* Orchestrating ML workflow to Train and Deploy a PyTorch Text Classification Model on Vertex AI Pipelines: https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/community-content/pytorch_text_classification_using_vertex_sdk_and_gcloud/pytorch-text-classification-vertex-ai-pipelines.ipynb
* Google Cloud Vertex AI Community Content: https://github.com/GoogleCloudPlatform/vertex-ai-samples/tree/main/community-content

Notebooks using the Hugging Face libraries: https://github.com/huggingface/notebooks
* Multi-Label Classification on Unhealthy Comments - Finetuning RoBERTa with PyTorch - Coding Tutorial: https://www.youtube.com/watch?v=vNKIg8rXK6w
* Hugging Face Transformers: the basics. Practical coding guides SE1E1. NLP Models (BERT/RoBERTa): https://www.youtube.com/watch?v=DQc2Mi7BcuI
* Fine-tuning pretrained NLP models with Huggingface’s Trainer: https://towardsdatascience.com/fine-tuning-pretrained-nlp-models-with-huggingfaces-trainer-6326a4456e7b
* Tuning and Deploying HF Transformers with Vertex AI — Part 1 Preparing Prerequisites and Dataset: https://blog.devops.dev/tuning-and-deploying-hf-transformers-with-vertex-ai-part-1-preparing-prerequisites-and-dataset-9794ebe8e291
* Tuning and Deploying Huggingface Transformers with Vertex AI — Part 2 Training Code: https://blog.devops.dev/tuning-and-deploying-hf-transformers-with-vertex-ai-part-2-training-code-591186445a2a

Bert Model:
* microsoft/Multilingual-MiniLM-L12-H384: https://huggingface.co/microsoft/Multilingual-MiniLM-L12-H384
* Bert Document: 
    * https://huggingface.co/docs/transformers/model_doc/bart
    * TFBertForSequenceClassification: https://huggingface.co/docs/transformers/model_doc/bert#transformers.TFBertForSequenceClassification
* Transformers:
    * README_zh-hant: https://github.com/huggingface/transformers/blob/main/README_zh-hant.md  
    * Fine-tune a pretrained model: https://huggingface.co/docs/transformers/training
    * PyTorch Trainer: https://huggingface.co/docs/transformers/v4.23.1/en/main_classes/trainer#transformers.Trainer
* Datasets:
    * https://huggingface.co/docs/datasets/main/en/package_reference/main_classes  

Vertex AI SDK for Python
* python-aiplatform: https://github.com/googleapis/python-aiplatform/tree/bae03158c06865d1b61c06a1c8af64e876ce76dd
    * experiment_tracking: https://github.com/googleapis/python-aiplatform/tree/d438e58dd50491c7a535cde4f88230a7b41f1345/samples/model-builder/experiment_tracking  
    * pricing: https://cloud.google.com/vertex-ai/pricing#text-data
* Class ListArtifactsRequest: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform_v1.types.ListArtifactsRequest
* MetadataServiceClient: https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform_v1.services.metadata_service.MetadataServiceClient#google_cloud_aiplatform_v1_services_metadata_service_MetadataServiceClient_list_artifacts

Tensorflow:
* Modrl: https://www.tensorflow.org/api_docs/python/tf/keras/Model
* Classify text with BERT: https://www.tensorflow.org/text/tutorials/classify_text_with_bert

Component docker container:
* Prebuilt containers for custom training: https://cloud.google.com/vertex-ai/docs/training/pre-built-containers
* Configure compute resources for custom training: https://cloud.google.com/vertex-ai/docs/training/configure-compute
* GPU platforms: https://cloud.google.com/compute/docs/gpus/#a100-80gb

Vertex AI - Feature Store: 
* Sample: https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/feature_store/sdk-feature-store.ipynb
* Fetch feature values for model training: https://cloud.google.com/vertex-ai/docs/featurestore/serving-batch

Other:
* https://github.com/jupyter/docker-stacks
* artifacts training list: https://console.cloud.google.com/artifacts/docker/vertex-ai/us/training
