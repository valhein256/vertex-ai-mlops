# Use pytorch GPU base image
FROM us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-10:latest

# set working directory
WORKDIR /app

# Install required packages
RUN pip install google-cloud-storage transformers sentencepiece datasets tqdm cloudml-hypertune

# Copies the trainer code to the docker image.
COPY ./src/__init__.py /app/trainer/__init__.py
COPY ./src/experiment.py /app/trainer/experiment.py
COPY ./src/utils.py /app/trainer/utils.py
COPY ./src/metadata.py /app/trainer/metadata.py
COPY ./src/model.py /app/trainer/model.py
COPY ./src/task.py /app/trainer/task.py

# Set up the entry point to invoke the trainer.
ENTRYPOINT ["python", "-m", "trainer.task"]
