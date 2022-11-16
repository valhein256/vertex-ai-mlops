FROM tensorflow/tensorflow:latest-jupyter AS build

WORKDIR /opt/lib

ADD ./requirements.txt /opt/lib

RUN pip install -r requirements.txt
