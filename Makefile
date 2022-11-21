SERVICE := vertex-ai-mlops
PROJECT_ID := trend-micro-check-beta
MLOPS_BUCKET_NAME = gs://mlops-builds
REGION := us-central1
APP_NAME := ${SERVICE}
PYTORCH_JUPYTER_IMAGE := ${SERVICE}-pytorch-jupyter

##@ Helpers

.PHONY: help

help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST) && echo

##@ DATASETS PRETRAINED
EN_DATASET_FILE := 2021-01-27_Dataset_ver_1_downsampling_en.parquet
JA_DATASET_FILE := 2021-01-27_Dataset_ver_1_downsampling_ja.parquet
GCS_DATASET := gs://tmc-stg-anti-scam-nlp-labeled-clean-data/fbi-sms-mlops/datasets/2021-01-27
GCS_EN_DATASET_FILE := $(GCS_DATASET)/$(EN_DATASET_FILE)
GCS_JA_DATASET_FILE := $(GCS_DATASET)/$(JA_DATASET_FILE)
DATASET_PATH := ./datasets
EN_DATASET_FILE_PATH := $(DATASET_PATH)/$(EN_DATASET_FILE)
JA_DATASET_FILE_PATH := $(DATASET_PATH)/$(JA_DATASET_FILE)

PRETRAINED_MODEL := Multilingual-MiniLM-L12-H384 
GCS_PRETRAINED := gs://tmc-stg-anti-scam-nlp-labeled-clean-data/fbi-sms-mlops/pretrained
GCS_PRETRAINED_MODEL_PATH := $(GCS_PRETRAINED)/$(PRETRAINED_MODEL)
PRETRAINED_PATH := ./pretrained
PRETRAINED_MODEL_PATH := $(PRETRAINED_PATH)/$(PRETRAINED_MODEL)

.PHONY: dataset-downloading dataset-uploading pretrained-downloading pretrained-uploading

dataset-downloading: ## Download Labeled Clean Dataset
	@gsutil cp $(GCS_EN_DATASET_FILE) $(EN_DATASET_FILE_PATH)
	@gsutil cp $(GCS_JA_DATASET_FILE) $(JA_DATASET_FILE_PATH)


dataset-uploading: ## Upload Labeled Clean Dataset
	@gsutil cp $(EN_DATASET_FILE_PATH) $(GCS_EN_DATASET_FILE)
	@gsutil cp $(JA_DATASET_FILE_PATH) $(GCS_JA_DATASET_FILE)

pretrained-downloading: ## Download Labeled Clean Pretrained
	@rm -rf $(PRETRAINED_MODEL_PATH)
	@mkdir -p $(PRETRAINED_MODEL_PATH)
	@gsutil cp -r $(GCS_PRETRAINED_MODEL_PATH) $(PRETRAINED_MODEL_PATH)


pretrained-uploading: ## Upload Labeled Clean Pretrained
	@gsutil cp -r $(PRETRAINED_MODEL_PATH) $(GCS_PRETRAINED_MODEL_PATH)


##@ MLOPS PREPARING
MLOPS_BUCKET_NAME = gs://mlops-builds

.PHONY: mlops-pipelines-preparing

mlops-pipelines-preparing: ## mlops-pipelines-preparing
	@echo "Upload training Dockerfile"
	@gsutil cp ./trainer/pytorch-trainer.Dockerfile ${MLOPS_BUCKET_NAME}/${SERVICE}/train/Dockerfile
	@echo "Upload training application code"
	@gsutil cp -r ./trainer/src/ ${MLOPS_BUCKET_NAME}/${SERVICE}/train/
	@echo "Upload custom prediction handler"
	@gsutil cp ./predictor/custom_handler.py ./predictor/index_to_name.json ${MLOPS_BUCKET_NAME}/${SERVICE}/serve/predictor/
	@echo "Upload serving Dockerfile"
	@gsutil cp ./predictor/pytorch-serve.Dockerfile ${MLOPS_BUCKET_NAME}/${SERVICE}/serve/Dockerfile
	@echo "Check"
	@gsutil ls -al ${MLOPS_BUCKET_NAME}
	@echo "Done !!"

