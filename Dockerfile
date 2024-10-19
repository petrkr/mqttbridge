FROM python:3.12-alpine

WORKDIR /app
COPY bridge.py /app/
COPY requirements.txt /app/

RUN pip install -r requirements.txt && \
    mkdir config


CMD "python" "bridge.py"
