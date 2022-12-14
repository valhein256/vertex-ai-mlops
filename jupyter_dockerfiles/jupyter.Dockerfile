FROM jupyter/datascience-notebook:latest AS build

USER root

RUN apt-get update && \
    apt-get install -y \
    apt-transport-https \
    ca-certificates \
    gnupg

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

RUN apt-get update && \
    apt-get install google-cloud-cli

RUN pip -q install --upgrade kfp
RUN pip -q install --upgrade google-cloud-pipeline-components
RUN pip -q install --upgrade google-cloud-aiplatform
