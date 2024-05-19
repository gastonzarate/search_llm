FROM --platform=linux/amd64 python:3.12.3


WORKDIR /app
COPY . /app

RUN pip3 install -r /app/requirements.txt