clean-preparing:
	@echo "Remove all resources of mlops-pipelines in ${MLOPS_BUCKET_NAME}"
	@gsutil rm -rf ${MLOPS_BUCKET_NAME}/${SERVICE}
	@echo "Check"
	@gsutil ls -al ${MLOPS_BUCKET_NAME}
	@echo "Done !!"


##@ Training
GCP_PROJECT_ID = ""
IMAGE_REPO_NAME = pytorch_gpu_train_fbi-sms-mlops
CUSTOM_TRAIN_IMAGE_URI = gcr.io/$(GCP_PROJECT_ID)/$(IMAGE_REPO_NAME)

.PHONY: build-pytorch-gpu-training pytorch-gpu-training

build-pytorch-gpu-training: ## Build pytorch-gpu-training
	@docker build -f ./trainer/pytorch-trainer.Dockerfile . -t ${CUSTOM_TRAIN_IMAGE_URI}

##@ JUPYTER
JUPYTER_DOCKERFILES_PATH = jupyter_dockerfiles
JUPYTER_IMAGE := ${SERVICE}-jupyter
TF_JUPYTER_IMAGE := ${SERVICE}-tf-jupyter

.PHONY: tf-jupyter tf-jupyter-bash

build-jupyter: ## Build Jupyter
	@docker build -f ./${JUPYTER_DOCKERFILES_PATH}/jupyter.Dockerfile . -t ${JUPYTER_IMAGE}

jupyter: ## Launch jupyter/datascience-notebook
	@docker run -it --rm \
		-v $(PWD):/home/jovyan/work/${SERVICE} \
		-v $(HOME)/.config/gcloud:/home/jovyan/.config/gcloud \
		-p 8888:8888 \
		${JUPYTER_IMAGE}

build-tf-jupyter: ## Build tf-jupyter
	@docker build -f ./Dockerfiles/tf-jupyter.Dockerfile . -t ${TF_JUPYTER_IMAGE}

tf-jupyter:  ## Launch tensorflow:latest-jupyter
	@docker run -it --rm \
		-v $(PWD)/notebooks:/tf/notebooks \
		-v $(PWD)/datasets:/tf/datasets \
		-v $(PWD)/pretrained:/tf/pretrained \
		-p 8888:8888 \
		${TF_JUPYTER_IMAGE}

tf-jupyter-bash: ## Run /bin/bash in tensorflow:latest-jupyter
	@docker run -it --rm \
		-v $(PWD)/notebooks:/tf/notebooks \
		-v $(PWD)/datasets:/tf/datasets \
		-v $(PWD)/pretrained:/tf/pretrained \
		${TF_JUPYTER_IMAGE} \
		/bin/bash

##@ DEPLOY

deploy: ## Deploy / Submit pipeline to vertex ai
	@docker run -it --rm \
		-v $(PWD):/home/jovyan/work/${SERVICE} \
		-v $(HOME)/.config/gcloud:/home/jovyan/.config/gcloud \
		-w /home/jovyan/work/${SERVICE} \
		-e PROJECT_ID=${PROJECT_ID} \
		-e BUCKET=${MLOPS_BUCKET_NAME} \
		-e REGION=${REGION} \
		-e APP_NAME=${SERVICE} \
		${JUPYTER_IMAGE} python3 ./pipelines/pipeline.py

clean-mlops-resources: ## Clean project resources on vertex ai
	@docker run -it --rm \
		-v $(PWD):/home/jovyan/work/${SERVICE} \
		-v $(HOME)/.config/gcloud:/home/jovyan/.config/gcloud \
		-w /home/jovyan/work/${SERVICE} \
		-e PROJECT_ID=${PROJECT_ID} \
		-e BUCKET=${MLOPS_BUCKET_NAME} \
		-e REGION=${REGION} \
		-e APP_NAME=${SERVICE} \
		${JUPYTER_IMAGE} python3 ./scripts/clean.py

##@ TEST IMAGE BUILDING
TRAINER_IMAGE = ${SERVICE}-trainer
SERVE_IMAGE = ${SERVICE}-serve 

.PHONY: build-trainer-image build-serve-image

build-trainer-image: ## build trainer image
	@docker build -f ./trainer/pytorch-trainer.Dockerfile . -t ${TRAINER_IMAGE}

build-serve-image:  ## build serve image
	@docker build -f ./predictor/pytorch-serve.Dockerfile . -t ${SERVE_IMAGE}
